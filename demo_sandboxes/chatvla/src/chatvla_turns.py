"""ChatVLA-1 official evaluate on the SAME weights.

Vendor: evaluate/evaluate_robot.py -> policy.evaluate(**batch, eval_in_vqa=...).
No second Qwen. ChatVLA-2 robot weights do not exist on the Hub.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
WEIGHTS = ROOT / "weights" / "ChatVLA"
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


VENDOR = ROOT / "vendor" / "ChatVLA_public"
OFFICIAL_TASK = "Remove the towel from the shelf."


def _vendor_on_path() -> None:
    import sys

    for p in (VENDOR, VENDOR / "policy_heads"):
        s = str(p)
        if p.exists() and s not in sys.path:
            sys.path.insert(0, s)


class ChatVLAPlay:
    def __init__(self, weights: Path | str = WEIGHTS, device: str = "cuda"):
        self.weights = Path(weights)
        self.device = device
        self.policy = None
        self.err = None
        _vendor_on_path()
        try:
            from qwen2_vla.model_load_utils import load_model_for_eval

            cfg = {
                "model_path": str(self.weights),
                "model_base": None,
                "enable_lora": False,
                "action_head": "scale_dp_policy",
                "save_model": False,
                "pretrain_path": None,
            }
            tok, pol, proc, _ctx = load_model_for_eval(
                model_path=str(self.weights), model_base=None, policy_config=cfg
            )
            self.tokenizer = tok
            self.policy = pol
            self.processor = proc
        except Exception as exc:  # noqa: BLE001
            self.err = f"{type(exc).__name__}: {exc}"

    def evaluate(self, top, left, right, task: str | None = None, eval_in_vqa: bool = False) -> dict[str, Any]:
        import numpy as np
        import torch
        from PIL import Image

        task = task or OFFICIAL_TASK
        frames = []
        for im in (top, left, right):
            if not isinstance(im, Image.Image):
                im = Image.open(im).convert("RGB")
            frames.append(im.convert("RGB"))
        text = ""
        action = None
        raw = None
        path_used = "policy.evaluate"
        if self.policy is None:
            path_used = f"vendor load failed: {self.err}"
            rec = {
                "sandbox": "chatvla",
                "path": path_used,
                "task": task,
                "text": "",
                "action": None,
                "verdict": "empty",
                "note": "ChatVLA-1 weights downloaded; vendor evaluate did not import. Do not substitute stock Qwen.",
            }
            append_log(rec)
            return rec
        try:
            # Official process_batch wants a 3-cam tensor; we go through their
            # chat template the same way evaluate_robot.py does.
            from evaluate.evaluate_robot import qwen2_vla_policy  # type: ignore
        except Exception:
            qwen2_vla_policy = None
        try:
            images = [np.array(im) for im in frames]
            stacked = np.stack(images, axis=0)
            t = torch.from_numpy(stacked).permute(0, 3, 1, 2).unsqueeze(0).float().to(self.device)
            state = torch.zeros(1, 14, dtype=torch.float32, device=self.device)
            if hasattr(self.policy, "evaluate"):
                all_actions, outputs = self.policy.evaluate(
                    states=state,
                    eval_in_vqa=eval_in_vqa,
                    is_eval=True,
                    tokenizer=getattr(self, "tokenizer", None),
                )
                raw = outputs
                text = str(outputs)
                action = all_actions
            else:
                path_used = "policy has no evaluate()"
        except Exception as exc:  # noqa: BLE001
            path_used = f"evaluate FAILED: {type(exc).__name__}: {exc}"
            # Same-weights chat generate only — still ChatVLA, not stock Qwen.
            try:
                from transformers import AutoProcessor
                from qwen_vl_utils import process_vision_info

                proc = AutoProcessor.from_pretrained(str(self.weights), trust_remote_code=True)
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": frames[0]},
                            {"type": "text", "text": task},
                        ],
                    }
                ]
                prompt = proc.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                img_in, vid_in = process_vision_info(messages)
                inputs = proc(text=[prompt], images=img_in, videos=vid_in, return_tensors="pt")
                inputs = {k: v.to(self.device) if hasattr(v, "to") else v for k, v in inputs.items()}
                with torch.inference_mode():
                    gen = self.policy.generate(**inputs, max_new_tokens=256)
                text = proc.batch_decode(gen, skip_special_tokens=False)[0]
                path_used += " ; same-weights generate"
            except Exception as exc2:  # noqa: BLE001
                path_used += f" ; generate also failed: {type(exc2).__name__}: {exc2}"
        rec = {
            "sandbox": "chatvla",
            "path": path_used,
            "task": task,
            "text": str(text),
            "raw": raw,
            "action": action,
            "verdict": mouth_verdict(str(text)),
            "eval_in_vqa": eval_in_vqa,
            "note": "three views are the same EO-1 example1.jpg stand-in, not ALOHA cameras",
        }
        append_log({k: rec[k] for k in ("sandbox", "path", "task", "text", "verdict", "eval_in_vqa")})
        return rec
