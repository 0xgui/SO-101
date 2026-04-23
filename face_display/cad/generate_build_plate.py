#!/usr/bin/env python3
"""
Face Display Build Plate Layout Generator

Reads the three STLs (shell, lid, mount), computes bounding boxes,
arranges them side-by-side on a virtual build plate, and outputs:
  1. build_plate_layout.scad  — OpenSCAD preview/arrangement file
  2. build_plate.stl        — rendered combined STL (slicer-ready)

Requires: OpenSCAD on PATH, Python 3 standard library.
"""
import struct
import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STL_FILES = ["shell.stl", "lid.stl", "mount.stl"]
SPACING = 5.0  # mm between parts

def parse_stl(path):
    """Parse an ASCII or binary STL and return (min/max) bounds."""
    with open(path, "rb") as f:
        data = f.read()

    if data.startswith(b"solid"):
        # Treat as ASCII (simple parser)
        lines = data.decode("ascii", errors="ignore").splitlines()
        verts = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 4 and parts[0] == "vertex":
                verts.append(tuple(float(p) for p in parts[1:4]))
        if verts:
            return bounds_from_verts(verts)
        # fall through to binary in case it has solid header but is binary

    # Binary STL
    num_tri = struct.unpack_from("<I", data, 80)[0]
    verts = []
    offset = 84
    for i in range(num_tri):
        # skip normal (12 bytes), read 3 vertices (36 bytes), skip attribute (2 bytes)
        for j in range(3):
            x, y, z = struct.unpack_from("<fff", data, offset + 12 + j * 12)
            verts.append((x, y, z))
        offset += 50
    return bounds_from_verts(verts)

def bounds_from_verts(verts):
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    return {
        "min": (min(xs), min(ys), min(zs)),
        "max": (max(xs), max(ys), max(zs)),
        "size": (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)),
    }

def main():
    infos = []
    for name in STL_FILES:
        path = os.path.join(SCRIPT_DIR, name)
        if not os.path.exists(path):
            print(f"ERROR: Missing {path}")
            sys.exit(1)
        b = parse_stl(path)
        infos.append((name, b))
        print(f"{name}: size {b['size'][0]:.2f} × {b['size'][1]:.2f} × {b['size'][2]:.2f} mm")

    # Arrange in a single row along +X, aligned to common Z=0 (bed) and Y=0 back edge
    scad_lines = [
        "// Auto-generated build plate layout for Face Display parts",
        "// Slicer-ready: import this STL or use the .scad for preview",
        "",
    ]
    x_cursor = 0.0
    max_y = 0.0
    for name, b in infos:
        w, d, h = b["size"]
        minx, miny, minz = b["min"]
        tx = x_cursor - minx
        ty = -miny  # align min_y to 0
        tz = -minz  # align min_z to 0 (sit flat on bed)
        scad_lines.append(f'// {name}: {w:.1f} x {d:.1f} x {h:.1f} mm')
        scad_lines.append(f'translate([{tx:.3f}, {ty:.3f}, {tz:.3f}])')
        scad_lines.append(f'    import("{name}");')
        scad_lines.append("")
        x_cursor += w + SPACING
        max_y = max(max_y, d)

    # Add a thin base plate so slicers see a common flat surface (optional but nice)
    plate_w = x_cursor - SPACING
    plate_d = max_y + 10.0
    scad_lines.append(f"// Optional thin build plate marker (0.1 mm, easy to remove)")
    scad_lines.append(f"// translate([-5, -5, -0.1]) cube([{plate_w+10:.1f}, {plate_d:.1f}, 0.1]);")
    scad_lines.append("")

    scad_path = os.path.join(SCRIPT_DIR, "build_plate_layout.scad")
    with open(scad_path, "w") as f:
        f.write("\n".join(scad_lines))
    print(f"Wrote {scad_path}")

    # Render combined STL via OpenSCAD
    out_stl = os.path.join(SCRIPT_DIR, "build_plate.stl")
    print(f"Rendering {out_stl} with OpenSCAD (this may take a minute)...")
    cmd = [
        "openscad",
        "-o", out_stl,
        scad_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("OpenSCAD stderr:", result.stderr)
        print("OpenSCAD stdout:", result.stdout)
        sys.exit(1)
    print(f"Success! {out_stl}")

if __name__ == "__main__":
    main()
