"""Official JARVIS-VLA play step: VLLM_AGENT.forward.

Wraps CraftJarvis agent_wrapper after vendor/JarvisVLA is on PYTHONPATH.
Talk is the decoded action tokens they emit — not a second chat template.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "JarvisVLA"
WEIGHTS = ROOT / "weights" / "JarvisVLA-Qwen2-VL-7B"
LOG_DIR = ROOT / "logs"
RUNG = ROOT / ".rung"


def _vendor_on_path() -> None:
    if str(VENDOR) not in sys.path:
        sys.path.insert(0, str(VENDOR))


def append_log(record: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"{day}.jsonl"
    record = dict(record)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
    return path


def is_degraded() -> bool:
    if not RUNG.exists():
        return False
    return "degraded" in RUNG.read_text(encoding="utf-8")


class OfficialVllmPlay:
    """Thin wrapper around jarvisvla.evaluate.agent_wrapper.VLLM_AGENT."""

    def __init__(
        self,
        checkpoint: Path | str = WEIGHTS,
        base_url: str = "http://localhost:8000/v1",
        temperature: float = 0.7,
        history_num: int = 2,
        instruction_type: str = "normal",
    ):
        _vendor_on_path()
        from jarvisvla.evaluate.agent_wrapper import VLLM_AGENT

        self.agent = VLLM_AGENT(
            checkpoint_path=str(checkpoint),
            base_url=base_url,
            api_key=os.environ.get("HF_TOKEN", "EMPTY"),
            history_num=history_num,
            action_chunk_len=1,
            instruction_type=instruction_type,
            temperature=temperature,
        )

    def reset(self) -> None:
        self.agent.reset()

    def step(self, frame, instruction: str, need_crafting_table: bool = False) -> dict[str, Any]:
        if isinstance(frame, Image.Image):
            import numpy as np

            obs = [np.asarray(frame.convert("RGB"))]
            pil = frame.convert("RGB")
        else:
            import numpy as np

            obs = [np.asarray(frame)]
            pil = Image.fromarray(obs[0])
        action = self.agent.forward(
            observations=obs,
            instructions=[instruction],
            verbos=True,
            need_crafting_table=need_crafting_table,
        )
        frame_path = LOG_DIR / "last_frame.png"
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        pil.save(frame_path)
        rec = {
            "sandbox": "jarvis_minestudio",
            "path": "vllm_agent",
            "instruction": instruction,
            "action": action,
            "reply": str(action),
            "think": None,
            "frame": str(frame_path),
        }
        append_log(rec)
        return rec


class DegradedHfOneStep:
    """Only if vLLM would not install. One screenshot → generate; not the official serve loop."""

    def __init__(self, checkpoint: Path | str = WEIGHTS):
        import torch
        from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
        from qwen_vl_utils import process_vision_info

        self.torch = torch
        self.process_vision_info = process_vision_info
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            str(checkpoint), torch_dtype="auto", device_map="auto", trust_remote_code=True
        )
        self.processor = AutoProcessor.from_pretrained(str(checkpoint), trust_remote_code=True)

    def step(self, frame, instruction: str, **_kwargs) -> dict[str, Any]:
        if not isinstance(frame, Image.Image):
            frame = Image.fromarray(frame).convert("RGB")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": frame},
                    {"type": "text", "text": f"{instruction}\nobservation: "},
                ],
            }
        ]
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = self.process_vision_info(messages)
        inputs = self.processor(
            text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt"
        ).to(self.model.device)
        with self.torch.inference_mode():
            out = self.model.generate(**inputs, max_new_tokens=64, temperature=0.7)
        trimmed = [o[len(i) :] for i, o in zip(inputs.input_ids, out)]
        reply = self.processor.batch_decode(trimmed, skip_special_tokens=False)[0]
        rec = {
            "sandbox": "jarvis_minestudio",
            "path": "degraded-hf-generate",
            "instruction": instruction,
            "reply": reply,
            "think": None,
            "action": None,
        }
        append_log(rec)
        return rec
