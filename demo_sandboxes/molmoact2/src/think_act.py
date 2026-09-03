"""Official MolmoAct2-Think-LIBERO action path.

predict_action + adaptive depth. Matches the Think-LIBERO model card, not a
chat wrapper. Sample cameras + EEF state are the card's libero_10 / ep0 / t0.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from hf_load import load_processor

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ROOT / "weights" / "MolmoAct2-Think-LIBERO"
LOG_DIR = ROOT / "logs"

# Official card: libero_10, episode 0, frame 0.
OFFICIAL_TASK = (
    "put the white mug on the left plate and put the yellow and white mug "
    "on the right plate"
)
OFFICIAL_STATE = np.array(
    [
        -0.05338004603981972,
        0.007029631175100803,
        0.6783280968666077,
        3.1407692432403564,
        0.0017593271331861615,
        -0.08994418382644653,
        0.03878866136074066,
        -0.03878721222281456,
    ],
    dtype=np.float32,
)


def append_log(record: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"{day}.jsonl"
    record = dict(record)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
    return path


class ThinkLibero:
    def __init__(self, weights: Path | str = WEIGHTS, device: str = "cuda"):
        import torch
        from transformers import AutoModelForImageTextToText

        self.processor = load_processor(weights)
        self.model = AutoModelForImageTextToText.from_pretrained(
            str(weights),
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
        ).to(device).eval()
        self.depth_cache = None

    def act(
        self,
        third: Image.Image | np.ndarray,
        wrist: Image.Image | np.ndarray | None,
        task: str = OFFICIAL_TASK,
        state: np.ndarray | None = None,
    ) -> dict[str, Any]:
        if isinstance(third, np.ndarray):
            third = Image.fromarray(third).convert("RGB")
        images: list[Image.Image] = [third.convert("RGB")]
        if wrist is not None:
            if isinstance(wrist, np.ndarray):
                wrist = Image.fromarray(wrist).convert("RGB")
            images.append(wrist.convert("RGB"))
        if state is None:
            state = OFFICIAL_STATE
        import torch

        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
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
            depth = out.get("depth_tokens", out.get("depth_bins", out.get("depth")))
            updated = out.get("depth_update_mask", out.get("updated_cells"))
        else:
            actions = getattr(out, "actions", None) or getattr(out, "action", out)
            depth = getattr(out, "depth_bins", None) or getattr(out, "depth_tokens", None)
            updated = getattr(out, "depth_update_mask", None)
            self.depth_cache = getattr(out, "depth_cache", self.depth_cache)

        think = {
            "depth_bins": depth,
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
