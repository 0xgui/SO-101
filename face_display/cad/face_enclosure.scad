// ============================================================
//  SO-101 Face Display Enclosure
//  ESP32-S3 SuperMini + 2.0" ST7789V 240×320 SPI TFT
//  Bambu Labs A1 Combo — no supports required
//
//  PRINT ORIENTATION
//    shell → face-down on plate (bezel face against bed)
//    lid   → flat-side down
//    mount → flat-side down
//
//  RENDER EACH PART:
//    1. Set PART = "shell" → F6 → File > Export > STL
//    2. Set PART = "lid"   → repeat
//    3. Set PART = "mount" → repeat
//    (PART = "all" shows an exploded preview)
//
//  HARDWARE:
//    Display : 2.0" ST7789V 240×320 TFT, PCB ~42×60 mm
//    MCU     : ESP32-S3 SuperMini, PCB ~22.5×18 mm
//    Arm     : SO-ARM100 / SO-101
// ============================================================

PART = "shell";  // "shell" | "lid" | "mount" | "all"

/* ---- Tolerances ----------------------------------------- */
tol = 0.2;   // general clearance added to female dimensions

/* ---- 2.0" ST7789V display PCB --------------------------- */
D_W  = 50.0;   // PCB width
D_H  = 70.0;   // PCB height
D_T  =  1.6;   // PCB thickness

// Viewable window size
VW   = 27.2;
VH   = 36.7;
// Window center offset from PCB center (screen sits near top; pins at bottom)
VX   =  0.0;
VY   =  8.5;   // positive = toward top edge

// Connector / component protrusion behind the PCB
// (the pin header row at the bottom edge sticks out ~4 mm behind)
PIN_ZONE_H = 12.0;  // height of the pin zone at the bottom of the PCB
PIN_Z      =  4.5;  // how far pins protrude behind PCB back face

/* ---- ESP32-S3 SuperMini (mounted on protoboard) --------- */
E_T   =  4.5;   // tallest component height above protoboard surface
USB_W = 10.0;
USB_H =  4.0;

/* ---- 50×70 mm Protoboard -------------------------------- */
// Both the display and ESP32 connect via jumper wires.
// Display sits at the front (screen faces out through bezel window).
// Protoboard with ESP32 sits behind it.
PB_W  = 50.0;   // protoboard width  (matches display PCB width)
PB_H  = 70.0;   // protoboard height (matches display PCB height)
PB_T  =  1.6;   // protoboard PCB thickness
PB_SO =  2.0;   // standoff height (elevates protoboard off the cavity floor)

/* ---- Box shell ------------------------------------------ */
WALL  = 2.0;    // side/front wall thickness
LEDGE = 1.5;    // display-retainer lip width on inner cavity
WIRE_GAP = 10.0; // space between display back and protoboard front
                 // (jumper wires need ~8 cm to loop around, this gives slack)

// Depth layers (front → back):
//   WALL | display PCB | WIRE_GAP | standoff | protoboard | ESP32 components | margin
INNER_D = D_T + WIRE_GAP + PB_SO + PB_T + E_T + 2.0;

// Internal cavity XY (loose-fit for display PCB)
INNER_W = D_W + 2*tol;
INNER_H = D_H + 2*tol;

// Outer box (front face at z=0, opening at z = WALL + INNER_D)
BOX_W  = INNER_W + 2*WALL;
BOX_H  = INNER_H + 2*WALL;
BOX_D  = WALL + INNER_D;   // WALL = front face; open back for lid

/* ---- Lid ------------------------------------------------ */
LID_T  = 2.5;   // lid floor thickness
SNAP_W = 2.5;   // snap rail width (printed on lid, fits slot in shell)
SNAP_H = 6.0;   // snap rail height
SNAP_HOOK = 0.7;// hook undercut depth

/* ---- Arm mount bracket ---------------------------------- */
// Top-hook clamp — slides over the top edge of the SO-101 base.
// Two M3 tightening screws through the front arm lock it in place.
//
// SO-101 base measured from STL:
//   Width : 110.9 mm
//   Height:  87.0 mm  (we grip the top 18 mm)
//
ARM_BASE_W     = 111.0;  // base width  (X)
HOOK_WALL      =   3.5;  // all wall thickness
HOOK_GRIP      =  18.0;  // how far the arms extend downward from the cap
HOOK_DEPTH     =  35.0;  // front-to-back hook depth (35 mm bridges fine, no supports)
HOOK_CLEARANCE =   0.4;  // slip fit clearance each side

// Inner screw pattern: attaches to lid bosses (display box back)
LID_BOSS_X = 30.0;
LID_BOSS_Y = 40.0;
MH_D       =  3.3;  // M3 clearance hole

// Two M3 bolts through the front arm press against the arm's front face
CLAMP_SCREW_D = 3.3;

// Derived
HOOK_INNER_W = ARM_BASE_W + 2*HOOK_CLEARANCE;  // 111.8 mm
HOOK_OUTER_W = HOOK_INNER_W + 2*HOOK_WALL;     // 118.8 mm

// ============================================================
//  HELPERS
// ============================================================

module rbox(w, h, d, r=2.5) {
    // Rounded-corner box centered in XY, starting at z=0
    hull()
        for (sx=[-1,1], sy=[-1,1])
            translate([sx*(w/2-r), sy*(h/2-r), 0])
                cylinder(r=r, h=d, $fn=32);
}

// ============================================================
//  SHELL
// ============================================================
// Printed face-down. Front bezel is at z=0 (bed).
// Display slides in from the back (z = BOX_D end).
// Lid snaps onto the back.

module shell() {
    difference() {
        // Outer body
        rbox(BOX_W, BOX_H, BOX_D, r=2.5);

        // ── inner cavity (open at back z=BOX_D) ─────────────
        translate([0, 0, WALL])
            rbox(INNER_W, INNER_H, INNER_D + 0.1, r=1.5);

        // ── bezel window through front face ─────────────────
        // Wall goes z=0 → z=WALL. Cut must span z=-0.1 → z=WALL+0.1.
        translate([VX - VW/2, VY - VH/2, -0.1])
            cube([VW, VH, WALL + 0.2]);

        // ── USB-C slot on bottom wall ────────────────────────
        // ESP32 is on the protoboard; orient it so USB-C faces down.
        // z of USB-C centre: WALL + D_T + WIRE_GAP + PB_SO + PB_T + E_T/2
        usb_z = WALL + D_T + WIRE_GAP + PB_SO + PB_T + E_T/2;
        translate([0, -(BOX_H/2 + 0.1), usb_z])
            cube([USB_W + 2*tol, WALL*2 + 0.2, USB_H + 2*tol], center=true);

        // ── cable exit notch on back edge (top wall) ─────────
        translate([0, BOX_H/2 + 0.1, WALL + D_T + 2])
            cube([12, WALL*2 + 0.2, 8], center=true);

        // ── snap-rail slots at back opening (all 4 corners) ──
        // The lid's snap rails slide into these slots.
        slot_inset = 4.0;   // distance from corner
        slot_depth = SNAP_H + 0.2;
        slot_w     = SNAP_W + 2*tol;
        for (sx=[-1,1])
            translate([sx*(INNER_W/2 - slot_inset - slot_w/2),
                       0, BOX_D - slot_depth])
                cube([slot_w, INNER_H + 0.2, slot_depth + 0.1], center=true);
        for (sy=[-1,1])
            translate([0, sy*(INNER_H/2 - slot_inset - slot_w/2),
                       BOX_D - slot_depth])
                cube([INNER_W + 0.2, slot_w, slot_depth + 0.1], center=true);
    }

    // ── display PCB retainer lip ─────────────────────────────
    // A thin ledge just inside the front wall that captures the PCB edges.
    // Runs around all 4 sides except across the window opening.
    translate([0, 0, WALL])
    difference() {
        rbox(INNER_W, INNER_H, D_T + tol + 0.4, r=1.5);
        // Remove center — keep only ledge strip
        rbox(INNER_W - 2*LEDGE, INNER_H - 2*LEDGE, D_T + tol + 0.6, r=0.5);
        // Remove over window so it does not block the screen
        translate([VX, VY, -0.1])
            cube([VW + 2, VH + 2, D_T + 2], center=true);
    }

    // ── Protoboard standoff pegs ─────────────────────────────
    // 4 corner pegs the 50×70 mm protoboard rests on.
    // Protoboard front face sits at z = WALL + D_T + WIRE_GAP + PB_SO
    peg_r  = 2.0;
    peg_z  = WALL + D_T + WIRE_GAP;
    peg_h  = PB_SO;
    pb_inset = 3.0;   // peg center inset from protoboard edge
    for (sx=[-1,1], sy=[-1,1])
        translate([sx*(PB_W/2 - pb_inset), sy*(PB_H/2 - pb_inset), peg_z])
            cylinder(r=peg_r, h=peg_h, $fn=16);
}

// ============================================================
//  LID
// ============================================================
// Flat plate + snap rails + M3 boss columns for mount bracket.
// Printed flat-side down (rails point up).

module lid() {
    BOSS_OD = 7.0;
    BOSS_H  = 5.0;
    INSERT_D = 4.2;  // M3 heat-set insert bore

    slot_inset = 4.0;

    union() {
        difference() {
            rbox(BOX_W, BOX_H, LID_T, r=2.5);
            // Wire notch on top edge (same side as shell cable exit)
            translate([0, BOX_H/2 + 0.1, LID_T/2])
                cube([12, WALL*2 + 0.2, 8], center=true);
        }

        // Snap rails (slide into shell slots)
        for (sx=[-1,1])
            translate([sx*(INNER_W/2 - slot_inset - SNAP_W/2), 0, LID_T])
            difference() {
                cube([SNAP_W, INNER_H - 2*slot_inset, SNAP_H], center=true);
                // Hook undercut on outer face (pulled inward when sliding in)
                translate([sx*(-SNAP_W/2 + SNAP_HOOK/2), 0, SNAP_H/2 - 2])
                    cube([SNAP_HOOK + 0.1, INNER_H, 2.5], center=true);
            }
        for (sy=[-1,1])
            translate([0, sy*(INNER_H/2 - slot_inset - SNAP_W/2), LID_T])
            difference() {
                cube([INNER_W - 2*slot_inset, SNAP_W, SNAP_H], center=true);
                translate([0, sy*(-SNAP_W/2 + SNAP_HOOK/2), SNAP_H/2 - 2])
                    cube([INNER_W, SNAP_HOOK + 0.1, 2.5], center=true);
            }

        // M3 boss columns for bracket screws
        for (sx=[-1,1], sy=[-1,1])
            translate([sx*LID_BOSS_X/2, sy*LID_BOSS_Y/2, LID_T])
            difference() {
                cylinder(d=BOSS_OD, h=BOSS_H, $fn=20);
                translate([0, 0, -0.1])
                    cylinder(d=INSERT_D, h=BOSS_H + 0.2, $fn=20);
            }
    }
}

// ============================================================
//  ARM MOUNT BRACKET — top-hook clamp
// ============================================================
//
//  Coordinate system (local, non-centered):
//    X: left ← 0 → right  (centered by caller)
//    Y: 0 = front face of bracket, positive = into arm
//    Z: 0 = bottom of face plate, positive = up
//
//  Side view (Y-Z cross section):
//
//    Z
//    │  [top cap]──────────────────┐  ← Z = face_h + HOOK_GRIP + HOOK_WALL
//    │  │                          │
//    │  │ front arm   back arm     │  ← HOOK_GRIP tall
//    │  │ (Y=0..HW)  (Y=HW+HD..)  │
//    │  └──┐ ARM SITS HERE  ┌──────┘  ← Z = face_h
//    │     │                │
//    │     │  face plate    │         ← face_h tall
//    │     │  (Y=0..HW)     │
//    │     │  display box   │
//    │     │  attaches here │
//    └─────────────────────────── Y
//
//  HW = HOOK_WALL, HD = HOOK_DEPTH
//
//  Print orientation: face plate face-down on bed.
//  The 35mm bridge (top cap inner span) prints fine on A1 without supports.

module mount() {
    face_w = BOX_W + 10;    // face plate width (display box + margin = ~64 mm)
    face_h = BOX_H + 10;    // face plate height (~84 mm)

    difference() {
        union() {
            // ── face plate ────────────────────────────────────
            // Y: 0 → HOOK_WALL,  Z: 0 → face_h,  X: centered
            translate([-face_w/2, 0, 0])
                cube([face_w, HOOK_WALL, face_h]);

            // ── hook front arm ────────────────────────────────
            // Continues face plate upward, wide enough to cover arm
            // Y: 0 → HOOK_WALL,  Z: face_h → face_h+HOOK_GRIP
            translate([-HOOK_OUTER_W/2, 0, face_h])
                cube([HOOK_OUTER_W, HOOK_WALL, HOOK_GRIP]);

            // ── hook top cap ──────────────────────────────────
            // Bridges front arm to back arm
            // Y: 0 → HOOK_WALL+HOOK_DEPTH+HOOK_WALL,  Z: face_h+HOOK_GRIP → +HOOK_WALL
            translate([-HOOK_OUTER_W/2, 0, face_h + HOOK_GRIP])
                cube([HOOK_OUTER_W,
                      HOOK_WALL + HOOK_DEPTH + HOOK_WALL,
                      HOOK_WALL]);

            // ── hook back arm ─────────────────────────────────
            // Hangs from back edge of top cap
            // Y: HOOK_WALL+HOOK_DEPTH → +HOOK_WALL,  Z: face_h → face_h+HOOK_GRIP
            translate([-HOOK_OUTER_W/2,
                       HOOK_WALL + HOOK_DEPTH,
                       face_h])
                cube([HOOK_OUTER_W, HOOK_WALL, HOOK_GRIP]);
        }

        // ── M3 holes through face plate for lid bosses ────────
        // Centered on face plate (Z = face_h/2 ± LID_BOSS_Y/2)
        for (sx=[-1,1], sy=[-1,1])
            translate([sx*LID_BOSS_X/2, -0.1, face_h/2 + sy*LID_BOSS_Y/2])
                rotate([-90, 0, 0])
                    cylinder(d=MH_D, h=HOOK_WALL + 0.2, $fn=20);

        // ── 2× M3 tightening holes through front hook arm ─────
        // Bolts press on arm's front face to lock the clamp
        for (sx=[-1,1])
            translate([sx*25, -0.1, face_h + HOOK_GRIP/2])
                rotate([-90, 0, 0])
                    cylinder(d=CLAMP_SCREW_D, h=HOOK_WALL + 0.2, $fn=20);
    }
}

// ============================================================
//  RENDER
// ============================================================

if (PART == "shell") {
    shell();
}
else if (PART == "lid") {
    // Flip for printing (rails face up, lid back on plate)
    translate([0, 0, LID_T])
        rotate([180, 0, 0])
            lid();
}
else if (PART == "mount") {
    mount();
}
else if (PART == "all") {
    // Exploded assembly preview
    color("SteelBlue")   shell();
    color("SlateGray", 0.85) translate([0, 0, BOX_D + 8]) lid();
    color("DimGray")     translate([BOX_W + 15, 0, 0]) mount();
}
