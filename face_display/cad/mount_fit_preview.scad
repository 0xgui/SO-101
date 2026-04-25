// SO-101 face display mount fit preview.
//
// This is a visual assembly aid, not a print file.
// Blue  = raised top lip of the fixed SO-101 base.
// Gray  = simplified fixed base / shoulder-pan housing.
// Amber = face display mount bracket.
// Green = display enclosure shell.

use <face_enclosure.scad>

$fn = 32;

/* ---- measured SO-101 base reference ---------------------- */
BASE_W = 110.925;
BASE_D = 72.0;
BASE_H = 87.0;

TOP_W = 82.4;
TOP_D = 17.5;
TOP_H = 18.0;

/* ---- copied from face_enclosure.scad for placement -------- */
BOX_W = 54.4;
BOX_H = 74.4;
BOX_D = 26.2;

HOOK_WALL = 3.5;
HOOK_GRIP = 18.0;
HOOK_CLEARANCE = 0.4;
FACE_H = BOX_H + 10.0;

MOUNT_Z = BASE_H - (FACE_H + HOOK_GRIP);
BASE_Y = HOOK_WALL + HOOK_CLEARANCE;
TOP_Y = HOOK_WALL + HOOK_CLEARANCE;

module label(txt, p, size=5) {
    color("black")
        translate(p)
            rotate([70, 0, 0])
                linear_extrude(height=0.8)
                    text(txt, size=size, halign="center", valign="center");
}

module simplified_so101_base() {
    // Main fixed base / shoulder-pan housing, shown as a transparent block.
    color([0.55, 0.55, 0.55, 0.28])
        translate([-BASE_W/2, BASE_Y, 0])
            cube([BASE_W, BASE_D, BASE_H - TOP_H]);

    // The top lip is the only part captured by the printed U-hook.
    color([0.05, 0.35, 1.0, 0.75])
        translate([-TOP_W/2, TOP_Y, BASE_H - TOP_H])
            cube([TOP_W, TOP_D, TOP_H]);
}

module assembled_shell() {
    // Map shell coordinates into assembly coordinates:
    // shell x -> mount x, shell depth z -> mount/front y,
    // shell vertical y -> mount vertical z.
    color([0.15, 0.60, 0.20, 0.70])
        multmatrix([
            [1, 0, 0, 0],
            [0, 0, 1, -BOX_D],
            [0, 1, 0, MOUNT_Z + FACE_H/2],
            [0, 0, 0, 1]
        ])
            shell();
}

module fit_preview() {
    simplified_so101_base();

    color([1.0, 0.65, 0.05, 0.48])
        translate([0, 0, MOUNT_Z])
            mount();

    assembled_shell();

    label("fixed SO-101 base", [0, BASE_Y + BASE_D/2, 18], 5);
    label("raised top lip inside U-hook", [0, TOP_Y + TOP_D/2, BASE_H + 9], 4.3);
    label("face box bolts to front plate", [0, -BOX_D - 12, MOUNT_Z + FACE_H/2], 4.3);
}

fit_preview();
