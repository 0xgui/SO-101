# SO-101
![botharms](https://github.com/user-attachments/assets/1c444c48-3b49-40f4-9793-57ff7570cd64)

Build notes and tooling for the [SO-101 robot arm](https://github.com/TheRobotStudio/SO-ARM100) — two arms (leader + follower) using STS3215 servos and LeRobot.

## Hardware

- 13x STS3215 7.4V servos (7 follower, 6 leader)
- 2x Waveshare Motor Control Boards
- 2x USB-C cables + 5V power supplies
- 4x table clamps

## Setup

### 1. Install LeRobot

```bash
pip install -e ".[feetech]"
```

### 2. Fix USB permissions (Linux)

```bash
sudo chmod 666 /dev/ttyACM0
```

Permanent fix (requires re-login):
```bash
sudo usermod -aG dialout $USER
```

### 3. Find ports

```bash
lerobot-find-port
```

### 4. Configure motor IDs

Run once per arm, one motor at a time:

```bash
# Follower (uses --robot.*)
lerobot-setup-motors --robot.type=so101_follower --robot.port=/dev/ttyACM0

# Leader (uses --teleop.*)
lerobot-setup-motors --teleop.type=so101_leader --teleop.port=/dev/ttyACM0
```

Motor IDs assigned (same for both arms):

| Joint          | ID |
|----------------|----|
| Shoulder Pan   | 1  |
| Shoulder Lift  | 2  |
| Elbow Flex     | 3  |
| Wrist Flex     | 4  |
| Wrist Roll     | 5  |
| Gripper        | 6  |

### 5. Calibrate

```bash
# Follower (uses --robot.*)
lerobot-calibrate --robot.type=so101_follower --robot.port=/dev/ttyACM0 --robot.id=my_follower_arm

# Leader (uses --teleop.*)
lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/ttyACM0 --teleop.id=my_leader_arm
```

During calibration: move all joints through their full range except `wrist_roll`, which is a continuous rotation joint.

### 6. Teleoperate

Run `lerobot-find-port` with each arm plugged in separately to confirm which port maps to which arm. Then:

```bash
lerobot-teleoperate \
  --robot.type=so101_follower --robot.port=/dev/ttyACM1 --robot.id=my_follower_arm \
  --teleop.type=so101_leader  --teleop.port=/dev/ttyACM0 --teleop.id=my_leader_arm
```

If you see a calibration mismatch prompt on startup, press Enter to load the saved calibration file.

## Scripts

### `test_servo.py`

Auto-detects the range of a single servo and sweeps min → center → max.

```bash
python3 test_servo.py
```

### `calibrate_servo.py`

Move servo by hand (torque off) to set min/max, then replays the motion under power.

```bash
python3 calibrate_servo.py
```

---

## Face Display (`face_display/`)

ESP32-S3 SuperMini + 2.0" ST7789V 240x320 SPI TFT. Receives serial commands from the LeRobot controller and shows animated retro ASCII Kaomoji expressions.

*(Note: The face rendering utilizes a custom differential screen-wipe bypass directly addressing `TFT_eSPI` to stop the ESP32-S3 from crashing due to memory fragmentation.)*

### Wiring

| Display | ESP32-S3 |
|---------|----------|
| VCC     | 3.3V     |
| GND     | GND      |
| CS      | GPIO 10  |
| DC      | GPIO 2   |
| RST     | GPIO 3   |
| MOSI    | GPIO 11  |
| SCK     | GPIO 12  |
| BLK     | 3.3V     |

### Flash

```bash
pip install platformio
cd face_display
# set upload_port in platformio.ini (e.g., /dev/ttyACM0)
pio run -t upload
pio device monitor
```

### Commands (115200 baud)

Send over serial to trigger the color-coded ASCII expressions:
`FACE:IDLE` `FACE:HAPPY` `FACE:SAD` `FACE:BLINK` `FACE:TALK`

### Python

```python
import serial
face = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
face.write(b"FACE:HAPPY\n")
```

---

## References

- [SO-ARM100 GitHub](https://github.com/TheRobotStudio/SO-ARM100)
- [LeRobot SO-101 guide](https://huggingface.co/docs/lerobot/so101)
- [Discord](https://discord.gg/ggrqhPTsMe)
