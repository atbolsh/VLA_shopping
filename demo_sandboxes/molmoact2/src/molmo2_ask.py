"""Official Molmo2-ER VQA path (allenai/molmo2 apply_chat_template).

Separate model from Think-LIBERO. Do not mix prompts with predict_action.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ROOT / "weights" / "Molmo2-ER"
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


class Molmo2Ask:
    def __init__(self, weights: Path | str = WEIGHTS):
        self.processor = AutoProcessor.from_pretrained(
            str(weights),
            trust_remote_code=True,
            padding_side="left",
        )
        self.model = AutoModelForImageTextToText.from_pretrained(
            str(weights),
            trust_remote_code=True,
            torch_dtype="auto",
            device_map="auto",
        )

    def ask(self, image: Image.Image, question: str, max_new_tokens: int = 256) -> dict[str, Any]:
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image).convert("RGB")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image", "image": image},
                ],
            }
        ]
        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
            padding=True,
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
            output = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        generated = output[0, inputs["input_ids"].size(1) :]
        reply = self.processor.decode(generated, skip_special_tokens=True)
        rec = {
            "sandbox": "molmoact2",
            "turn": "ask_molmo2er",
            "question": question,
            "reply": reply,
            "think": None,
        }
        append_log(rec)
        return rec
