# Build Plate — Face Display Parts

This folder now contains a **pre-arranged build plate** (`build_plate.stl`) ready to slice and print.

---

## What's on the plate

Three parts are laid out left-to-right with 5 mm spacing between them:

| Part     | Position | Dimensions (×)       | Print settings              |
|----------|----------|----------------------|-----------------------------|
| **Shell** | Left     | 54.4 × 74.4 × 26.2 mm | No supports, face-down      |
| **Lid**   | Center   | 54.4 × 74.4 × 8.0 mm  | No supports, flat-side down |
| **Mount** | Right    | 100.0 × 92.0 × 4.6 mm | No supports, flat-side down |

**Build plate footprint:** ~219 × 92 mm  
Fits on any 250×250 mm bed (e.g., Bambu A1, Prusa MK4, etc.).

---

## How to use

1. **Import `build_plate.stl`** into your slicer (Bambu Studio, PrusaSlicer, Cura, OrcaSlicer).
2. Each part is already in the correct orientation — **do not rotate**.
3. Slice with your standard filament settings (PLA or PETG recommended).
4. **No supports needed** for any part.

---

## Regenerating the layout

If you change tolerances or re-export individual STLs, regenerate the plate:

```bash
cd face_display/cad
python3 generate_build_plate.py
```

This re-reads `shell.stl`, `lid.stl`, and `mount.stl`, computes bounding boxes, and produces:
- `build_plate_layout.scad` — OpenSCAD preview file
- `build_plate.stl` — combined, slicer-ready STL

---

## Recommended print settings

- **Material:** PLA or PETG (PETG for mount bracket if you want more toughness)
- **Layer height:** 0.2 mm (quality) or 0.28 mm (speed)
- **Walls:** 3–4 perimeters
- **Infill:** 20–30 % (gyroid or grid)
- **Supports:** OFF
- **Brim:** Optional on mount bracket if bed adhesion is poor
