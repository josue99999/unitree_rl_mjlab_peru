# G1 Caporal Motion Tracking

This note contains the minimal commands needed to reproduce the Caporal motion tracking setup, train it on a server, test it in Python, and run the exported policy in simulation or on a Unitree G1.

## 1. Clone

```bash
git clone https://github.com/josue99999/unitree_rl_mjlab.git
cd unitree_rl_mjlab
```

Create and activate the Python environment used for training, then install the repo and dependencies following the main project setup.

## 2. Important Files

```text
src/assets/motions/g1/caporal.npz
checkpoints/g1_caporal/model_25500.pt
deploy/robots/g1/config/policy/mimic/caporal/params/caporal.npz
deploy/robots/g1/config/policy/mimic/caporal/exported/policy.onnx
deploy/robots/g1/config/policy/mimic/caporal/params/deploy.yaml
```

The caporal deploy state is registered in:

```text
deploy/robots/g1/config/config.yaml
```

The joystick transition is:

```text
Velocity -> Mimic_Caporal: LB + A
```

## 3. Train From Scratch

```bash
python scripts/train.py Unitree-G1-Tracking-No-State-Estimation \
  --motion-file src/assets/motions/g1/caporal.npz \
  --env.scene.num-envs 4096 \
  --agent.experiment-name g1_caporal
```

Use fewer environments if the GPU memory is limited:

```bash
python scripts/train.py Unitree-G1-Tracking-No-State-Estimation \
  --motion-file src/assets/motions/g1/caporal.npz \
  --env.scene.num-envs 512 \
  --agent.experiment-name g1_caporal
```

## 4. Train From Zero, Initialized From Checkpoint

This starts a new run at iteration `0`, but initializes actor and critic weights from the checkpoint. The optimizer and iteration counter are not restored.

```bash
python scripts/train.py Unitree-G1-Tracking-No-State-Estimation \
  --motion-file src/assets/motions/g1/caporal.npz \
  --env.scene.num-envs 4096 \
  --agent.experiment-name g1_caporal \
  --agent.run-name fresh_init_from_25500 \
  --init-checkpoint-file checkpoints/g1_caporal/model_25500.pt
```

## 5. Resume An Interrupted Run

This continues a previous run, including checkpoint iteration and optimizer state.

```bash
python scripts/train.py Unitree-G1-Tracking-No-State-Estimation \
  --motion-file src/assets/motions/g1/caporal.npz \
  --env.scene.num-envs 512 \
  --agent.experiment-name g1_caporal \
  --agent.resume True \
  --agent.load-run 2026-05-03_01-30-52 \
  --agent.load-checkpoint model_25500.pt
```

## 6. Play In Python

```bash
python scripts/play.py Unitree-G1-Tracking-No-State-Estimation \
  --motion-file src/assets/motions/g1/caporal.npz \
  --checkpoint-file checkpoints/g1_caporal/model_25500.pt \
  --num-envs 1 \
  --viewer native
```

If there is no display:

```bash
python scripts/play.py Unitree-G1-Tracking-No-State-Estimation \
  --motion-file src/assets/motions/g1/caporal.npz \
  --checkpoint-file checkpoints/g1_caporal/model_25500.pt \
  --num-envs 1 \
  --viewer viser
```

## 7. Build Deploy Controller

```bash
cd deploy/robots/g1
mkdir -p build
cd build
cmake ..
make -j$(nproc)
```

## 8. Simulation Deploy Without A Physical Gamepad

Terminal 1, virtual joystick:

```bash
sudo python3 /home/josu/unitree_sim2real_ws/keyboard_joystick/keyboard_joystick.py
```

Terminal 2, Unitree MuJoCo:

```bash
cd /home/josu/unitree_sim2real_ws/unitree_rl_mjlab/simulate
./build/unitree_mujoco
```

Terminal 3, G1 controller:

```bash
cd /home/josu/unitree_sim2real_ws/unitree_rl_mjlab/deploy/robots/g1
./build/g1_ctrl -n lo
```

Keyboard sequence in Terminal 1:

```text
1 -> FixStand
2 -> Velocity
4 -> Mimic_Caporal
0 -> Passive
```

## 9. Real Robot Deploy

Connect the PC to the robot by Ethernet, then set a static IP on the PC interface. Replace `enp5s0` with the real Ethernet interface name.

```bash
ip -br link
ip -br addr

IFACE=enp5s0
sudo ip link set "$IFACE" up
sudo ip addr flush dev "$IFACE"
sudo ip addr add 192.168.123.222/24 dev "$IFACE"
ip addr show "$IFACE"
```

Robot preparation:

```text
1. Power on the G1.
2. Wait until it is in zero-torque/suspended state.
3. Press L2 + R2 on the Unitree controller to enter debug mode.
4. Keep enough free space around the robot.
```

Run the controller:

```bash
cd /home/josu/unitree_sim2real_ws/unitree_rl_mjlab/deploy/robots/g1
./build/g1_ctrl -n enp5s0
```

Controller sequence:

```text
L2 + Up -> FixStand
R2 + A  -> Velocity
LB + A  -> Mimic_Caporal
LT + B  -> Passive
```

