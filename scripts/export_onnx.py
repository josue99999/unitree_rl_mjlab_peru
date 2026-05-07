"""Export policy.onnx (g1_ctrl-compatible format) from a .pt checkpoint."""

import sys
from dataclasses import asdict

import tyro

import mjlab
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.tasks.registry import list_tasks, load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.tasks.tracking.mdp import MotionCommandCfg
from mjlab.utils.torch import configure_torch_backends

import src.tasks  # noqa: F401


def main():
    import mjlab.tasks  # noqa: F401

    all_tasks = list_tasks()
    chosen_task, remaining_args = tyro.cli(
        tyro.extras.literal_type_from_choices(all_tasks),
        add_help=False,
        return_unknown_args=True,
        config=mjlab.TYRO_FLAGS,
    )

    from dataclasses import dataclass

    @dataclass(frozen=True)
    class ExportConfig:
        checkpoint_file: str
        output_dir: str
        motion_file: str | None = None

    cfg = tyro.cli(
        ExportConfig,
        args=remaining_args,
        prog=sys.argv[0] + f" {chosen_task}",
        config=mjlab.TYRO_FLAGS,
    )

    configure_torch_backends()

    env_cfg = load_env_cfg(chosen_task, play=True)
    agent_cfg = load_rl_cfg(chosen_task)

    is_tracking = "motion" in env_cfg.commands and isinstance(
        env_cfg.commands["motion"], MotionCommandCfg
    )
    if is_tracking:
        if not cfg.motion_file:
            raise ValueError("--motion-file required for tracking tasks")
        env_cfg.commands["motion"].motion_file = cfg.motion_file

    device = "cpu"
    env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
    env = RslRlVecEnvWrapper(env)

    runner_cls = load_runner_cls(chosen_task) or MjlabOnPolicyRunner
    runner = runner_cls(env, asdict(agent_cfg), device=device)
    runner.load(cfg.checkpoint_file, load_cfg={"actor": True}, strict=True, map_location=device)

    # Export compatible policy.onnx (obs-only, no time_step — for g1_ctrl)
    runner.export_policy_to_onnx(cfg.output_dir, "policy.onnx")
    print(f"[INFO] Exported compatible policy.onnx to: {cfg.output_dir}/policy.onnx")

    env.close()


if __name__ == "__main__":
    main()
