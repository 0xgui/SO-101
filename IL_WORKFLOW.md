# Imitation Learning (IL) Workflow — SO-101

This guide documents the end-to-end pipeline for teaching the SO-101 arm tasks via imitation learning using LeRobot.

**Prerequisites:**
- SO-101 follower + leader arms assembled, calibrated, and connected
- LeRobot installed in a conda environment (`lerobot_new` recommended)
- Hugging Face account with CLI login (`hf auth login`)
- One or more cameras (USB webcams tested)

---

## 1. Environment Setup (One-Time)

### 1.1 Create conda env with Python 3.12

LeRobot requires Python >=3.12.

```bash
conda create -n lerobot_new python=3.12 -y
conda activate lerobot_new
```

### 1.2 Install LeRobot

```bash
cd /path/to/lerobot  # clone from https://github.com/huggingface/lerobot
pip install -e ".[feetech,dataset,train]"
```

### 1.3 Install PyTorch with CUDA 12.8 (Required for RTX 50-series / Blackwell)

If you have an RTX 5070 Ti, 5090, or other Blackwell (sm_120) GPU, you **must** use PyTorch with CUDA 12.8:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

Verify with:
```bash
python3 -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.get_device_name(0))"
# Expected: 2.11.0+cu128, CUDA 12.8, your GPU name
```

### 1.4 Hugging Face CLI

```bash
pip install huggingface-hub[cli]
hf auth login --token <YOUR_WRITE_TOKEN> --add-to-git-credential
```

Set your username for commands below:
```bash
export HF_USER=$(NO_COLOR=1 hf auth whoami | head -1 | awk '{print $NF}')
```

---

## 2. Teleoperate with Cameras

### Single camera
```bash
lerobot-teleoperate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=<FOLLOWER_ID> \
    --robot.cameras="{ front: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}}" \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM1 \
    --teleop.id=<LEADER_ID> \
    --display_data=true
```

### Dual camera (front + side)
```bash
lerobot-teleoperate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=<FOLLOWER_ID> \
    --robot.cameras="{ front: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30, rotation: ROTATE_180}, side: {type: opencv, index_or_path: /dev/video2, width: 640, height: 480, fps: 30}}" \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM1 \
    --teleop.id=<LEADER_ID> \
    --display_data=true
```

**Notes:**
- `rotation: ROTATE_180` flips an upside-down camera.
- Supported rotations: `NO_ROTATION`, `ROTATE_90`, `ROTATE_180`, `ROTATE_270`.
- If you see a calibration mismatch prompt on startup, **press Enter** to load the saved calibration file.

---

## 3. Record a Dataset

`lerobot-record` is the same as teleop, but it saves every frame and action.

```bash
lerobot-record \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=<FOLLOWER_ID> \
    --robot.cameras="{ front: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}, side: {type: opencv, index_or_path: /dev/video2, width: 640, height: 480, fps: 30}}" \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM1 \
    --teleop.id=<LEADER_ID> \
    --display_data=true \
    --dataset.repo_id=${HF_USER}/<DATASET_NAME> \
    --dataset.num_episodes=5 \
    --dataset.single_task="Pick up the orange boat and place it in the bin" \
    --dataset.streaming_encoding=true \
    --dataset.encoder_threads=2 \
    --dataset.reset_time_s=10
```

### Recording workflow
1. Press **Enter** → starts recording episode
2. Teleoperate the task
3. Press **Enter** → finishes episode and starts encoding
4. Reset the scene (move objects/robot back to start)
5. Wait `reset_time_s` (10s in example above) or press Enter again
6. Repeat for all episodes

### Camera resolution gotcha
Many USB webcams **only support 640×480 at 30 fps** and will reject other settings. If you get errors like:
```
failed to set capture_width=480 (actual_width=640)
failed to set fps=15 (actual_fps=30)
```
Just use `width=640, height=480, fps=30`. The recording loop may warn about running slower than 30 Hz, but it still works.

### Re-recording the same dataset name
LeRobot caches datasets locally. If you need to re-record, clear the cache first:
```bash
rm -rf ~/.cache/huggingface/lerobot/${HF_USER}/<DATASET_NAME>
```

---

## 4. Train a Policy

### ACT (Action Chunking with Transformers)

```bash
lerobot-train \
    --dataset.repo_id=${HF_USER}/<DATASET_NAME> \
    --policy.type=act \
    --output_dir=outputs/train/act_<DATASET_NAME> \
    --job_name=act_<DATASET_NAME> \
    --policy.device=cuda \
    --wandb.enable=false \
    --policy.repo_id=${HF_USER}/act_<DATASET_NAME>_policy
```

**Training details:**
- 100K steps default (~2–4 hours on an RTX 5070 Ti)
- Checkpoints save every 20K steps to `outputs/train/.../checkpoints/`
- Final policy pushes to Hugging Face Hub at `--policy.repo_id`

### Weights & Biases (optional)
To track training curves with W&B:
```bash
wandb login
```
Then set `--wandb.enable=true`.

### CUDA compatibility check
If you see:
```
RuntimeError: CUDA error: no kernel image is available for execution on the device
```
Your PyTorch does not support your GPU architecture. Follow Section 1.3 to install `cu128`.

### Install gotchas
If `lerobot-train` fails with missing imports (`datasets`, etc.), reinstall with extras:
```bash
pip install -e ".[feetech,dataset,train]"
```

---

## 5. Evaluate (Run Policy Autonomously)

The leader arm is **not used** here. The robot uses the trained policy to decide actions from camera images.

```bash
lerobot-record \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=<FOLLOWER_ID> \
    --robot.cameras="{ front: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}, side: {type: opencv, index_or_path: /dev/video2, width: 640, height: 480, fps: 30}}" \
    --display_data=true \
    --dataset.repo_id=${HF_USER}/eval_<DATASET_NAME> \
    --dataset.single_task="Pick up the orange boat and place it in the bin" \
    --control.policy.path=outputs/train/act_<DATASET_NAME>/checkpoints/last/pretrained_model
```

You can also use a Hub checkpoint:
```bash
--control.policy.path=${HF_USER}/act_<DATASET_NAME>_policy
```

---

## Quick Reference: Full Pipeline

```bash
# 1. Activate env
conda activate lerobot_new

# 2. Record
lerobot-record \
    --robot.type=so101_follower --robot.port=/dev/ttyACM0 --robot.id=my_robot \
    --robot.cameras="{ front: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}}" \
    --teleop.type=so101_leader --teleop.port=/dev/ttyACM1 --teleop.id=my_leader \
    --dataset.repo_id=${HF_USER}/my_task --dataset.num_episodes=5 \
    --dataset.single_task="My task description" --dataset.reset_time_s=10

# 3. Train
lerobot-train \
    --dataset.repo_id=${HF_USER}/my_task \
    --policy.type=act \
    --output_dir=outputs/train/act_my_task \
    --job_name=act_my_task \
    --policy.device=cuda \
    --wandb.enable=false \
    --policy.repo_id=${HF_USER}/act_my_task_policy

# 4. Evaluate
lerobot-record \
    --robot.type=so101_follower --robot.port=/dev/ttyACM0 --robot.id=my_robot \
    --robot.cameras="{ front: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}}" \
    --dataset.repo_id=${HF_USER}/eval_my_task \
    --control.policy.path=outputs/train/act_my_task/checkpoints/last/pretrained_model
```

---

## References

- [LeRobot IL Robots Tutorial](https://huggingface.co/docs/lerobot/il_robots)
- [LeRobot SO-101 Guide](https://huggingface.co/docs/lerobot/so101)
- [SO-ARM100 GitHub](https://github.com/TheRobotStudio/SO-ARM100)
