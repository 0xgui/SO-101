# Face Display — Assembly Guide

---

## Parts overview

Three parts to print + hardware:

```
                    SHELL                          LID                    MOUNT BRACKET
         (front view, bezel side)          (back view)                 (front view)

    ┌─────────────────────────┐      ┌─────────────────────────┐   ╔═══╦═════════════╦═══╗
    │  ┌───────────────────┐  │      │  ●               ●  │  │   ║   ║             ║   ║
    │  │   bezel window    │  │      │  │  (M3 boss cols)│  │  │   ║   ║  face plate ║   ║
    │  │  (screen shows    │  │      │  │                │  │  │   ║   ║  (display   ║   ║
    │  │   through here)   │  │      │  │                │  │  │   ║   ║   box bolts ║   ║
    │  └───────────────────┘  │      │  │                │  │  │   ║   ║   here)     ║   ║
    │                         │      │  ●               ●  │  │   ║   ║             ║   ║
    │  [USB-C slot on bottom] │      └─────────────────────────┘   ║   ║  ● holes ● ║   ║
    └─────────────────────────┘                                     ╚═══╩═════════════╩═══╝
                                           ↑ snap rails on inside        ↑ wide U-hook on top
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
      │← 2mm →│← 1.6mm →│←── 10mm ──→│← 2mm →│← 1.6mm →│← 4.5mm →│← 2mm →│
      │  wall  │ display  │ wire slack  │standof│protoboard│  ESP32  │margin │
      │        │   PCB    │  (jumpers   │  pegs │          │ chips   │       │
      │[window]│[screen→] │  loop here) │       │[ESP32-S3]│         │       │
      │        │          │             │       │          │         │       │
    ══╪════════╪══════════╪═════════════╪═══════╪══════════╪═════════╪═══════╪══
      z=0    z=2        z=3.6       z=13.6  z=15.6     z=17.2    z=21.7  z=23.7
                                                                      (BOX_D total ~24mm)
```

---

## Hardware list

| Item | Qty | Purpose |
|------|-----|---------|
| M3 heat-set inserts | 8 | 4 in lid boss columns + 4 in mount face plate |
| M3×8 mm bolts | 8 | Lid → mount bracket |
| M3×12 mm bolts | 2 | Hook tightening screws (lock bracket to arm) |
| Jumper wires ~8 cm | 8 | Display PCB → protoboard |
| Soldering iron (220 °C) | 1 | Installing heat-set inserts |

---

## Step 1 — Install heat-set inserts

Use a soldering iron at ~220 °C. Press each insert flush or just below the surface.

```
    LID (back face up):                    MOUNT BRACKET (front face up):

    ┌─────────────────────────┐            ┌─────────────────────────┐
    │  ╔══╗           ╔══╗   │            │   ╔══╗           ╔══╗   │
    │  ║██║  boss     ║██║   │            │   ║██║  boss     ║██║   │
    │  ║██║  columns  ║██║   │            │   ║██║  columns  ║██║   │
    │  ╚══╝ (4 total) ╚══╝   │            │   ╚══╝ (4 total) ╚══╝   │
    │                         │            │                         │
    │  ╔══╗           ╔══╗   │            │   ╔══╗           ╔══╗   │
    │  ║██║           ║██║   │            │   ║██║           ║██║   │
    │  ╚══╝           ╚══╝   │            │   ╚══╝           ╚══╝   │
    └─────────────────────────┘            └─────────────────────────┘
          ↓ press inserts in                     ↓ press inserts in
         with soldering iron                    with soldering iron
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
    ║  4. protoboard + ESP32     ║  ← sits on 4 corner standoff pegs
    ║  ···························  ← standoff pegs (2 mm tall)
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
       — 4 corner pegs locate it automatically
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

```
    Exploded view (side):

    ┌──────────────────────────┐  ← shell (display inside)
    └──────────────────────────┘
    ┌──────────────────────────┐  ← lid (snap rails face into shell)
    │  ●    ●    ●    ●       │    boss columns point outward
    └──────────────────────────┘
           ↕ M3×8 mm bolts (8×)
    ┌──────────────────────────┐  ← mount bracket face plate
    │  ○    ○    ○    ○       │    holes align with lid boss inserts
    └──────────────────────────┘
```

Drive 8× M3×8 mm bolts through the mount face plate into the lid boss inserts.

---

## Step 7 — Mount on the SO-101 arm

The mount bracket is a **U-hook** that slides over the top edge of the SO-101 base.

```
    Side view of mount + arm (cross-section):

         FRONT                      BACK
           │                          │
    ───────┤← face plate (3.5 mm) ───┤
           │  [display box bolted     │
           │   here on front]         │
    ───────┤                          │
           │  ┌────────────────────┐  │
           │  │  hook front arm    │  │  ← 18 mm tall
           │  │  (3.5 mm thick)   │  │
    ═══════╪══╧══════════╤═════════╧══╪══  ← top cap (bridges 35 mm)
           │             │            │
           │             │            │  ← hook back arm (18 mm tall)
           │   SO-101    │            │
           │   base      │            │
           │   (arm      │            │
           │   body      │            │
           │   here)     │            │
           │             │            │

    Bracket width = 119 mm (arm is 111 mm wide — 4 mm clearance each side)
    Hook depth    =  35 mm into the arm from front
    Hook grip     =  18 mm down each side from the top cap

    HOW TO INSTALL:
    a) Hold bracket above arm base, hook opening facing DOWN
    b) Lower onto arm — hook slides over the top edge
    c) Push down until hook arms sit 18 mm below the arm top surface
    d) Thread 2× M3×12 mm bolts through the two holes in the
       hook FRONT ARM — tighten until they press against the
       arm's front face and the bracket cannot slide up
```

```
    Front view — bracket on arm:

    ┌───────────────────────────────────────────┐  ← top cap (above arm top)
    │                                           │
    ╠═════════╦═════════════════════╦═════════╣  ← hook front arm
    │         │                     │         │    (2× M3 bolts here → ●  ●)
    │         │   SO-101 base top   │         │
    │         │   (arm body here)   │         │
    │         │                     │         │
    ╠═════════╩═════════════════════╩═════════╣  ← hook bottom (18 mm below cap)
    │                                         │
    │         face plate (display box         │
    │         bolts to this surface)          │
    │                                         │
    │         ●           ●                   │  ← M3 boss holes
    │                                         │
    │         ●           ●                   │
    │                                         │
    └─────────────────────────────────────────┘
```

---

## Final assembly exploded diagram

```
                        ╔══════════╗
                        ║  SO-101  ║
                        ║   arm    ║
                        ║  base    ║
                        ╚══════════╝
                             ↑
                    slides up into hook
                             │
    ╔══╦═══════════════════╦══╗   ← MOUNT BRACKET
    ║  ║   hook (U-shape)  ║  ║     (119mm wide)
    ╠══╩═══════════════════╩══╣
    │      face plate         │
    │   ○  ○  ○  ○            │   ← M3×8 bolts (8×) ↕
    └─────────────────────────┘
    ┌─────────────────────────┐
    │   ●  ●  ●  ●            │   ← LID (heat-set inserts in bosses)
    │   snap rails →  ┃ ┃ ┃ ┃ │
    └─────────────────────────┘
              ↓ press to snap
    ┌─────────────────────────┐
    │   ┌─────────────────┐   │   ← SHELL
    │   │  protoboard     │   │     inner cavity:
    │   │  [ESP32-S3]     │   │     • protoboard on pegs
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
| Hook too tight on arm | `HOOK_CLEARANCE` 0.4 → 0.8, re-render `mount.stl` |
| Hook too loose | `HOOK_CLEARANCE` 0.4 → 0.1, re-render `mount.stl` |
| Display PCB too tight in shell | `tol` 0.2 → 0.3, re-render `shell.stl` |
| Display PCB too loose | `tol` 0.2 → 0.1, re-render `shell.stl` |
| Wires too cramped | `WIRE_GAP` 10 → 15, re-render `shell.stl` + `lid.stl` |
| Lid won't snap closed | Sand the snap rails lightly |
| USB-C slot wrong height | Measure your actual setup, adjust `E_T` in scad |

---

## Re-render commands

```bash
cd face_display/cad
openscad -o shell.stl -D 'PART="shell"' face_enclosure.scad
openscad -o lid.stl   -D 'PART="lid"'   face_enclosure.scad
openscad -o mount.stl -D 'PART="mount"' face_enclosure.scad
```
