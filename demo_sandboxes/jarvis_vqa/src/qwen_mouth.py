"""Leftover-mouth smoke for CraftJarvis/JarvisVLA-Qwen2-VL-7B.

Prompt layout matches the official SFT / VLLM_AGENT turn: instruction text,
then ``\\nobservation: \\n``, then the image. Decode keeps specials (action
tokens). If a token has no unicode string, the id is shown as ``<id:N>``.
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
_ACTIONISH = re.compile(r"<\|reserved_special_token_\d+\|>|<id:\d+>")


def _maps_to_unicode(s: str | None) -> bool:
    if not s:
        return False
    return not all(ch == "\ufffd" for ch in s)


def decode_keep_specials(tokenizer, ids) -> str:
    """Decode generated ids. Named specials stay as the tokenizer wrote them.

    Only tokens that decode to empty / U+FFFD become ``<id:N>``.
    """
    pieces: list[str] = []
    for tid in ids:
        tid = int(tid)
        chunk = tokenizer.decode(
            [tid], skip_special_tokens=False, clean_up_tokenization_spaces=False
        )
        if _maps_to_unicode(chunk):
            pieces.append(chunk)
            continue
        name = tokenizer.convert_ids_to_tokens(tid)
        if isinstance(name, bytes):
            try:
                name = name.decode("utf-8")
            except UnicodeDecodeError:
                name = ""
        if _maps_to_unicode(name):
            pieces.append(name)
        else:
            pieces.append(f"<id:{tid}>")
    return "".join(pieces)


def mouth_verdict(text: str) -> str:
    reserved = _ACTIONISH.findall(text or "")
    leftover = _ACTIONISH.sub(" ", text or "")
    words = _WORD.findall(leftover)
    if len(reserved) >= 3 and len(words) < 3:
        return "action_tokens"
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
        # Official SFT / VLLM_AGENT order: text, then image. Not Qwen's image-first snippet.
        prompt = f"{question}\nobservation: \n"
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image", "image": image},
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
        tokenizer = self.processor.tokenizer
        reply = decode_keep_specials(tokenizer, trimmed[0].tolist())
        verdict = mouth_verdict(reply)
        frame_path = LOG_DIR / "last_frame.png"
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        image.save(frame_path)
        rec = {
            "sandbox": "jarvis_vqa",
            "question": question,
            "prompt": prompt,
            "reply": reply,
            "think": None,
            "verdict": verdict,
            "frame": str(frame_path),
            "weights": self.weights,
        }
        append_log(rec)
        return rec
