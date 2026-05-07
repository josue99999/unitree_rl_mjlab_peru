# Unitree G1 — Caporal Dance Motion Tracking

Motion imitation RL for the Unitree G1 humanoid robot, trained to perform the **Caporal** dance using PPO + domain randomization. Built on top of [mjlab](https://github.com/mujocolab/mjlab.git) with MuJoCo physics.

<div align="center">
  <img src="doc/gif/caporal_sim2sim.gif" width="700"/>
  <br><em>Sim-to-sim: G1 performing Caporal in unitree_mujoco</em>
</div>

---

## Overview

This repository contains:
- PPO-based motion tracking training pipeline for the Unitree G1 (29 DoF)
- Robust domain randomization: push disturbances, friction noise, encoder bias, COM offset
- Trained checkpoint for the **Caporal** dance (46,000 iterations)
- Trained checkpoint for the **Huayno** dance
- Sim-to-sim deployment via `unitree_mujoco` + `g1_ctrl`
- ONNX export pipeline compatible with `g1_ctrl`

---

## Installation

### Requirements

- Ubuntu 22.04
- Python 3.11
- CUDA (optional, CPU also supported)

### Setup

```bash
git clone https://github.com/josue99999/unitree_rl_mjlab_peru.git
cd unitree_rl_mjlab_peru
pip install -e .
```

Install compatible physics backends:

```bash
pip install mujoco==3.5.0
pip install warp-lang==1.12.1
```

---

## Training

### Caporal (from checkpoint)

```bash
python scripts/train.py \
  Unitree-G1-Tracking-No-State-Estimation \
  --motion-file src/assets/motions/g1/caporal.npz \
  --env.scene.num-envs 512 \
  --agent.experiment-name g1_caporal \
  --agent.run-name caporal_robust \
  --init-checkpoint-file best_checkpoints/g1_caporal/model_46000.pt \
  --agent.max-iterations 500001
```

### Huayno (from scratch)

```bash
python scripts/train.py \
  Unitree-G1-Tracking-No-State-Estimation \
  --motion-file src/assets/motions/g1/huayno.npz \
  --env.scene.num-envs 512 \
  --agent.experiment-name g1_huayno \
  --agent.run-name huayno_robust \
  --agent.max-iterations 500001
```

---

## Play (visualize in MuJoCo viewer)

```bash
python scripts/play.py \
  Unitree-G1-Tracking-No-State-Estimation \
  --motion-file src/assets/motions/g1/caporal.npz \
  --checkpoint-file best_checkpoints/g1_caporal/model_46000.pt
```

Add `--video True` to record an mp4 automatically.

---

## Export ONNX (for g1_ctrl)

If you have a `.pt` checkpoint and need a `policy.onnx` compatible with `g1_ctrl`:

```bash
python scripts/export_onnx.py \
  Unitree-G1-Tracking-No-State-Estimation \
  --checkpoint-file best_checkpoints/g1_caporal/model_46000.pt \
  --motion-file src/assets/motions/g1/caporal.npz \
  --output-dir deploy/robots/g1/config/policy/mimic/caporal/exported/
```

---

## Sim-to-Sim Deployment (unitree_mujoco)

Build the required binaries first (see `simulate/` and `deploy/robots/g1/`).

**Terminal 1** — Keyboard joystick:
```bash
sudo python3 /path/to/keyboard_joystick/keyboard_joystick.py
```

**Terminal 2** — MuJoCo simulator:
```bash
cd simulate
./build/unitree_mujoco
```

**Terminal 3** — G1 controller:
```bash
cd deploy/robots/g1
./build/g1_ctrl -n lo
```

Then press **R2 + A** to stand, and **LB + A** to activate `Mimic_Caporal`.

---

## Checkpoints

| Dance    | Iterations | File                                          |
|----------|-----------|-----------------------------------------------|
| Caporal  | 46,000    | `best_checkpoints/g1_caporal/model_46000.pt`  |
| Caporal  | 63,000    | `best_checkpoints/g1_caporal/model_63000.pt`  |

Deployed ONNX (g1_ctrl compatible):
- `deploy/robots/g1/config/policy/mimic/caporal/exported/policy.onnx`
- `deploy/robots/g1/config/policy/mimic/huayno/exported/policy.onnx`

---

## Domain Randomization (robustness config)

| Parameter          | Value             |
|--------------------|-------------------|
| Push velocity x/y  | ±1.0 m/s          |
| Push interval      | 0.5 – 2.0 s       |
| Foot friction      | 0.2 – 1.5         |
| Encoder bias       | ±0.05 rad         |
| COM offset         | ±0.1 m            |
| Episode length     | 20 s              |

---

## Based on

- [unitree_rl_mjlab](https://github.com/unitreerobotics/unitree_rl_mjlab) — original repo
- [BeyondMimic](https://beyondmimic.github.io/) — motion tracking approach
- [mjlab](https://github.com/mujocolab/mjlab.git) — RL framework
