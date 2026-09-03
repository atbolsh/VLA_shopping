"""Leftover-mouth smoke for CraftJarvis/JarvisVLA-Qwen2-VL-7B.

Official path is Qwen2-VL's own chat template + qwen_vl_utils, on the
JarvisVLA weights — not a Gemma-style system prompt.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEIGHTS = ROOT / "weights" / "JarvisVLA-Qwen2-VL-7B"
LOG_DIR = ROOT / "logs"

_WORD = re.compile(r"[A-Za-z]{2,}")


def mouth_verdict(text: str) -> str:
    words = _WORD.findall(text or "")
    if len(words) >= 3:
        return "usable"
    if (text or "").strip():
        return "garbage"
    return "empty"


def append_log(record: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"{day}.jsonl"
    record = dict(record)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


class JarvisQwenMouth:
    def __init__(self, weights: Path | str = DEFAULT_WEIGHTS, device: str = "cuda"):
        self.weights = str(weights)
        self.device = device
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.weights,
            torch_dtype="auto",
            device_map="auto",
            trust_remote_code=True,
        )
        self.processor = AutoProcessor.from_pretrained(
            self.weights, trust_remote_code=True
        )

    def ask(self, image: Image.Image | Path | str, question: str, max_new_tokens: int = 256) -> dict[str, Any]:
        if not isinstance(image, Image.Image):
            image = Image.open(image).convert("RGB")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": question},
                ],
            }
        ]
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(self.model.device)
        with torch.inference_mode():
            generated = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        trimmed = [
            out[len(inp) :] for inp, out in zip(inputs.input_ids, generated)
        ]
        reply = self.processor.batch_decode(
            trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        verdict = mouth_verdict(reply)
        frame_path = LOG_DIR / "last_frame.png"
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        image.save(frame_path)
        rec = {
            "sandbox": "jarvis_vqa",
            "question": question,
            "reply": reply,
            "think": None,
            "verdict": verdict,
            "frame": str(frame_path),
            "weights": self.weights,
        }
        append_log(rec)
        return rec
