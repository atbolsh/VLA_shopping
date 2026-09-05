"""Two-headed EO-1 wrapper: one observation, ask (lm_head) and act (flow).

Official inference builds two sequences. This does not invent a shared z.
It encodes the same Bridge still once as a PIL, then fires both heads.

Act uses the Bridge ``robot_config`` from ``eo1-qwen25_vl-bridge`` (stats +
``observation.images.image_0``). The Hub 3B card ships an empty config, which
is why ``select_action`` IndexError'd on the demo stills. Chunk size is 16
to match ``EO-1-3B`` ``config.action_chunk_size``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from eo1_chat import VL_EVAL_GEN, user_turn
from widowx_env import DEFAULT_TASK, WidowXBridgeEnv, bridge7_to_simpler

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ROOT / "weights" / "EO-1-3B"
CONFIG_PATH = Path(__file__).resolve().parent / "bridge_robot_config.json"
BRIDGE_REPO = "bridge_orig_1.0.0_lerobot"
ASK_SUFFIX = "In one English sentence, what is the next subtask you will execute?"


def load_bridge_robot_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _as_image(image) -> Image.Image:
    if isinstance(image, Image.Image):
        return image.convert("RGB")
    arr = np.asarray(image)
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr).convert("RGB")


def _first_action(action) -> np.ndarray | None:
    if action is None:
        return None
    if hasattr(action, "detach"):
        action = action.detach().cpu().numpy()
    arr = np.asarray(action)
    if arr.ndim == 3:
        arr = arr[0]
    if arr.ndim == 2:
        return arr[0].astype(np.float32)
    if arr.ndim == 1:
        return arr.astype(np.float32)
    return None


class EO1Both:
    """Same 3B. Ask = VL-eval ``model.generate``. Act = ``select_action`` + Bridge stats."""

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
        self.processor.set_normalization(load_bridge_robot_config())
        if not getattr(self.processor, "normalize_inputs", None):
            raise RuntimeError("Bridge robot_config did not install. select_action will fail.")

    def _to_device(self, inputs: dict) -> dict:
        return {k: v.to(self.device) if hasattr(v, "to") else v for k, v in inputs.items()}

    def ask(self, image, instruction: str) -> str:
        import torch
        from qwen_vl_utils import process_vision_info

        image = _as_image(image)
        text = f"{instruction.strip()}\n{ASK_SUFFIX}"
        messages = user_turn(image, text)
        prompt = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        images, videos = process_vision_info(messages)
        packed = self.processor(
            text=prompt, images=images, videos=videos, padding=True, return_tensors="pt"
        )
        inputs = self._to_device(dict(packed))
        in_len = int(inputs["input_ids"].shape[1])
        gen = dict(VL_EVAL_GEN)
        with torch.inference_mode():
            seq = self.model.generate(**inputs, **gen)
        return self.processor.decode(seq[0, in_len:], skip_special_tokens=True).strip()

    def act(self, image, state, instruction: str):
        image = _as_image(image)
        state = np.asarray(state, dtype=np.float32).reshape(-1)
        batch = {
            "observation.images.image_0": [image],
            "observation.state": [state],
            "task": [instruction.strip()],
            "repo_id": [BRIDGE_REPO],
        }
        out = self.processor.select_action(self.model, batch)
        action = getattr(out, "action", out)
        if hasattr(action, "detach"):
            action = action.detach().cpu().numpy()
        return action

    def both(self, image, state, instruction: str) -> dict[str, Any]:
        image = _as_image(image)
        ask = self.ask(image, instruction)
        action = self.act(image, state, instruction)
        return {
            "ask": ask,
            "action": action,
            "action0": _first_action(action),
            "instruction": instruction,
        }


class EO1Live:
    """Interactive loop: user instruction → ask + act → WidowX step → new view."""

    def __init__(
        self,
        task: str = DEFAULT_TASK,
        weights: Path | str = WEIGHTS,
        device: str = "cuda",
    ):
        self.policy = EO1Both(weights=weights, device=device)
        self.env = WidowXBridgeEnv(task)
        self.last: dict[str, Any] | None = None

    @property
    def instruction_default(self) -> str:
        return self.env.instruction

    def reset(self, seed: int | None = None) -> np.ndarray:
        self.last = None
        return self.env.reset(seed=seed)

    def step(self, instruction: str | None = None) -> dict[str, Any]:
        instruction = (instruction or self.env.instruction).strip()
        rec = self.policy.both(self.env.image, self.env.state, instruction)
        raw0 = rec["action0"]
        if raw0 is None:
            rec["env_error"] = "no action from select_action"
            rec["image"] = self.env.image
            rec["state"] = self.env.state
            rec["steps"] = self.env.steps
            rec["done"] = self.env.done
            rec["reward"] = self.env.reward
            self.last = rec
            return rec
        self.env.step_bridge7(raw0[:7])
        rec.update(
            {
                "image": self.env.image,
                "state": self.env.state,
                "steps": self.env.steps,
                "done": self.env.done or self.env.truncated,
                "reward": self.env.reward,
                "simpler_action": bridge7_to_simpler(raw0[:7]),
                "env_instruction": self.env.instruction,
            }
        )
        self.last = rec
        return rec


def attach_widgets(live: EO1Live):
    """Instruction box + Ask+Act. Edit the text before the next press."""
    import ipywidgets as widgets
    from IPython.display import Markdown, display
    from PIL import Image

    box = widgets.Textarea(
        value=live.instruction_default,
        description="instruction",
        layout=widgets.Layout(width="90%", height="80px"),
    )
    act_btn = widgets.Button(description="Ask + Act", button_style="primary")
    reset_btn = widgets.Button(description="Reset env")
    out = widgets.Output()

    def _show(rec: dict | None = None) -> None:
        display(Markdown(f"**view** step `{live.env.steps}` · done `{live.env.done}` · reward `{live.env.reward}`"))
        display(Image.fromarray(live.env.image))
        if rec is None:
            return
        display(Markdown("**ask**"))
        print(rec.get("ask") or "_(empty)_")
        display(Markdown("**act** (first of chunk, Bridge 7)"))
        print(rec.get("action0"))
        if rec.get("env_error"):
            display(Markdown(f"**env** `{rec['env_error']}`"))

    def on_act(_):
        with out:
            out.clear_output(wait=True)
            rec = live.step(box.value)
            _show(rec)

    def on_reset(_):
        live.reset()
        box.value = live.instruction_default
        with out:
            out.clear_output(wait=True)
            _show()

    act_btn.on_click(on_act)
    reset_btn.on_click(on_reset)
    display(box, widgets.HBox([act_btn, reset_btn]), out)
    with out:
        _show()
