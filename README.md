# SO-101

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
# Follower
lerobot-setup-motors --robot.type=so101_follower --robot.port=/dev/ttyACM0

# Leader
lerobot-setup-motors --teleop.type=so101_leader --teleop.port=/dev/ttyACM1
```

Leader arm gear ratios:

| Joint          | ID | Gear Ratio |
|----------------|----|------------|
| Shoulder Pan   | 1  | 1/191      |
| Shoulder Lift  | 2  | 1/345      |
| Elbow Flex     | 3  | 1/191      |
| Wrist Flex     | 4  | 1/147      |
| Wrist Roll     | 5  | 1/147      |
| Gripper        | 6  | 1/147      |

### 5. Calibrate

```bash
lerobot-calibrate --robot.type=so101_follower --robot.port=/dev/ttyACM0 --robot.id=my_follower_arm
lerobot-calibrate --teleop.type=so101_leader  --teleop.port=/dev/ttyACM1 --teleop.id=my_leader_arm
```

### 6. Teleoperate

```bash
lerobot-teleoperate \
  --robot.type=so101_follower --robot.port=/dev/ttyACM0 --robot.id=my_follower_arm \
  --teleop.type=so101_leader  --teleop.port=/dev/ttyACM1 --teleop.id=my_leader_arm
```

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

## References

- [SO-ARM100 GitHub](https://github.com/TheRobotStudio/SO-ARM100)
- [LeRobot SO-101 guide](https://huggingface.co/docs/lerobot/so101)
- [Discord](https://discord.gg/ggrqhPTsMe)
