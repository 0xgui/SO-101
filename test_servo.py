"""Test servo: auto-find range, then sweep left and right."""
import time
from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors.motors_bus import Motor, MotorNormMode

PORT = "/dev/ttyACM0"
MOTOR_NAME = "gripper"
MOTOR_ID = 6

bus = FeetechMotorsBus(
    port=PORT,
    motors={MOTOR_NAME: Motor(MOTOR_ID, "sts3215", MotorNormMode.RANGE_0_100)},
)
bus.connect(handshake=False)

def read_pos():
    try:
        return bus.read("Present_Position", MOTOR_NAME, normalize=False)
    except RuntimeError:
        return None

def reset_overload():
    """Clear overload error by toggling torque off then on."""
    try:
        bus.write("Torque_Enable", MOTOR_NAME, 0, normalize=False)
        time.sleep(0.3)
        bus.write("Torque_Enable", MOTOR_NAME, 1, normalize=False)
        time.sleep(0.3)
        print("  Overload reset.")
    except RuntimeError as e:
        print(f"  Reset failed: {e}")

def move(target, delay=0.5):
    """Returns actual position reached, or None on overload."""
    try:
        bus.write("Goal_Position", MOTOR_NAME, target, normalize=False)
        time.sleep(delay)
        return read_pos()
    except RuntimeError:
        reset_overload()
        return None

# --- Step 1: find min by scanning toward 0 ---
print("Finding minimum position (moving toward 0)...")
current = read_pos()
min_pos = current
step = 100

prev = min_pos
for target in range(current, -1, -step):
    result = move(target)
    if result is None:
        print(f"  Hit lower limit, min = {min_pos}")
        break
    # wrap-around: position jumped way up (past 0 into 4095 territory)
    if result > prev + 500:
        print(f"  Hit lower limit (wrap), min = {min_pos}")
        break
    # motor lagging far behind target = hit hard stop
    if (result - target) > 200:
        print(f"  Hit lower limit, min = {min_pos}")
        break
    prev = min_pos
    min_pos = result
    print(f"  pos: {min_pos}")

# --- Step 2: find max by scanning toward 4095 ---
# Start from min_pos + step to move away from the hard limit
print(f"\nFinding maximum position (moving toward 4095)...")
start = min_pos + step
move(start, delay=1.0)  # move away from lower limit first
max_pos = read_pos() or start

for target in range(start, 6000, step):
    result = move(target)
    if result is None:
        print(f"  Hit upper limit, max = {max_pos}")
        break
    # motor lagging far behind target = hit hard stop
    if (target - result) > 400:
        print(f"  Hit upper limit, max = {max_pos}")
        break
    max_pos = result
    print(f"  pos: {max_pos}")

# --- Step 3: sweep ---
center = (min_pos + max_pos) // 2
print(f"\nRange: {min_pos} → {max_pos}  |  Center: {center}")

print("\nMoving to CENTER...")
move(center, delay=1.5)
print(f"Position: {read_pos()}")

input("\nPress Enter to move to MIN (left)...")
move(min_pos + 50, delay=1.5)
print(f"Position: {read_pos()}")

input("Press Enter to move to MAX (right)...")
move(max_pos - 50, delay=1.5)
print(f"Position: {read_pos()}")

input("Press Enter to return to CENTER and exit...")
move(center, delay=1.5)
print(f"Position: {read_pos()}")

bus.disconnect()
print("Done.")
