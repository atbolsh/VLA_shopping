"""WALL-OSS same-weights action + CoT probe.

Official: Qwen2_5_VLMoEForAction.from_pretrained + generate_flow_action / validate.
Paper CoT is not in fake_inference.py. We also try tokenizer generate on THESE weights.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
WEIGHTS = ROOT / "weights" / "wall-oss-flow"
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


VENDOR = ROOT / "vendor" / "wall-x"
OFFICIAL_TASK = "pick up the cup"


def _vendor_on_path() -> None:
    import sys

    s = str(VENDOR)
    if VENDOR.exists() and s not in sys.path:
        sys.path.insert(0, s)


class WallOSSPlay:
    def __init__(self, weights: Path | str = WEIGHTS, device: str = "cuda"):
        import torch

        _vendor_on_path()
        self.weights = Path(weights)
        self.device = device
        self.model = None
        self.err = None
        try:
            from wall_x.model.qwen2_5_based.modeling_qwen2_5_vl_act import (
                Qwen2_5_VLMoEForAction,
            )

            self.model = Qwen2_5_VLMoEForAction.from_pretrained(str(self.weights))
            self.model = self.model.to(device).bfloat16().eval()
        except Exception as exc:  # noqa: BLE001
            self.err = f"{type(exc).__name__}: {exc}"

    def act_and_talk(self, face, wrist, task: str | None = None) -> dict[str, Any]:
        import torch
        from PIL import Image

        task = task or OFFICIAL_TASK
        if not isinstance(face, Image.Image):
            face = Image.open(face).convert("RGB")
        if wrist is not None and not isinstance(wrist, Image.Image):
            wrist = Image.open(wrist).convert("RGB")
        text = ""
        action = None
        path_used = "generate_flow_action"
        if self.model is None:
            rec = {
                "sandbox": "wall_oss",
                "path": f"load failed: {self.err}",
                "task": task,
                "text": "",
                "action": None,
                "verdict": "empty",
            }
            append_log(rec)
            return rec
        # Official action path when present.
        try:
            if hasattr(self.model, "generate_flow_action"):
                # Minimal call; vendor scripts pass padding + constructed batch.
                # If this signature is wrong, we still do the text probe.
                action = "generate_flow_action present; need official batch — see text probe"
                path_used = "generate_flow_action (signature not faked; see note)"
            else:
                path_used = "no generate_flow_action"
        except Exception as exc:  # noqa: BLE001
            path_used = f"flow FAILED: {type(exc).__name__}: {exc}"
        # Same-weights text / CoT probe. This is the ask.
        try:
            proc = getattr(self.model, "processor", None)
            tok = getattr(proc, "tokenizer", None) if proc is not None else None
            if tok is None:
                from transformers import AutoProcessor

                proc = AutoProcessor.from_pretrained(str(self.weights), trust_remote_code=True)
                tok = proc.tokenizer
            prompt = (
                f"Instruction: {task}\n"
                "Write the chain of thought and the next subtask in plain English, "
                "then stop. Do not emit action tokens."
            )
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": face},
                        {"type": "text", "text": prompt},
                    ],
                }
            ]
            if hasattr(proc, "apply_chat_template"):
                inputs = proc.apply_chat_template(
                    messages, tokenize=True, return_dict=True, return_tensors="pt", add_generation_prompt=True
                )
            else:
                inputs = tok(prompt, return_tensors="pt")
            inputs = {k: v.to(self.device) if hasattr(v, "to") else v for k, v in inputs.items()}
            in_len = inputs["input_ids"].shape[1]
            with torch.inference_mode():
                if hasattr(self.model, "generate"):
                    seq = self.model.generate(**inputs, max_new_tokens=256)
                    text = tok.decode(seq[0, in_len:], skip_special_tokens=False)
                    path_used += " ; same-weights generate"
                else:
                    path_used += " ; model has no generate()"
        except Exception as exc:  # noqa: BLE001
            path_used += f" ; text FAILED: {type(exc).__name__}: {exc}"
        rec = {
            "sandbox": "wall_oss",
            "path": path_used,
            "task": task,
            "text": str(text),
            "action": action,
            "verdict": mouth_verdict(str(text)),
            "note": "face/wrist are EO-1 demo stand-ins, not X-Square cameras",
        }
        append_log({k: rec[k] for k in ("sandbox", "path", "task", "text", "verdict")})
        return rec
