"""InternVLA-N1 System 2 as Qwen2.5-VL chat — second official surface, cuda:1."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from transformers import AutoProcessor

try:
    from transformers import Qwen2_5_VLForConditionalGeneration as _S2Model
except ImportError:  # 4.51 sometimes still exports the 2-VL name
    from transformers import Qwen2VLForConditionalGeneration as _S2Model

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ROOT / "weights" / "InternVLA-N1-System2"
LOG_DIR = ROOT / "logs"
DEVICE = "cuda:1"


def append_log(record: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"{day}.jsonl"
    record = dict(record)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
    return path


class System2Ask:
    def __init__(self, weights: Path | str = WEIGHTS, device: str = DEVICE):
        self.device = torch.device(device if torch.cuda.device_count() > 1 else "cuda:0")
        self.model = _S2Model.from_pretrained(
            str(weights),
            torch_dtype=torch.bfloat16,
            device_map={"": self.device},
            trust_remote_code=True,
        )
        self.processor = AutoProcessor.from_pretrained(str(weights), trust_remote_code=True)

    def ask(self, image: Image.Image, question: str, max_new_tokens: int = 256) -> dict[str, Any]:
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image).convert("RGB")
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
        inputs = self.processor(
            text=[text], images=[image], padding=True, return_tensors="pt"
        ).to(self.device)
        with torch.inference_mode():
            out = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        trimmed = [o[len(i) :] for i, o in zip(inputs.input_ids, out)]
        reply = self.processor.batch_decode(trimmed, skip_special_tokens=True)[0]
        rec = {
            "sandbox": "internvla_n1",
            "turn": "system2_ask",
            "device": str(self.device),
            "question": question,
            "reply": reply,
            "think": None,
        }
        append_log(rec)
        return rec
