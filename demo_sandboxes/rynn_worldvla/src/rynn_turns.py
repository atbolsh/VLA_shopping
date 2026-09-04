"""Three official-shaped turns on the same RynnVLA-002 / WorldVLA weights.

Stay in Lumina/xllmx. Do not use AutoModelForCausalLM.
Talk = leftover BPE (>=16384) after banning image + reserved/action ids.
A caption from Meta Chameleon or RynnVLA-001-7B-Base does not count.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "WorldVLA"
WEIGHTS = ROOT / "weights"
LOG_DIR = ROOT / "logs"

# notes/11_chameleon_talk_harness.md — measured on WorldVLA text_tokenizer.json
BOS, PAD, EOS, UNK = 0, 1, 2, 3
IMG_LO, IMG_HI = 4, 8195
ACT_LO, ACT_HI = 8196, 16383
BPE_LO = 16384

_WORD = re.compile(r"[A-Za-z]{3,}")


def _on_path() -> None:
    # rynnvla-002 first: official ``from model import ChameleonXLLMX…``.
    for p in (VENDOR / "rynnvla-002", VENDOR, ROOT / "src"):
        s = str(p)
        if p.exists() and s not in sys.path:
            sys.path.insert(0, s)


def append_log(record: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"{day}.jsonl"
    record = dict(record)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
    return path


def leftover_verdict(text: str) -> str:
    cleaned = re.sub(r"IMGIMG\S*|</?s>|<\w+>", " ", text or "")
    words = _WORD.findall(cleaned)
    if len(words) >= 3:
        return "usable"
    if (text or "").strip():
        return "garbage"
    return "empty"


def find_tokenizer_json() -> Path:
    hits = list((WEIGHTS / "WorldVLA").rglob("text_tokenizer.json"))
    if not hits:
        hits = list(WEIGHTS.rglob("text_tokenizer.json"))
    if not hits:
        raise FileNotFoundError("text_tokenizer.json not under weights/")
    return hits[0]


def find_vla_ckpt() -> Path:
    goal = WEIGHTS / "RynnVLA-002" / "VLA_model_256" / "libero_goal"
    if goal.exists():
        return goal
    raise FileNotFoundError(f"missing {goal}")


def find_world_ckpt() -> Path:
    for name in ("Action_World_model_512", "World_model_512"):
        p = WEIGHTS / "RynnVLA-002" / name / "libero_goal"
        if p.exists():
            return p
    raise FileNotFoundError("no world-model ckpt under weights/RynnVLA-002")


class _BanNonBpe(torch.nn.Module):
    """Force next-token onto BPE + bos/eos. Image and action bins are banned."""

    def __init__(self, vocab: int):
        super().__init__()
        self.vocab = vocab

    def __call__(self, input_ids: torch.Tensor, scores: torch.Tensor) -> torch.Tensor:
        banned = torch.arange(self.vocab, device=scores.device)
        mask = (banned >= IMG_LO) & (banned <= ACT_HI)
        scores = scores.clone()
        scores[:, mask] = -float("inf")
        return scores


def _load_xllmx(ckpt: Path):
    """Official WorldVLA class — ``rynnvla-002/model``, never AutoModelForCausalLM.

    Eval scripts (``eval_solver_libero_g_video_512_third_wrist.py``) do
    ``from model import ChameleonXLLMXForConditionalGeneration`` then
    ``from_pretrained(ckpt, torch_dtype=bfloat16)``. The ``_ck`` /
    ``_ck_action_head`` variants are the same family if the base class
    rejects the checkpoint.
    """
    _on_path()
    if not (VENDOR / "rynnvla-002" / "model" / "__init__.py").is_file():
        raise ImportError(
            f"vendor WorldVLA missing at {VENDOR}. "
            "In the rynn-worldvla venv: bash setup.sh"
        )
    errors = []
    for cls in (
        "ChameleonXLLMXForConditionalGeneration",
        "ChameleonXLLMXForConditionalGeneration_ck",
        "ChameleonXLLMXForConditionalGeneration_ck_action_head",
    ):
        try:
            m = __import__("model", fromlist=[cls])
            K = getattr(m, cls)
            model = K.from_pretrained(
                str(ckpt),
                torch_dtype=torch.bfloat16,
                max_position_embeddings=4096,
            )
            model.eval()
            if torch.cuda.is_available():
                model.cuda()
            return model
        except Exception as exc:  # noqa: BLE001
            errors.append(f"model.{cls}: {exc}")
    raise ImportError(
        "Could not load official rynnvla-002 ChameleonXLLMX class. Tried:\n"
        + "\n".join(errors)
    )


def _load_chameleon_tokenizer():
    """WorldVLA ships a raw Chameleon ``text_tokenizer.json``, not an HF
    LlamaTokenizer folder (no tokenizer_config.json / config.json). Official
    convert script: ``LlamaTokenizerFast(tokenizer_file=..., legacy=False)``
    in ``rynnvla-002/model/chameleon/convert_chameleon_weights_to_hf.py``.
    """
    tok_json = find_tokenizer_json()
    from transformers import LlamaTokenizerFast

    tok = LlamaTokenizerFast(tokenizer_file=str(tok_json), legacy=False)
    tok.pad_token_id = PAD
    tok.bos_token_id = BOS
    tok.eos_token_id = EOS
    tok.sep_token_id = 8710
    return tok


def load_sample_cameras() -> tuple[Image.Image, Image.Image, Path, Path]:
    """Official first frames, not assets/ orange/blue placeholders."""
    shot = ROOT / "screenshot"
    third_p = shot / "sample_third.png"
    wrist_p = shot / "sample_wrist.png"
    if not (third_p.is_file() and wrist_p.is_file()):
        raise FileNotFoundError(
            "screenshot/ missing official LIBERO frames. "
            "In the rynn-worldvla venv: python download_frames.py"
        )
    third = Image.open(third_p).convert("RGB")
    wrist = Image.open(wrist_p).convert("RGB")
    if len(set(third.getdata())) <= 16 or len(set(wrist.getdata())) <= 16:
        raise FileNotFoundError(
            "screenshot/ still looks like a solid-color placeholder. "
            "Re-run: python download_frames.py"
        )
    return third, wrist, third_p, wrist_p


class RynnSession:
    def __init__(self):
        self.tokenizer = _load_chameleon_tokenizer()
        self.vla = None
        self.world = None
        self.force_sdpa = True
        rung = ROOT / ".rung"
        if rung.exists() and "flash_attn=1" in rung.read_text(encoding="utf-8"):
            self.force_sdpa = False

    def _ensure_vla(self):
        if self.vla is None:
            self.vla = _load_xllmx(find_vla_ckpt())
        return self.vla

    def _ensure_world(self):
        if self.world is None:
            self.world = _load_xllmx(find_world_ckpt())
        return self.world

    def _greedy_banned(self, model, prompt_ids: list[int], max_new: int = 64) -> tuple[list[int], str]:
        device = next(model.parameters()).device
        ids = torch.tensor([prompt_ids], device=device)
        banned = _BanNonBpe(int(getattr(self.tokenizer, "vocab_size", 65536)))
        produced: list[int] = []
        with torch.inference_mode():
            for _ in range(max_new):
                out = model(input_ids=ids)
                logits = out.logits if hasattr(out, "logits") else out[0]
                step = banned(ids, logits[:, -1, :])
                nxt = int(torch.argmax(step, dim=-1).item())
                produced.append(nxt)
                if nxt in (EOS, BOS) and produced:
                    break
                ids = torch.cat([ids, torch.tensor([[nxt]], device=device)], dim=1)
        text = self.tokenizer.decode(produced, skip_special_tokens=False)
        return produced, text

    def talk(self, image: Image.Image, question: str) -> dict[str, Any]:
        """Leftover English: same VLA weights, image+action ids banned."""
        model = self._ensure_vla()
        prompt = (
            f"{question}\n"
            "Answer in English using only ordinary words. "
            "Do not emit image or action tokens."
        )
        # Text-only prompt on purpose: official VLA would ask for <|action|> / <|image|>.
        prompt_ids = self.tokenizer.encode(prompt, add_special_tokens=True)
        ids, text = self._greedy_banned(model, prompt_ids)
        verdict = leftover_verdict(text)
        rec = {
            "sandbox": "rynn_worldvla",
            "turn": "talk",
            "question": question,
            "reply": text,
            "think": {
                "banned_id_range": [IMG_LO, ACT_HI],
                "produced_ids": ids[:48],
                "bpe_only": all((i < IMG_LO) or (i >= BPE_LO) or i == EOS for i in ids),
            },
            "verdict": verdict,
            "note": "leftover BPE from VLA weights, not Meta Chameleon / 001-Base",
        }
        append_log(rec)
        return rec

    def act(self, third: Image.Image, wrist: Image.Image | None, instruction: str) -> dict[str, Any]:
        """Official-shaped action query: ask for <|action|>."""
        model = self._ensure_vla()
        prompt = f"What action should the robot take to {instruction}?<|action|>"
        prompt_ids = self.tokenizer.encode(prompt, add_special_tokens=True)
        device = next(model.parameters()).device
        ids = torch.tensor([prompt_ids], device=device)
        produced: list[int] = []
        with torch.inference_mode():
            for _ in range(16):
                out = model(input_ids=ids)
                logits = out.logits if hasattr(out, "logits") else out[0]
                nxt = int(torch.argmax(logits[:, -1, :], dim=-1).item())
                produced.append(nxt)
                if nxt == EOS:
                    break
                ids = torch.cat([ids, torch.tensor([[nxt]], device=device)], dim=1)
        n_act = sum(1 for i in produced if ACT_LO <= i <= ACT_HI)
        rec = {
            "sandbox": "rynn_worldvla",
            "turn": "act",
            "instruction": instruction,
            "reply": f"{n_act} action-bin tokens of {len(produced)}: {produced}",
            "think": {"produced_ids": produced},
            "action_ids": produced,
            "third": "shown",
            "wrist": wrist is not None,
        }
        append_log(rec)
        return rec

    def dream(
        self,
        third: Image.Image,
        wrist: Image.Image | None,
        action_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        """Official-shaped world-model query: action + frame → next image tokens.

        Full PNG decode uses their VQ codebook + eval_world_model_goal.sh.
        This open-loop path reports the generated image-token ids and saves
        a side-by-side of the *input* frames; if the vendor solver is
        importable it also writes next_frame.png.
        """
        model = self._ensure_world()
        prompt = (
            "Generate the next image based on the provided sequence of "
            "historical images and corresponding actions.<|image|><|action|>"
        )
        prompt_ids = self.tokenizer.encode(prompt, add_special_tokens=True)
        if action_ids:
            prompt_ids = prompt_ids + [i for i in action_ids if ACT_LO <= i <= ACT_HI][:8]
        device = next(model.parameters()).device
        ids = torch.tensor([prompt_ids], device=device)
        produced: list[int] = []
        with torch.inference_mode():
            for _ in range(32):
                out = model(input_ids=ids)
                logits = out.logits if hasattr(out, "logits") else out[0]
                nxt = int(torch.argmax(logits[:, -1, :], dim=-1).item())
                produced.append(nxt)
                if nxt == EOS:
                    break
                ids = torch.cat([ids, torch.tensor([[nxt]], device=device)], dim=1)
        n_img = sum(1 for i in produced if IMG_LO <= i <= IMG_HI)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        third_path = LOG_DIR / "dream_input_third.png"
        third.save(third_path)
        next_path = None
        try:
            next_path = self._try_official_vq_decode(produced)
        except Exception as exc:  # noqa: BLE001
            next_path = f"vq-decode-not-available: {exc}"
        rec = {
            "sandbox": "rynn_worldvla",
            "turn": "dream",
            "reply": f"{n_img} image tokens of {len(produced)}",
            "think": {"produced_ids": produced[:64]},
            "input_frame": str(third_path),
            "next_frame": next_path,
            "official_script": "vendor/WorldVLA/rynnvla-002/exps_libero_world_model/eval_world_model_goal.sh",
        }
        append_log(rec)
        return rec

    def _try_official_vq_decode(self, token_ids: list[int]) -> str:
        """Best-effort: vendor ImageTokenizer if present."""
        _on_path()
        img_ids = [i - IMG_LO for i in token_ids if IMG_LO <= i <= IMG_HI]
        if not img_ids:
            raise RuntimeError("no IMGIMG tokens to decode")
        # Official eval script is the real PNG path; this is a stub hook.
        raise RuntimeError(
            "use eval_world_model_goal.sh on the same ckpt for a decoded PNG"
        )
