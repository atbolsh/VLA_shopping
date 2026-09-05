"""WidowX / Bridge visual-matching env (SimplerEnv).

EO-1 and ECoT-OpenVLA were both trained on Bridge. This is that table, not the
demo JPEGs. Install once: ``bash setup_simpler.sh`` in the sandbox venv.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

WIDOWX_TASKS = (
    "widowx_carrot_on_plate",
    "widowx_spoon_on_towel",
    "widowx_stack_cube",
    "widowx_put_eggplant_in_basket",
)
DEFAULT_TASK = "widowx_carrot_on_plate"
BRIDGE_IMAGE_SIZE = (256, 256)

# EE pose in Bridge was relative to a top-down pose, not the robot base.
# https://github.com/EO-Robotics/EO1/blob/main/experiments/3_simpler/simpler_env/eo/eo_model.py
_DEFAULT_ROT = np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]])


def _quat2mat(q: np.ndarray) -> np.ndarray:
    w, x, y, z = q
    nq = w * w + x * x + y * y + z * z
    if nq < 1e-12:
        return np.eye(3)
    s = 2.0 / nq
    X, Y, Z = x * s, y * s, z * s
    wX, wY, wZ = w * X, w * Y, w * Z
    xX, xY, xZ = x * X, x * Y, x * Z
    yY, yZ, zZ = y * Y, y * Z, z * Z
    return np.array(
        [
            [1.0 - (yY + zZ), xY - wZ, xZ + wY],
            [xY + wZ, 1.0 - (xX + zZ), yZ - wX],
            [xZ - wY, yZ + wX, 1.0 - (xX + yY)],
        ]
    )


def _mat2euler(mat: np.ndarray) -> tuple[float, float, float]:
    """sxyz, copied from EO-1 geometry.py (transforms3d)."""
    m = np.asarray(mat, dtype=np.float64)[:3, :3]
    cy = math.sqrt(m[0, 0] * m[0, 0] + m[1, 0] * m[1, 0])
    if cy > 1e-14:
        ax = math.atan2(m[2, 1], m[2, 2])
        ay = math.atan2(-m[2, 0], cy)
        az = math.atan2(m[1, 0], m[0, 0])
    else:
        ax = math.atan2(-m[1, 2], m[1, 1])
        ay = math.atan2(-m[2, 0], cy)
        az = 0.0
    return ax, ay, az


def preprocess_widowx_state(eef_pos: np.ndarray) -> np.ndarray:
    """xyz + rpy (Bridge top-down) + pad + gripper openness. Official EO-1."""
    proprio = np.asarray(eef_pos, dtype=np.float64).reshape(-1)
    if proprio.shape[0] < 8:
        raise ValueError(f"eef_pos expected 8 values, got {proprio.shape}")
    rm = _quat2mat(proprio[3:7])
    rpy = np.array(_mat2euler(rm @ _DEFAULT_ROT.T), dtype=np.float32)
    return np.concatenate([proprio[:3], rpy, [0.0], [float(proprio[7])]]).astype(np.float32)


def bridge7_to_simpler(raw: np.ndarray, action_scale: float = 1.0) -> np.ndarray:
    """Bridge 7 (xyz, rpy, gripper[0,1]) → SimplerEnv 7 (xyz, axangle, gripper ±1)."""
    from transforms3d.euler import euler2axangle

    raw = np.asarray(raw, dtype=np.float64).reshape(-1)
    world = raw[:3] * action_scale
    ax, ang = euler2axangle(float(raw[3]), float(raw[4]), float(raw[5]))
    rot = np.asarray(ax) * float(ang) * action_scale
    grip = 2.0 * (float(raw[6]) > 0.5) - 1.0
    return np.concatenate([world, rot, [grip]]).astype(np.float32)


def _resize_rgb(image: np.ndarray, size: tuple[int, int] = BRIDGE_IMAGE_SIZE) -> np.ndarray:
    from PIL import Image

    if image.shape[0] == size[1] and image.shape[1] == size[0]:
        return np.asarray(image)
    return np.asarray(Image.fromarray(image).resize(size, Image.BILINEAR))


def _image_from_obs(env, obs: dict) -> np.ndarray:
    from simpler_env.utils.env.observation_utils import get_image_from_maniskill2_obs_dict

    rgb = get_image_from_maniskill2_obs_dict(env, obs)
    return np.asarray(rgb)


def _eef_pos_from_obs(env, obs: dict) -> np.ndarray:
    extra = obs.get("extra") or {}
    agent = obs.get("agent") or {}
    if "eef_pos" in extra:
        p = np.asarray(extra["eef_pos"], dtype=np.float64).reshape(-1)
        if p.size >= 8:
            return p[:8]
    if "eef_pos" in agent:
        p = np.asarray(agent["eef_pos"], dtype=np.float64).reshape(-1)
        if p.size >= 8:
            return p[:8]
    tcp = extra.get("tcp_pose")
    if tcp is None:
        tcp = agent.get("tcp_pose")
    if tcp is not None:
        pose = np.asarray(tcp, dtype=np.float64).reshape(-1)
        grip = extra.get("gripper_width", extra.get("gripper", agent.get("gripper", 1.0)))
        g = float(np.asarray(grip).reshape(-1)[0])
        if pose.size >= 7:
            return np.concatenate([pose[:7], [g]])
    tcp_obj = getattr(getattr(env, "agent", None), "tcp", None)
    if tcp_obj is not None and hasattr(tcp_obj, "pose"):
        pose = tcp_obj.pose
        xyz = np.asarray(pose.p, dtype=np.float64).reshape(-1)
        quat = np.asarray(pose.q, dtype=np.float64).reshape(-1)
        qpos = np.asarray(env.agent.robot.get_qpos()).reshape(-1)
        grip = float(qpos[-1]) if qpos.size else 1.0
        return np.concatenate([xyz[:3], quat[:4], [grip]])
    raise RuntimeError("Could not read WidowX eef_pos from SimplerEnv observation.")


class WidowXBridgeEnv:
    """Closed-loop WidowX table. ``step_bridge7`` takes an unnormalized Bridge action."""

    def __init__(self, task: str = DEFAULT_TASK):
        if task not in WIDOWX_TASKS:
            raise ValueError(f"task must be one of {WIDOWX_TASKS}")
        try:
            import simpler_env
        except ImportError as exc:
            raise ImportError(
                "SimplerEnv is not installed. In this sandbox venv: bash setup_simpler.sh"
            ) from exc
        self.task = task
        self.env = simpler_env.make(task)
        self.obs: dict[str, Any] | None = None
        self.instruction = ""
        self.reward = 0.0
        self.done = False
        self.truncated = False
        self.info: dict[str, Any] = {}
        self.steps = 0
        self.reset()

    def reset(self, seed: int | None = None) -> np.ndarray:
        kwargs = {}
        if seed is not None:
            kwargs["seed"] = seed
        out = self.env.reset(**kwargs)
        self.obs = out[0] if isinstance(out, tuple) else out
        try:
            self.instruction = str(self.env.get_language_instruction() or "")
        except Exception:  # noqa: BLE001
            self.instruction = {
                "widowx_carrot_on_plate": "put the carrot on the plate",
                "widowx_spoon_on_towel": "put the spoon on the towel",
                "widowx_stack_cube": "stack the green cube on the yellow cube",
                "widowx_put_eggplant_in_basket": "put the eggplant in the basket",
            }.get(self.task, self.task.replace("_", " "))
        self.reward = 0.0
        self.done = False
        self.truncated = False
        self.info = {}
        self.steps = 0
        return self.image

    @property
    def image(self) -> np.ndarray:
        assert self.obs is not None
        return _resize_rgb(_image_from_obs(self.env, self.obs))

    @property
    def state(self) -> np.ndarray:
        assert self.obs is not None
        return preprocess_widowx_state(_eef_pos_from_obs(self.env, self.obs))

    def step_bridge7(self, raw7: np.ndarray, action_scale: float = 1.0) -> np.ndarray:
        action = bridge7_to_simpler(raw7, action_scale=action_scale)
        out = self.env.step(action)
        if len(out) == 5:
            self.obs, self.reward, terminated, truncated, self.info = out
            self.done = bool(terminated)
            self.truncated = bool(truncated)
        else:
            self.obs, self.reward, done, self.info = out
            self.done = bool(done)
            self.truncated = False
        self.steps += 1
        return self.image
