"""Official ECoT-OpenVLA predict_action + English chain decode.

Prompt and unnorm_key match the Colab / README. Same weights. No second VLM.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
WEIGHTS = ROOT / "weights" / "ecot-openvla-7b-bridge"
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


TAGS = [
    "TASK:",
    "PLAN:",
    "VISIBLE OBJECTS:",
    "SUBTASK REASONING:",
    "SUBTASK:",
    "MOVE REASONING:",
    "MOVE:",
    "GRIPPER POSITION:",
    "ACTION:",
]
OFFICIAL_TASK = "put the mushroom in the pot"


def official_prompt(instruction: str) -> str:
    return (
        "A chat between a curious user and an artificial intelligence assistant. "
        "The assistant gives helpful, detailed, and polite answers to the user's questions. "
        f"USER: What action should the robot take to {instruction.lower()}? ASSISTANT: TASK:"
    )


def split_reasoning(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    work = " " + (text or "")
    positions = []
    for tag in TAGS:
        key = " " + tag
        i = work.find(key)
        if i >= 0:
            positions.append((i, tag))
    positions.sort()
    for n, (i, tag) in enumerate(positions):
        start = i + 1 + len(tag)
        end = positions[n + 1][0] if n + 1 < len(positions) else len(work)
        found[tag] = work[start:end].strip()
    return found


class ECoTPlay:
    def __init__(self, weights: Path | str = WEIGHTS, device: str = "cuda"):
        import torch
        from transformers import AutoModelForVision2Seq, AutoProcessor

        self.weights = Path(weights)
        self.device = device
        self.processor = AutoProcessor.from_pretrained(str(self.weights), trust_remote_code=True)
        self.model = AutoModelForVision2Seq.from_pretrained(
            str(self.weights), torch_dtype=torch.bfloat16, trust_remote_code=True
        ).to(device).eval()

    def predict(self, image, instruction: str | None = None) -> dict[str, Any]:
        import torch
        from PIL import Image

        if not isinstance(image, Image.Image):
            image = Image.open(image).convert("RGB")
        instruction = instruction or OFFICIAL_TASK
        prompt = official_prompt(instruction)
        inputs = self.processor(prompt, image).to(self.device, dtype=torch.bfloat16)
        with torch.inference_mode():
            action, generated_ids = self.model.predict_action(
                **inputs, unnorm_key="bridge_orig", do_sample=False, max_new_tokens=1024
            )
        if hasattr(action, "detach"):
            action = action.detach().cpu().numpy()
        text = self.processor.batch_decode(generated_ids)[0]
        parts = split_reasoning(text)
        english = " ".join(
            parts.get(t, "") for t in ("TASK:", "PLAN:", "SUBTASK:", "MOVE:")
        )
        rec = {
            "sandbox": "ecot_openvla",
            "path": "predict_action + batch_decode",
            "task": instruction,
            "prompt": prompt,
            "text": text,
            "parts": parts,
            "action": action,
            "verdict": mouth_verdict(english or text),
        }
        append_log({k: rec[k] for k in ("sandbox", "path", "task", "text", "verdict")})
        return rec
