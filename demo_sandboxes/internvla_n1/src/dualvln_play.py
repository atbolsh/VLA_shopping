"""Official InternVLAN1AsyncAgent path (inference_only_demo.ipynb).

DualVLN is hardcoded to cuda:0. Do not invent a new policy.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "InternNav"
WEIGHTS = ROOT / "weights" / "InternVLA-N1-DualVLN"
LOG_DIR = ROOT / "logs"
DEVICE = "cuda:0"


def _on_path() -> None:
    for p in (VENDOR, VENDOR / "src" / "diffusion-policy"):
        s = str(p)
        if p.exists() and s not in sys.path:
            sys.path.insert(0, s)


def append_log(record: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"{day}.jsonl"
    record = dict(record)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
    return path


class Args:
    """Same fields as the official notebook's Args."""

    def __init__(self, model_path: str):
        self.device = DEVICE
        self.model_path = model_path
        self.resize_w = 384
        self.resize_h = 384
        self.num_history = 8
        self.camera_intrinsic = np.array(
            [
                [386.5, 0.0, 328.9, 0.0],
                [0.0, 386.5, 244.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
        self.plan_step_gap = 4


def _make_agent(args: Args):
    _on_path()
    from internnav.agent.internvla_n1_agent_realworld import InternVLAN1AsyncAgent

    try:
        return InternVLAN1AsyncAgent(args)
    except Exception as first:
        print("flash_attention_2 failed, retrying with sdpa (official notebook allows this):", first)
        import internnav.model.basemodel.internvla_n1.internvla_n1 as n1

        orig = n1.InternVLAN1ForCausalLM.from_pretrained

        def _fp(*a, **k):
            k["attn_implementation"] = "sdpa"
            return orig(*a, **k)

        n1.InternVLAN1ForCausalLM.from_pretrained = staticmethod(_fp)  # type: ignore[method-assign]
        return InternVLAN1AsyncAgent(args)


class DualVlnPlay:
    def __init__(self, model_path: Path | str = WEIGHTS):
        self.args = Args(str(model_path))
        self.agent = _make_agent(self.args)
        self.agent.reset()
        dummy_rgb = np.zeros((480, 640, 3), dtype=np.uint8)
        dummy_depth = np.zeros((480, 640), dtype=np.float32)
        dummy_pose = np.eye(4)
        self.agent.step(
            dummy_rgb, dummy_depth, dummy_pose, "hello", intrinsic=self.args.camera_intrinsic
        )
        self.agent.reset()
        self.agent.last_s2_idx = -100

    def step(
        self,
        rgb: np.ndarray,
        depth: np.ndarray | None,
        pose: np.ndarray | None,
        instruction: str,
    ) -> dict[str, Any]:
        if depth is None:
            depth = np.zeros(rgb.shape[:2], dtype=np.float32)
        if pose is None:
            pose = np.eye(4)
        before = self.agent.episode_idx
        last_s2 = self.agent.last_s2_idx
        out = self.agent.step(
            rgb, depth, pose, instruction, intrinsic=self.args.camera_intrinsic
        )
        s2_ran = (self.agent.last_s2_idx != last_s2) or (self.agent.episode_idx == before + 1)
        pixel = getattr(out, "output_pixel", None)
        traj = getattr(out, "output_trajectory", None)
        action = getattr(out, "output_action", None)
        llm = self.agent.llm_output
        vis = self._annotate(rgb, llm, traj, pixel)
        frame_path = LOG_DIR / "last_frame.png"
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        Image.fromarray(vis).save(frame_path)
        rec = {
            "sandbox": "internvla_n1",
            "turn": "dualvln_step",
            "instruction": instruction,
            "reply": llm,
            "think": {
                "llm_output": llm,
                "pixel_goal": pixel,
                "s2_ran": bool(s2_ran),
                "plan_step_gap": self.args.plan_step_gap,
                "episode_idx": self.agent.episode_idx,
            },
            "action": action,
            "trajectory": traj,
            "frame": str(frame_path),
        }
        append_log(rec)
        rec["vis"] = vis
        return rec

    def _annotate(self, rgb, llm_output, trajectory, pixel_goal) -> np.ndarray:
        image = np.array(rgb)
        if pixel_goal is not None and len(pixel_goal) >= 2:
            y, x = int(pixel_goal[0]), int(pixel_goal[1])
            if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
                image[max(0, y - 3) : y + 4, max(0, x - 3) : x + 4] = (255, 0, 0)
        return image
