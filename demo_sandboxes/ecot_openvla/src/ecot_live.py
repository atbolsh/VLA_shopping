"""ECoT on WidowX / Bridge: one predict_action is already ask (chain) + act."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from ecot_turns import ECoTPlay
from widowx_env import DEFAULT_TASK, WidowXBridgeEnv, bridge7_to_simpler

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ROOT / "weights" / "ecot-openvla-7b-bridge"


def _as_image(image) -> Image.Image:
    if isinstance(image, Image.Image):
        return image.convert("RGB")
    arr = np.asarray(image)
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr).convert("RGB")


def _raw7(action) -> np.ndarray | None:
    if action is None:
        return None
    if hasattr(action, "detach"):
        action = action.detach().cpu().numpy()
    arr = np.asarray(action).reshape(-1)
    if arr.size < 7:
        return None
    return arr[:7].astype(np.float32)


class ECoTLive:
    """Interactive loop: user instruction → TASK/PLAN/SUBTASK/MOVE + action → env step."""

    def __init__(
        self,
        task: str = DEFAULT_TASK,
        weights: Path | str = WEIGHTS,
        device: str = "cuda",
    ):
        self.policy = ECoTPlay(weights=weights, device=device)
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
        out = self.policy.predict(_as_image(self.env.image), instruction)
        raw0 = _raw7(out.get("action"))
        rec: dict[str, Any] = {
            "ask": out.get("text") or "",
            "parts": out.get("parts") or {},
            "action": out.get("action"),
            "action0": raw0,
            "instruction": instruction,
            "verdict": out.get("verdict"),
        }
        if raw0 is None:
            rec["env_error"] = "no action from predict_action"
        else:
            self.env.step_bridge7(raw0)
            rec["simpler_action"] = bridge7_to_simpler(raw0)
        rec.update(
            {
                "image": self.env.image,
                "steps": self.env.steps,
                "done": self.env.done or self.env.truncated,
                "reward": self.env.reward,
                "env_instruction": self.env.instruction,
            }
        )
        self.last = rec
        return rec


def attach_widgets(live: ECoTLive):
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
        display(Markdown("**ask** (TASK / PLAN / SUBTASK / MOVE)"))
        print(rec.get("ask") or "_(empty)_")
        display(Markdown("**act** (Bridge 7)"))
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
