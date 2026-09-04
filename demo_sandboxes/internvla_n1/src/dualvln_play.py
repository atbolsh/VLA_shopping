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
sys.path.insert(0, str(Path(__file__).resolve().parent))
WEIGHTS = ROOT / "weights" / "InternVLA-N1-DualVLN"
LOG_DIR = ROOT / "logs"
DEVICE = "cuda:0"


def _on_path() -> None:
    from patch_internnav import ensure_internnav

    ensure_internnav()
    for p in (VENDOR, VENDOR / "src" / "diffusion-policy"):
        s = str(p)
        if p.exists() and s not in sys.path:
            sys.path.insert(0, s)


def _import_realworld_agent():
    """Load InternVLAN1AsyncAgent without executing internnav.agent.__init__.

    That __init__ imports CMA/RDP/sim InternVLAN1Agent (Habitat). The official
    inference_only_demo uses the realworld class, which does not need them.
    """
    import types

    import internnav  # noqa: F401

    name = "internnav.agent"
    pkg = types.ModuleType(name)
    pkg.__path__ = [str(VENDOR / "internnav" / "agent")]
    pkg.__package__ = name
    sys.modules[name] = pkg
    from internnav.agent.internvla_n1_agent_realworld import InternVLAN1AsyncAgent

    return InternVLAN1AsyncAgent


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


def _is_flash_attn_error(exc: BaseException) -> bool:
    blob = f"{type(exc).__name__} {exc}".lower()
    return "flash" in blob and "depth_anything" not in blob


def verify_s1_weights(model, model_dir: Path) -> str:
    """Prove the S1 modules hold the checkpoint's weights, not init garbage.

    build_depthanythingv2 does load_state_dict(torch.load(.pth)) inside
    __init__. Under from_pretrained(device_map=...) the module is on the
    meta device, so that copy is a no-op (the warning wall). It does not
    matter *iff* the DualVLN shards carry model.rgb_model.* themselves —
    they do (175 keys) — and iff those actually landed. Check elementwise
    against the shard files, one probe per S1 module.
    """
    import torch
    from safetensors import safe_open

    meta = [n for n, p in model.named_parameters() if p.is_meta]
    if meta:
        raise RuntimeError(f"{len(meta)} parameters still on meta device, e.g. {meta[:3]}")
    index_path = Path(model_dir) / "model.safetensors.index.json"
    weight_map = json.loads(index_path.read_text())["weight_map"]
    prefixes = [
        "model.rgb_model.",
        "model.traj_dit.",
        "model.memory_encoder.",
        "model.rgb_resampler.",
        "model.cond_projector.",
        "model.latent_queries",
        "model.action_encoder.",
    ]
    probes = []
    for pref in prefixes:
        hit = next((k for k in sorted(weight_map) if k.startswith(pref)), None)
        if hit:
            probes.append(hit)
    live = dict(model.named_parameters())
    live.update(dict(model.named_buffers()))
    for key in probes:
        with safe_open(str(Path(model_dir) / weight_map[key]), framework="pt", device="cpu") as f:
            saved = f.get_tensor(key)
        param = live[key].detach().to("cpu")
        if not torch.equal(param, saved.to(param.dtype)):
            raise RuntimeError(f"S1 weight mismatch vs shard: {key}")
    return (
        f"S1 weights verified vs shards: {len(probes)}/{len(probes)} probes equal "
        f"({', '.join(p.removeprefix('model.').split('.')[0] for p in probes)})"
    )


def _make_agent(args: Args):
    _on_path()
    import warnings

    from patch_internnav import ensure_depth_anything

    ensure_depth_anything()
    InternVLAN1AsyncAgent = _import_realworld_agent()

    # Benign under from_pretrained(device_map=...): the in-__init__
    # DepthAnything .pth load hits meta parameters and no-ops; the real
    # rgb_model weights come from the DualVLN shards (verified after load).
    warnings.filterwarnings(
        "ignore",
        message=".*copying from a non-meta parameter in the checkpoint to a meta parameter.*",
    )
    try:
        return InternVLAN1AsyncAgent(args)
    except Exception as first:
        if not _is_flash_attn_error(first):
            raise
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
        print(verify_s1_weights(self.agent.model, Path(self.args.model_path)))
        self.agent.reset()
        print("warmup: one step on a black dummy frame (its S2 output is throwaway)")
        dummy_rgb = np.zeros((480, 640, 3), dtype=np.uint8)
        dummy_depth = np.zeros((480, 640), dtype=np.float32)
        dummy_pose = np.eye(4)
        self.agent.step(
            dummy_rgb, dummy_depth, dummy_pose, "hello", intrinsic=self.args.camera_intrinsic
        )
        self.agent.reset()
        self.agent.last_s2_idx = -100
        print("warmup done; agent state reset")

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
