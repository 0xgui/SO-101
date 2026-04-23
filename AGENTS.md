# AGENTS.md — SO-101

Personal build notes / tooling for the SO-101 robot arm (leader + follower) using LeRobot and STS3215 servos.

## Repo structure

```
├── README.md                         # Main setup docs; follow for hardware bring-up
├── NOTES.md                          # Scratch notes, next-features for face display
├── test_servo.py                     # Sweep a single servo (hardcoded defaults)
├── calibrate_servo.py                # Torque-off manual min/max calibration
├── find_port.sh                      # Detect /dev/ttyUSB* or /dev/ttyACM* port changes
└── face_display/
    ├── platformio.ini                # ESP32-S3 SuperMini + ST7789V TFT config
    ├── src/main.cpp                  # Face renderer; reads serial commands, 115200
    ├── src/faces.h                   # ASCII Kaomoji tables
    ├── cad/
    │   ├── face_enclosure.scad       # Parametric enclosure (shell / lid / mount)
    │   ├── generate_build_plate.py   # Arranges STLs into build_plate.stl
    │   ├── build_plate.stl           # Combined slicer-ready plate
    │   └── ASSEMBLY.md               # Full assembly guide
    └── (Standard PlatformIO layout)
```

## Key architectural facts

- **LeRobot lives in `/home/gs/projects/github/lerobot` and is installed via a `conda` environment named `lerobot`.** Before running any LeRobot CLI, activate it:
  ```bash
  conda activate lerobot
  ```
- **USB serial:** Linux users need `/dev/ttyACM0` access. Run once: `sudo usermod -aG dialout $USER` (requires re-login), or `sudo chmod 666 /dev/ttyACM0` for a temporary fix.
- **Port discovery:** `lerobot-find-port` identifies which arm is on which port. If unsure, run `find_port.sh` (snapshots ports before/after plugging in a device).
- **Robot IDs used in this repo:** follower is `purple_bot`, leader is `yellow_bot`.

## Tooling commands

| Task | Command |
|------|---------|
| Find LeRobot motor bus ports | `lerobot-find-port` |
| Set motor IDs (follower) | `lerobot-setup-motors --robot.type=so101_follower --robot.port=/dev/ttyACM0` |
| Set motor IDs (leader) | `lerobot-setup-motors --teleop.type=so101_leader --teleop.port=/dev/ttyACM0` |
| Calibrate (follower) | `lerobot-calibrate --robot.type=so101_follower --robot.port=/dev/ttyACM0 --robot.id=purple_bot` |
| Calibrate (leader) | `lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/ttyACM0 --teleop.id=yellow_bot` |
| Teleoperate | `lerobot-teleoperate --robot.type=so101_follower --robot.port=/dev/ttyACM1 --robot.id=purple_bot --teleop.type=so101_leader --teleop.port=/dev/ttyACM0 --teleop.id=yellow_bot` |
| Flash face display | `cd face_display && pio run -t upload` |
| Rebuild single STL from OpenSCAD | `openscad -o shell.stl -D 'PART="shell"' face_display/cad/face_enclosure.scad` |
| Regenerate build plate | `python3 face_display/cad/generate_build_plate.py` |

## Hardcoded values that must be verified before running scripts

- **Port:** `PORT = "/dev/ttyACM0"` in all Python scripts
- **Motor ID:** `MOTOR_ID = 6` (gripper) in `test_servo.py` and `calibrate_servo.py`
- **Motor name:** `MOTOR_NAME = "gripper"` in both scripts

These must be edited to match the actual connected motor before use.

## Face display firmware constraints

- The ESP32-S3 SuperMini has **limited SRAM**. `main.cpp` intentionally draws directly to the TFT hardware (`renderer->draw(..., autoBlinking)`) rather than using a `TFT_eSprite` RAM buffer. A previous sprite-based implementation caused memory panics and reboots.
- Serial protocol: newline-terminated strings at `115200` baud: `FACE:IDLE`, `FACE:HAPPY`, `FACE:SAD`, `FACE:BLINK`, `FACE:TALK`.
- `TFT_eSPI` pin config is fully driven via `build_flags` in `platformio.ini` (never edit the library's `User_Setup.h`).

## CAD / enclosure facts

- `face_enclosure.scad` is parametric. Key tunables:
  - `ARM_BASE_W = 111.0` — measured from the official SO-101 `Base_SO101.stl` (110.9 mm)
  - `HOOK_CLEARANCE = 0.4` — slip-fit each side
  - `D_W / D_H = 50.0 / 70.0` — display PCB cavity (verify against your actual display)
  - `WIRE_GAP = 10.0` — slack space between display and ESP32 protoboard
- `generate_build_plate.py` uses `openscad` CLI to render `build_plate.stl`. Requires OpenSCAD on PATH.

## Imitation Learning

For the full LeRobot IL pipeline (record → train ACT → evaluate) with camera setup, see [`IL_WORKFLOW.md`](IL_WORKFLOW.md).

## Conventions

- Commit messages follow the repo's style: `{Add,Fix,Update} <short description>`
- Python scripts have **no tests** — verification is done physically on the arm
- Hardware docs live in `ASSEMBLY.md` (face display), `README.md` (overall setup), and `NOTES.md` (scratch / next-up)

## Common pitfalls

1. **LeRobot not installed** → `ModuleNotFoundError: lerobot`. Solution: `conda activate lerobot`.
2. **USB permission denied** → `PermissionError: [Errno 13] /dev/ttyACM0`. Solution: add user to `dialout` group or `chmod 666`.
3. **Face display upload fails** → wrong `upload_port` in `platformio.ini`. Solution: run `./find_port.sh` and let it patch the `platformio.ini`.
4. **OpenSCAD not on PATH** → `generate_build_plate.py` fails. Solution: `apt install openscad`.
5. **Mount bracket too tight or loose** → adjust `HOOK_CLEARANCE` in `face_enclosure.scad`, re-render `mount.stl`.
