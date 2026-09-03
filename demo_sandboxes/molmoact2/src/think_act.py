"""Official MolmoAct2-Think-LIBERO action path.

predict_action + adaptive depth. Matches the Think-LIBERO model card, not a
chat wrapper. Sample cameras + EEF state are the card's libero_10 / ep0 / t0.

The caution sentence is injected into the official ``The task is to {task}``
slot. ``normalize_language=False`` so it is not lowercased / stripped.
"""

from __future__ import annotations

import json
import re
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
INJECT = (
    "if an instruction is unclear, ask a follow-up before committing; "
    "keep the arm still until you are certain"
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

# Brackets stay visible. Payload values (depth_N / action_N / state_N) become █.
_KEEP = {
    "<depth_start>",
    "<depth_end>",
    "<depth_output>",
    "<action_start>",
    "<action_end>",
    "<action_output>",
    "<state_start>",
    "<state_end>",
    "<setup_start>",
    "<setup_end>",
    "<control_start>",
    "<control_end>",
    "<|im_start|>",
    "<|im_end|>",
    "<|image|>",
    "<|endoftext|>",
}
_PAYLOAD = re.compile(r"^<(?:depth|action|state)_\d+>$")
_BOX = "█"


def composed_task(base: str = OFFICIAL_TASK, inject: str = INJECT) -> str:
    inject = (inject or "").strip()
    if not inject:
        return base
    if base.endswith("."):
        return f"{base} {inject}"
    return f"{base}. {inject}"


def _maps_to_unicode(s: str | None) -> bool:
    if not s:
        return False
    return not all(ch == "\ufffd" for ch in s)


def _token_name(tokenizer, tid: int) -> str:
    name = tokenizer.convert_ids_to_tokens(tid)
    if isinstance(name, bytes):
        try:
            name = name.decode("utf-8")
        except UnicodeDecodeError:
            name = ""
    if not isinstance(name, str):
        name = ""
    return name.lstrip("Ġ▁")


def _token_text(tokenizer, tid: int) -> str:
    chunk = tokenizer.decode(
        [tid], skip_special_tokens=False, clean_up_tokenization_spaces=False
    )
    if _maps_to_unicode(chunk):
        return chunk
    name = _token_name(tokenizer, tid)
    if _maps_to_unicode(name):
        return name
    return f"<id:{tid}>"


def flatten_token_ids(ids) -> list[int]:
    if ids is None:
        return []
    if hasattr(ids, "detach"):
        tensor = ids.detach().cpu()
        if tensor.ndim == 0:
            return [int(tensor.item())]
        if tensor.ndim >= 2:
            tensor = tensor[0]
        return [int(x) for x in tensor.reshape(-1).tolist()]
    if isinstance(ids, (list, tuple)):
        if ids and isinstance(ids[0], (list, tuple)):
            return [int(x) for x in ids[0]]
        return [int(x) for x in ids]
    return [int(ids)]


def format_generated(tokenizer, ids) -> dict[str, Any]:
    """Full decode + English-ish line with depth/action payloads boxed."""
    flat = flatten_token_ids(ids)
    names: list[str] = []
    pieces: list[str] = []
    for tid in flat:
        name = _token_name(tokenizer, tid) or f"<id:{tid}>"
        names.append(name)
        if _PAYLOAD.match(name):
            pieces.append(_BOX)
        elif name in _KEEP:
            pieces.append(name)
        else:
            pieces.append(_token_text(tokenizer, tid))
    full = ""
    if flat:
        full = tokenizer.decode(
            flat, skip_special_tokens=False, clean_up_tokenization_spaces=False
        )
    return {
        "token_ids": flat,
        "token_names": names,
        "full_text": full,
        "boxed": "".join(pieces),
    }


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
        task: str | None = None,
        inject: str = INJECT,
        state: np.ndarray | None = None,
        normalize_language: bool = False,
    ) -> dict[str, Any]:
        if task is None:
            task = composed_task(OFFICIAL_TASK, inject)
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
                normalize_language=normalize_language,
                enable_cuda_graph=False,
            )
        generated = None
        if isinstance(out, dict):
            self.depth_cache = out.get("depth_cache", self.depth_cache)
            actions = out.get("actions", out.get("action"))
            depth = out.get("depth_tokens", out.get("depth_bins", out.get("depth")))
            updated = out.get("depth_update_mask", out.get("updated_cells"))
            generated = out.get("generated_token_ids")
        else:
            actions = getattr(out, "actions", None) or getattr(out, "action", out)
            depth = getattr(out, "depth_bins", None) or getattr(out, "depth_tokens", None)
            updated = getattr(out, "depth_update_mask", None)
            generated = getattr(out, "generated_token_ids", None)
            self.depth_cache = getattr(out, "depth_cache", self.depth_cache)

        shown = format_generated(self.processor.tokenizer, generated)
        rec = {
            "sandbox": "molmoact2",
            "turn": "act_think_inject",
            "task": task,
            "inject": inject,
            "normalize_language": normalize_language,
            "full_text": shown["full_text"],
            "boxed": shown["boxed"],
            "token_names": shown["token_names"],
            "token_ids": shown["token_ids"],
            "depth_bins": depth,
            "updated_cells": updated,
            "actions": actions,
            "reply": shown["boxed"] or shown["full_text"] or f"actions={actions}",
            "think": {
                "full_text": shown["full_text"],
                "boxed": shown["boxed"],
                "depth_bins": depth,
                "updated_cells": updated,
            },
        }
        append_log(
            {
                k: rec[k]
                for k in (
                    "sandbox",
                    "turn",
                    "task",
                    "inject",
                    "full_text",
                    "boxed",
                    "reply",
                )
            }
        )
        return rec
