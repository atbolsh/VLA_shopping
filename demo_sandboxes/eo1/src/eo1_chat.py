"""Official EO-1 chat railroads, with every string printed.

GitHub README (text path): example2.png + apply_chat_template(tokenize=True)
  without add_generation_prompt, then model.generate(max_new_tokens=1024).
  https://github.com/EO-Robotics/EO1

Their VL-eval chat (RoboVQA / ERQA / EO-Bench): tokenize=False,
  add_generation_prompt=True, process_vision_info, then processor(...).
  experiments/8_vllmeval/vlm/model.py :: generate_inner_transformers
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
WEIGHTS = ROOT / "weights" / "EO-1-3B"
SHOT = ROOT / "screenshot"

# Exact README string (backslash-newline is Python line-join; spaces stay).
OFFICIAL_TTT = (
    "You are a helpful physical agent equipped with both reasoning and robotic control. "
    "            You see the Tic-Tac-Toe board, think strategically, act logically, and block threats."
)

OFFICIAL_ACT_TASK = "Pick up a red piece and place it at (0, 2)."

# Official VL-eval sampling (EO1VisionFlowMatchingChat.__init__).
VL_EVAL_GEN = dict(
    max_new_tokens=1024,
    top_p=0.001,
    top_k=1,
    temperature=0.01,
    repetition_penalty=1.0,
)

CHATTY = (
    (
        "see_english",
        "What do you see? Answer in plain English sentences.",
    ),
    (
        "next_subtask",
        "In one English sentence, what is the next subtask you will execute?",
    ),
    (
        "i_will_now",
        "Think out loud in English. Then write a line that starts with: I will now",
    ),
    (
        "pick_red_explain",
        f"{OFFICIAL_ACT_TASK} Explain the plan in English first.",
    ),
)


def append_log(record: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"{day}-chat.jsonl"
    rec = dict(record)
    rec.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str, ensure_ascii=False) + "\n")
    return path


def _img_label(image) -> str:
    from PIL import Image

    if isinstance(image, Image.Image):
        return f"<PIL {image.size[0]}x{image.size[1]} {image.mode}>"
    return str(image)


def messages_for_print(messages: list[dict]) -> list[dict]:
    out = []
    for msg in messages:
        item = {"role": msg.get("role")}
        content = msg.get("content")
        if isinstance(content, str):
            item["content"] = content
        else:
            item["content"] = []
            for part in content or []:
                p = dict(part)
                if "image" in p:
                    p["image"] = _img_label(p["image"])
                item["content"].append(p)
        out.append(item)
    return out


def user_turn(image, text: str) -> list[dict]:
    return [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": text},
            ],
        }
    ]


def user_turn_two(image, wrist, text: str) -> list[dict]:
    return [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "image", "image": wrist},
                {"type": "text", "text": text},
            ],
        }
    ]


def dump_block(title: str, body: str) -> None:
    from IPython.display import Markdown, display

    display(Markdown(f"**{title}**"))
    print(body if body else "_(empty)_")


class EO1Chat:
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

    def _to_device(self, inputs: dict) -> dict:
        return {k: v.to(self.device) if hasattr(v, "to") else v for k, v in inputs.items()}

    def _inputs_readme(self, messages: list[dict]) -> tuple[dict, str]:
        prompt = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        packed = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            add_generation_prompt=False,
        )
        return self._to_device(dict(packed)), prompt

    def _inputs_vl_eval(self, messages: list[dict]) -> tuple[dict, str]:
        from qwen_vl_utils import process_vision_info

        prompt = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        images, videos = process_vision_info(messages)
        packed = self.processor(
            text=prompt,
            images=images,
            videos=videos,
            padding=True,
            return_tensors="pt",
        )
        return self._to_device(dict(packed)), prompt

    def run(
        self,
        label: str,
        messages: list[dict],
        *,
        railroad: str,
        gen_kwargs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        import torch
        from IPython.display import Markdown, display

        if railroad == "readme":
            inputs, prompt = self._inputs_readme(messages)
            gen = {"max_new_tokens": 1024, "return_dict_in_generate": True}
        elif railroad == "vl_eval":
            inputs, prompt = self._inputs_vl_eval(messages)
            gen = dict(VL_EVAL_GEN)
            gen["return_dict_in_generate"] = True
        else:
            raise ValueError(railroad)
        if gen_kwargs:
            gen.update(gen_kwargs)

        in_ids = inputs["input_ids"]
        in_len = int(in_ids.shape[1])
        prompt_from_ids = self.processor.decode(in_ids[0], skip_special_tokens=False)

        display(Markdown(f"### {label}"))
        display(Markdown(f"`railroad={railroad}` · `in_len={in_len}` · gen `{ {k: gen[k] for k in gen if k != 'return_dict_in_generate'} }`"))
        dump_block("messages", json.dumps(messages_for_print(messages), indent=2, ensure_ascii=False))
        dump_block("prompt (apply_chat_template tokenize=False)", prompt)
        dump_block("prompt decoded from input_ids (special tokens kept)", prompt_from_ids)

        with torch.inference_mode():
            out = self.model.generate(**inputs, **gen)
        seq = out.sequences[0]
        raw = self.processor.decode(seq[in_len:], skip_special_tokens=False)
        formatted = self.processor.decode(seq[in_len:], skip_special_tokens=True)
        full_raw = self.processor.decode(seq, skip_special_tokens=False)
        n_new = int(seq.shape[0] - in_len)

        dump_block(f"raw continuation ({n_new} new tokens, special tokens kept)", raw)
        dump_block("formatted continuation (skip_special_tokens=True)", formatted)
        dump_block("full sequence decoded (special tokens kept)", full_raw)

        rec = {
            "sandbox": "eo1",
            "label": label,
            "railroad": railroad,
            "in_len": in_len,
            "n_new": n_new,
            "prompt": prompt,
            "raw": raw,
            "formatted": formatted,
        }
        append_log(rec)
        return rec
