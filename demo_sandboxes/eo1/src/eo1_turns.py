"""Official EO-1 unified generate: text AND actions from the same 3B.

HF card: ``processor.generate(model, batch)`` -> ``output.text``, ``output.action``.
``select_action`` is act-only. ``model.generate`` is reason-only. Use generate.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
WEIGHTS = ROOT / "weights" / "EO-1-3B"
_WORD = re.compile(r"[A-Za-z]{2,}")


def append_log(record: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"{day}.jsonl"
    record = dict(record)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
    return path


def mouth_verdict(text: str) -> str:
    words = _WORD.findall(text or "")
    if len(set(w.lower() for w in words)) >= 4:
        return "usable"
    if (text or "").strip():
        return "garbage"
    return "empty"


OFFICIAL_TASK = (
    "You are a helpful physical agent equipped with both reasoning and robotic control. "
    "You see the Tic-Tac-Toe board, think strategically, act logically, and block threats."
)


class EO1Play:
    def __init__(self, weights: Path | str = WEIGHTS, device: str = "cuda"):
        import torch
        from transformers import AutoModel, AutoProcessor

        self.weights = Path(weights)
        self.device = device
        self.processor = AutoProcessor.from_pretrained(str(self.weights), trust_remote_code=True)
        self.model = AutoModel.from_pretrained(
            str(self.weights),
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
        ).eval().to(device)

    def generate(self, image, wrist, task: str | None = None, state=None) -> dict[str, Any]:
        import numpy as np
        import torch
        from PIL import Image

        if not isinstance(image, Image.Image):
            image = Image.open(image).convert("RGB")
        if wrist is not None and not isinstance(wrist, Image.Image):
            wrist = Image.open(wrist).convert("RGB")
        if wrist is None:
            wrist = image
        if state is None:
            state = np.zeros(8, dtype=np.float32)
        task = task or OFFICIAL_TASK
        batch = {
            "observation.images.image": [image],
            "observation.images.wrist_image": [wrist],
            "observation.state": [state],
            "task": [task],
        }
        text = ""
        action = None
        path_used = "processor.generate"
        try:
            with torch.inference_mode():
                out = self.processor.generate(self.model, batch)
            text = getattr(out, "text", None) or ""
            if isinstance(text, (list, tuple)):
                text = text[0] if text else ""
            action = getattr(out, "action", None)
            if action is not None and hasattr(action, "detach"):
                action = action.detach().cpu().numpy()
        except Exception as exc:  # noqa: BLE001
            path_used = f"processor.generate FAILED: {type(exc).__name__}: {exc}"
            # Official fallback: reason-only generate on the SAME weights.
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": task},
                    ],
                }
            ]
            inputs = self.processor.apply_chat_template(
                messages, tokenize=True, return_dict=True, return_tensors="pt"
            )
            inputs = {k: v.to(self.device) if hasattr(v, "to") else v for k, v in inputs.items()}
            in_len = inputs["input_ids"].shape[1]
            with torch.inference_mode():
                seq = self.model.generate(**inputs, max_new_tokens=256)
            text = self.processor.decode(seq[0, in_len:])
            try:
                act = self.processor.select_action(self.model, batch)
                action = getattr(act, "action", act)
                if action is not None and hasattr(action, "detach"):
                    action = action.detach().cpu().numpy()
                path_used += " ; recovered via generate + select_action"
            except Exception as exc2:  # noqa: BLE001
                path_used += f" ; select_action also failed: {type(exc2).__name__}: {exc2}"
        rec = {
            "sandbox": "eo1",
            "path": path_used,
            "task": task,
            "text": str(text),
            "action": action,
            "verdict": mouth_verdict(str(text)),
        }
        append_log({k: rec[k] for k in ("sandbox", "path", "task", "text", "verdict")})
        return rec
