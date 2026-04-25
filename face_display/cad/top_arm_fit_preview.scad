// SO-101 face display top-arm fit preview.
//
// This is a visual assembly aid, not a print file.
// Purple = simplified upper arm link from Upper_arm_SO101.stl dimensions.
// Amber  = printable top-arm strap mount.
// Green  = face display enclosure.

use <face_enclosure.scad>

$fn = 32;

/* ---- measured from official Upper_arm_SO101.stl ---------- */
ARM_LEN = 142.1;
ARM_SIDE_H = 67.3;
ARM_THICK = 24.5;

/* ---- copied from face_enclosure.scad for placement -------- */
BOX_D = 26.2;
STRAP_PLATE_T = 4.0;
BACK_RAIL_H = 1.2;

module label(txt, p, size=5) {
    color("black")
        translate(p)
            rotate([70, 0, 0])
                linear_extrude(height=0.8)
                    text(txt, size=size, halign="center", valign="center");
}

module simplified_top_arm() {
    color([0.45, 0.25, 0.85, 0.45])
        translate([-ARM_LEN/2, 0, -ARM_SIDE_H/2])
            cube([ARM_LEN, ARM_THICK, ARM_SIDE_H]);

    // Approximate screw clusters so orientation matches the visible side link.
    color([0.04, 0.04, 0.05, 0.9])
        for (x=[-48, 48], z=[-20, 20])
            translate([x, -0.2, z])
                rotate([-90, 0, 0])
                    cylinder(d=5.5, h=1.0);
}

module mounted_face() {
    arm_side_y = 0;
    mount_back_y = arm_side_y - (STRAP_PLATE_T + BACK_RAIL_H/2);

    // Strap mount sits against the visible side of the top arm.
    color([1.0, 0.65, 0.05, 0.62])
        translate([0, mount_back_y, 0])
            rotate([-90, 0, 0])
                strap_mount();

    // Shell/lid assembly sits outside the strap plate, screen facing outward.
    color([0.15, 0.60, 0.20, 0.72])
        translate([0, mount_back_y - BOX_D, 0])
            rotate([-90, 0, 0])
                shell();
}

module strap_paths() {
    // Visual-only straps around the upper arm link.
    color([0.02, 0.02, 0.02, 0.78])
        for (x=[-40, 40])
            translate([x - 3, -(STRAP_PLATE_T + BACK_RAIL_H + 1.5), -ARM_SIDE_H/2 - 4])
                cube([6, ARM_THICK + STRAP_PLATE_T + BACK_RAIL_H + 3, ARM_SIDE_H + 8]);
}

module fit_preview() {
    simplified_top_arm();
    mounted_face();
    strap_paths();

    label("top arm / upper link", [0, ARM_THICK + 12, -24], 5);
    label("two straps wrap around this link", [0, ARM_THICK + 12, 24], 4.2);
    label("screen faces outward", [0, -BOX_D - 22, 0], 4.6);
}

fit_preview();
