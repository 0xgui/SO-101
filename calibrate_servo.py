"""
Manual calibration: move servo by hand to set min/max, then replay.
- Torque is disabled so you can freely move the servo by hand.
- Press Enter to record each position.
"""
import time
from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors.motors_bus import Motor, MotorNormMode

PORT = "/dev/ttyACM0"
MOTOR_NAME = "gripper"
MOTOR_ID = 6
BUFFER = 40  # steps away from hard stop to avoid overload

bus = FeetechMotorsBus(
    port=PORT,
    motors={MOTOR_NAME: Motor(MOTOR_ID, "sts3215", MotorNormMode.RANGE_0_100)},
)
bus.connect(handshake=False)

def torque(on: bool):
    bus.write("Torque_Enable", MOTOR_NAME, 1 if on else 0, normalize=False)
    time.sleep(0.2)

def read_pos():
    return bus.read("Present_Position", MOTOR_NAME, normalize=False)

def move(target, delay=1.5):
    try:
        bus.write("Goal_Position", MOTOR_NAME, int(target), normalize=False)
        time.sleep(delay)
    except RuntimeError:
        torque(False)
        time.sleep(0.3)
        torque(True)
    return read_pos()

def safe_enable_torque():
    """Enable torque without the motor jumping to a stale Goal_Position."""
    # Read current pos and write it as goal before enabling torque
    current = read_pos()
    torque(True)
    move(current, delay=0.3)

def midpoint_with_wrap(a, b, total=4096):
    """Compute midpoint accounting for encoder wrap-around."""
    if b >= a:
        return (a + b) // 2
    # range crosses 0: a is high (e.g. 2583), b is low (e.g. 1180)
    # going right from a means decreasing through 0 to b
    span = (a - b) % total         # steps from a to b going right (decreasing)
    mid_offset = span // 2
    return (a - mid_offset) % total

# --- Calibrate MIN ---
torque(False)
print("=" * 40)
print("STEP 1: MINIMUM position (left / closed)")
print("Torque OFF — move servo to the left limit by hand.")
input("Press Enter to record...")
min_pos = read_pos()
print(f"  MIN recorded: {min_pos}")

# --- Calibrate MAX ---
print("\n" + "=" * 40)
print("STEP 2: MAXIMUM position (right / open)")
print("Move servo to the right limit by hand.")
input("Press Enter to record...")
max_pos = read_pos()
print(f"  MAX recorded: {max_pos}")

# Apply buffer away from hard stops
# min is the left (high encoder), max is right (low encoder if wrapped)
safe_min = min_pos - BUFFER   # back off left stop rightward
safe_max = max_pos + BUFFER   # back off right stop leftward (works for both cases)
center = midpoint_with_wrap(safe_min, safe_max)

print(f"\nCalibration done.")
print(f"  Raw:  min={min_pos}  max={max_pos}")
print(f"  Safe: min={safe_min}  max={safe_max}  center={center}")

# Re-enable torque without jumping
safe_enable_torque()

# --- Replay ---
print("\nMoving to CENTER...")
move(center)
print(f"  Position: {read_pos()}")

input("\nPress Enter to move to MIN (left)...")
move(safe_min)
print(f"  Position: {read_pos()}")

input("Press Enter to move to MAX (right)...")
move(safe_max)
print(f"  Position: {read_pos()}")

input("Press Enter to return to CENTER and exit...")
move(center)
print(f"  Position: {read_pos()}")

bus.disconnect()
print("Done.")
