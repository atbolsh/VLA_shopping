"""Official MolmoAct2-Think-LIBERO action path.

predict_action + adaptive depth. Not a chat wrapper.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ROOT / "weights" / "MolmoAct2-Think-LIBERO"
LOG_DIR = ROOT / "logs"


def append_log(record: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"{day}.jsonl"
    record = dict(record)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
    return path


def _to_np(im: Image.Image | np.ndarray) -> np.ndarray:
    if isinstance(im, Image.Image):
        return np.asarray(im.convert("RGB"))
    return np.asarray(im)


class ThinkLibero:
    def __init__(self, weights: Path | str = WEIGHTS, device: str = "cuda"):
        import torch
        from transformers import AutoModel, AutoProcessor

        self.processor = AutoProcessor.from_pretrained(
            str(weights), trust_remote_code=True
        )
        self.model = AutoModel.from_pretrained(
            str(weights),
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            device_map=device,
        )
        self.model.eval()
        self.depth_cache = None

    def act(
        self,
        third: Image.Image | np.ndarray,
        wrist: Image.Image | np.ndarray | None,
        task: str,
        state: np.ndarray | None = None,
    ) -> dict[str, Any]:
        images = [_to_np(third)]
        if wrist is not None:
            images.append(_to_np(wrist))
        if state is None:
            # LIBERO EEF + gripper placeholder; replace with env state in closed loop.
            state = np.zeros((8,), dtype=np.float32)
        out = self.model.predict_action(
            processor=self.processor,
            images=images,
            task=task,
            state=state,
            norm_tag="libero",
            inference_action_mode="continuous",
            enable_depth_reasoning=True,
            enable_adaptive_depth=True,
            depth_cache=self.depth_cache,
            num_steps=10,
            normalize_language=True,
            enable_cuda_graph=False,
        )
        if isinstance(out, dict):
            self.depth_cache = out.get("depth_cache", self.depth_cache)
            actions = out.get("actions", out.get("action"))
            depth = out.get("depth_tokens", out.get("depth"))
            updated = out.get("depth_update_mask", out.get("updated_cells"))
        else:
            actions = getattr(out, "actions", None) or getattr(out, "action", out)
            depth = getattr(out, "depth_tokens", None)
            updated = getattr(out, "depth_update_mask", None)
            self.depth_cache = getattr(out, "depth_cache", self.depth_cache)

        think = {
            "depth_tokens": depth,
            "updated_cells": updated,
            "task_prompt_style": (
                f"The task is to {task}. ... first predict the depth map of the "
                "main image and then predict the action"
            ),
        }
        rec = {
            "sandbox": "molmoact2",
            "turn": "act_think",
            "task": task,
            "reply": f"actions={actions}",
            "think": think,
            "actions": actions,
        }
        append_log(rec)
        return rec
