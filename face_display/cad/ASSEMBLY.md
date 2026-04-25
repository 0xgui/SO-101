# Face Display — Assembly Guide

---

## Parts overview

Three parts to print + hardware:

```
                    SHELL                          LID                   STRAP MOUNT
         (front view, bezel side)          (back view)                 (front view)

    ┌─────────────────────────┐      ┌─────────────────────────┐   ┌──────────────────────┐
    │  ┌───────────────────┐  │      │  ●               ●  │  │   │  ║              ║    │
    │  │   bezel window    │  │      │  │  (M3 boss cols)│  │  │   │  ║  strap slots ║    │
    │  │  (screen shows    │  │      │  │                │  │  │   │  ║              ║    │
    │  │   through here)   │  │      │  │                │  │  │   │    ○        ○        │
    │  └───────────────────┘  │      │  │                │  │  │   │                      │
    │                         │      │  ●               ●  │  │   │    ○        ○        │
    │  [USB-C slot on bottom] │      └─────────────────────────┘   │  ║              ║    │
    └─────────────────────────┘                                    └──────────────────────┘
                                           ↑ snap rails on inside       ↑ zip ties pass here
```

---

## Box dimensions

```
    Top view of shell (inside):
    ┌──────────────────────────────────┐
    │←──────── 54 mm outer ──────────→│
    │  ┌──────────────────────────┐   │
    │  │←────── 50 mm inner ────→│   │
    │  │   display PCB fits here  │   │
    │  └──────────────────────────┘   │
    └──────────────────────────────────┘

    Side cross-section (what's inside, front → back):

    FRONT                                              BACK
      │← 2mm →│← 1.6mm →│←── 10mm ──→│← 2mm →│← 1.6mm →│← 7.0mm →│← 2mm →│
      │  wall  │ display  │ wire slack  │standof│protoboard│  ESP32  │margin │
      │        │   PCB    │  (jumpers   │ledges │          │ chips   │       │
      │[window]│[screen→] │  loop here) │       │[ESP32-S3]│         │       │
      │        │          │             │       │          │         │       │
    ══╪════════╪══════════╪═════════════╪═══════╪══════════╪═════════╪═══════╪══
      z=0    z=2        z=3.6       z=13.6  z=15.6     z=17.2    z=24.2  z=26.2
                                                                      (BOX_D total ~26mm)
```

---

## Hardware list

| Item | Qty | Purpose |
|------|-----|---------|
| M3 heat-set inserts | 4 | Lid boss columns |
| M3×8 mm bolts | 4 | Lid → mount bracket |
| Long zip ties | 2 | Strap mount around the top arm / upper link |
| Jumper wires ~8 cm | 8 | Display PCB → protoboard |
| Soldering iron (220 °C) | 1 | Installing heat-set inserts |

---

## Step 1 — Install heat-set inserts

Use a soldering iron at ~220 °C. Press each insert flush or just below the surface.
Only the lid gets heat-set inserts. The mount bracket has clearance holes.

```
    LID (back face up):

    ┌─────────────────────────┐
    │  ╔══╗           ╔══╗   │
    │  ║██║  boss     ║██║   │
    │  ║██║  columns  ║██║   │
    │  ╚══╝ (4 total) ╚══╝   │
    │                         │
    │  ╔══╗           ╔══╗   │
    │  ║██║           ║██║   │
    │  ╚══╝           ╚══╝   │
    └─────────────────────────┘
          ↓ press inserts in
         with soldering iron
```

---

## Step 2 — Prepare the protoboard

Mount the ESP32-S3 SuperMini on the 50×70 mm protoboard.
**Orient the ESP32 so the USB-C port faces the BOTTOM edge of the board.**

```
    Protoboard (top view):
    ┌──────────────────────────────────────────────┐
    │  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  · │  ← top edge (faces up in box)
    │  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  · │
    │  ·  ·  ┌──────────────────────┐ ·  ·  ·  · │
    │  ·  ·  │   ESP32-S3 SuperMini │ ·  ·  ·  · │
    │  ·  ·  │  [antenna]           │ ·  ·  ·  · │
    │  ·  ·  │                      │ ·  ·  ·  · │
    │  ·  ·  └──────────────────────┘ ·  ·  ·  · │
    │  ·  ·  ·  ·  [USB-C here] ·  ·  ·  ·  ·  · │  ← bottom edge (USB-C faces down)
    └──────────────────────────────────────────────┘
               ↓ (faces bottom wall of box, USB-C slot lines up here)

    Also solder 8 short wires (~8 cm) for display connection.
    Leave the display ends free for now.

    Wiring:
    ┌─────────────────────────────────────────────────┐
    │  Display pin  →  ESP32-S3 GPIO                  │
    │  VCC          →  3.3V                           │
    │  GND          →  GND                            │
    │  CS           →  GPIO 10                        │
    │  DC           →  GPIO 2                         │
    │  RST          →  GPIO 3                         │
    │  MOSI         →  GPIO 11                        │
    │  SCK          →  GPIO 12                        │
    │  BLK          →  3.3V                           │
    └─────────────────────────────────────────────────┘
```

---

## Step 3 — Wire the display

Connect the free wire ends to the display module pin header.
Coil the wires loosely — they will loop in the 10 mm wire gap inside the box.

```
    Display PCB (back face — where pins are):

    ┌──────────────────────────────┐
    │                              │  ← top edge
    │     [screen on other side]   │
    │                              │
    │                              │
    │ [VCC][GND][CS][DC][RST]      │
    │ [MOSI][SCK][BLK]  ←pins     │  ← bottom edge (pin header row)
    └──────────────────────────────┘
         │   │   │   │   │   │
         └───┴───┴───┴───┴───┴── 8 cm jumper wires → protoboard
```

---

## Step 4 — Load display and protoboard into shell

Hold the shell with the **open back facing up** and the bezel window facing down.

```
    Shell cross-section (loading order, top = open back):

    ╔════════════════════════════╗  ← open back (you load from here)
    ║                            ║
    ║  4. protoboard + ESP32     ║  ← sits on side support ledges
    ║  ···························  ← ledges tied into shell walls
    ║  ·· wire slack zone ·······  ← 10 mm air gap, wires loop here
    ║  ···························
    ║  3. display PCB             ║  ← rests on inner ledge lip, screen down
    ╠════════════════════════════╣  ← bezel wall (front face)
    ║  [bezel window opening]    ║  ← screen visible from outside
    ╚════════════════════════════╝  ← front face (pointing toward camera)

    Step-by-step:
    a) Hold shell open-side up
    b) Drop display PCB in, screen facing DOWN (toward bezel window)
       — it rests on the inner ledge lip
    c) Feed jumper wires into the cavity
    d) Lower protoboard in, component-side UP
       — side ledges support the board edges
       — USB-C end faces the bottom wall slot
    e) Check USB-C aligns with the slot on the bottom wall
```

```
    Bottom wall — USB-C slot alignment:

    ─────────────────────────────────
    │  ╔════╗                       │  ← bottom wall (outside view)
    │  ║USB ║  ← slot cut in wall   │
    │  ╚════╝                       │
    ─────────────────────────────────
         ↑
    USB-C port of ESP32 must face here
    (route serial wires out the top notch)
```

---

## Step 5 — Snap the lid on

```
    Shell back opening (open side):        Lid (front view of rail side):

    ┌──────────────────────────┐           ┌──────────────────────────┐
    │  ╔══╗             ╔══╗  │           │  ┃━━┃             ┃━━┃  │
    │  ║  ║  ← slots   ║  ║  │           │  ┃  ┃  ← rails   ┃  ┃  │
    │  ║  ║  (4 sides) ║  ║  │           │  ┃  ┃  (4 sides) ┃  ┃  │
    │  ╚══╝             ╚══╝  │           │  ┗━━┛             ┗━━┛  │
    └──────────────────────────┘           └──────────────────────────┘

    Rails slide INTO slots. Press firmly and evenly until all 4 click.

    Side view of snap action:
           slot in shell wall
           │  ╔═╗  │
           │  ║ ║← rail tip with hook
           │  ║ ╚╗
           │  ║  ╚═ hook catches on slot edge → CLICK
           │  ║
           │  (lid floor)
```

---

## Step 6 — Bolt lid to mount bracket

The lid and mount are two separate printed parts:

- The **lid** has four raised boss columns. Install heat-set inserts into those bosses.
- The **mount** is the large flat strap plate. Its four center holes are through-holes.
- The **M3 bolt heads sit on the arm side of the mount**.
- The bolts pass through the mount and thread into the inserts in the lid.

```
    Exploded view (side, before tightening):

    ARM SIDE / ZIP TIE SIDE
              ↓
    ┌──────────────────────────┐
    │      STRAP MOUNT         │  ← bolt heads sit in this face
    │    ○              ○      │
    └──────────┬────┬──────────┘
               │M3×8│
               │bolt│  passes through mount
    ┌──────────▼────▼──────────┐
    │          LID             │  ← heat-set inserts are in these bosses
    │      ●            ●      │
    └──────────────────────────┘
       snap rails point into shell
    ┌──────────────────────────┐
    │          SHELL           │  ← display/protoboard inside
    └──────────────────────────┘
              ↓
    SCREEN SIDE / OUTWARD SIDE
```

Drive 4× M3×8 mm bolts through the strap mount into the lid boss inserts. After
that, snap the lid onto the shell.

---

## Step 7 — Mount on the SO-101 top arm

This mount is for the **top arm / upper link**: the long slanted purple link
between the shoulder and elbow in the photo. Do not put the face on the gripper.
Do not use the old base hook unless you intentionally render `base_mount`.

Open `top_arm_fit_preview.png` first if the location is unclear. It shows the
top arm in purple, the strap mount in amber, the face box in green, and the two
black straps wrapping around the upper link.

```
    VIEWED FROM THE SIDE OF THE TOP ARM

    ┌──────────────────────────────────────────────┐
    │              SO-101 top arm link             │
    └──────────────────────────────────────────────┘
          │                                  │
          │                                  │
          │                                  │
      zip tie                            zip tie
          │                                  │
    ┌─────┴──────────────────────────────────┴─────┐
    │              strap mount plate                │
    │       ○                              ○        │
    │                                                │
    │       ○                              ○        │
    └────────────────────────────────────────────────┘
                    │  M3×8 bolts into lid
                    ↓
             ┌──────────────────┐
             │   face display   │  ← screen faces outward
             └──────────────────┘
```

How to install:

1. Bolt the strap mount plate to the lid using 4× M3×8 bolts.
2. Snap the lid onto the face display shell.
3. Hold the face against the outside face of the top arm / upper link.
4. Feed one long zip tie through the left upper/lower slot pair and around the arm link.
5. Feed the second long zip tie through the right upper/lower slot pair and around the arm link.
6. Tighten both zip ties until the face cannot slide, but do not crush the printed arm.

---

## Final assembly exploded diagram

```
    ┌─────────────────────────┐
    │  SO-101 top arm link    │   ← zip ties wrap around this link
    └─────────────────────────┘
          ↑             ↑
          │             │
       zip tie       zip tie
          │             │
    ┌─────────────────────────┐
    │   STRAP MOUNT PLATE     │
    │   ○  ○  ○  ○            │   ← M3×8 bolts (4×) ↕
    └─────────────────────────┘
    ┌─────────────────────────┐
    │   ●  ●  ●  ●            │   ← LID (heat-set inserts in bosses)
    │   snap rails →  ┃ ┃ ┃ ┃ │
    └─────────────────────────┘
              ↓ press to snap
    ┌─────────────────────────┐
    │   ┌─────────────────┐   │   ← SHELL
    │   │  protoboard     │   │     inner cavity:
    │   │  [ESP32-S3]     │   │     • protoboard on side ledges
    │   └─────────────────┘   │     • wire gap below
    │   ↕ 8× jumper wires     │     • display PCB at front
    │   ┌─────────────────┐   │
    │   │  display PCB    │   │
    │   │  [screen →]     │   │
    │   └────[window]─────┘   │
    └─────────────────────────┘
              ↓
         screen visible
         from the front!
```

---

## Fit troubleshooting

| Problem | Fix in `face_enclosure.scad` |
|---------|------------------------------|
| Zip ties do not fit slots | Increase `STRAP_SLOT_W`, re-render `mount.stl` |
| Face slides on top arm | Add thin rubber tape between mount and arm, or tighten zip ties |
| Mount plate is too large | Reduce `STRAP_PLATE_W` / `STRAP_PLATE_H`, re-render `mount.stl` |
| Display PCB too tight in shell | `tol` 0.2 → 0.3, re-render `shell.stl` |
| Display PCB too loose | `tol` 0.2 → 0.1, re-render `shell.stl` |
| Wires too cramped | `WIRE_GAP` 10 → 15, re-render `shell.stl` + `lid.stl` |
| Lid won't snap closed | Sand the snap rails lightly |
| USB-C slot wrong height | Measure your actual flat-soldered stack, adjust `E_T` in scad |

---

## Re-render commands

```bash
cd face_display/cad
openscad -o shell.stl -D 'PART="shell"' face_enclosure.scad
openscad -o lid.stl   -D 'PART="lid"'   face_enclosure.scad
openscad -o mount.stl -D 'PART="mount"' face_enclosure.scad
```
