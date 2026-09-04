"""Three official-shaped turns on the same RynnVLA-002 / WorldVLA weights.

Stay in Lumina/xllmx. Do not use AutoModelForCausalLM.
Talk = leftover BPE (>=16384) after banning image + reserved/action ids.
A caption from Meta Chameleon or RynnVLA-001-7B-Base does not count.
"""

from __future__ import annotations

import json
import os
import re
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image
from transformers import GenerationConfig

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "WorldVLA"
WEIGHTS = ROOT / "weights"
LOG_DIR = ROOT / "logs"

# notes/11_chameleon_talk_harness.md — measured on WorldVLA text_tokenizer.json
BOS, PAD, EOS, UNK = 0, 1, 2, 3
IMG_LO, IMG_HI = 4, 8195
ACT_LO, ACT_HI = 8196, 16383
BPE_LO = 16384
SEP_ID = 8710
ACTION_START_ID = 10004
ACTION_END_ID = 15004

# VLA_model_256/libero_goal args.json + official discrete eval
HIS_TYPE = "his_2_third_view_wrist_w_state"
ACTION_STEPS = 5
VLA_RESOLUTION = 256
WORLD_RESOLUTION = 512

_WORD = re.compile(r"[A-Za-z]{3,}")

# Discrete eval_solver_libero_discrete_w_state.unnorm_action_min_max
_ACTION_MIN = np.array([-0.9375, -0.9375, -0.9375, -0.24214286, -0.375, -0.36428571, -1.0])
_ACTION_MAX = np.array([0.9375, 0.9375, 0.9375, 0.34821429, 0.375, 0.375, 1.0])


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


def find_chameleon_tokenizer_dir() -> Path:
    tok = find_tokenizer_json().parent
    for name in ("vqgan.yaml", "vqgan.ckpt"):
        if not (tok / name).is_file():
            raise FileNotFoundError(f"missing {tok / name}")
    return tok


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


def _link_dir(dest: Path, target: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    target = target.resolve()
    if dest.is_symlink():
        if dest.resolve() == target:
            return
        dest.unlink()
    elif dest.exists():
        return
    dest.symlink_to(target, target_is_directory=True)


def _ensure_official_ckpts_layout() -> Path:
    """ItemProcessor hardcodes ``../ckpts/chameleon/tokenizer`` relative to CWD.

    Official eval CWD is ``rynnvla-002``. Point ``WorldVLA/ckpts/chameleon`` at
    the downloaded ``weights/WorldVLA/chameleon`` folder (which contains
    ``tokenizer/``).
    """
    tok_dir = find_chameleon_tokenizer_dir()
    chameleon_root = tok_dir.parent if tok_dir.name == "tokenizer" else tok_dir
    _link_dir(VENDOR / "ckpts" / "chameleon", chameleon_root)
    _link_dir(VENDOR / "rynnvla-002" / "ckpts" / "chameleon", chameleon_root)
    return tok_dir


def _ensure_hf_tokenizer_dir() -> Path:
    """xllmx Tokenizer wants tokenizer.json + tokenizer_config.json.

    Official eval passes the Lumina-mGPT-7B-768 snapshot. setup.sh downloads
    those tokenizer files. Fallback: save the raw Chameleon json as an HF folder.
    """
    def _usable(path: Path) -> bool:
        return (path / "tokenizer_config.json").is_file() and (
            (path / "tokenizer.json").is_file() or (path / "tokenizer.model").is_file()
        )

    for cand in (
        WEIGHTS / "Lumina-mGPT-7B-768",
        VENDOR
        / "ckpts"
        / "models--Alpha-VLLM--Lumina-mGPT-7B-768"
        / "snapshots"
        / "9624463a82ea5ce814af9b561dcd08a31082c3af",
    ):
        if _usable(cand):
            return cand
    hf_dir = WEIGHTS / "WorldVLA" / "chameleon" / "hf_tokenizer"
    if _usable(hf_dir):
        return hf_dir
    tok = _load_chameleon_tokenizer()
    hf_dir.mkdir(parents=True, exist_ok=True)
    tok.save_pretrained(str(hf_dir))
    if not _usable(hf_dir):
        raise FileNotFoundError(
            "Could not build an HF tokenizer folder. Re-run setup.sh "
            "(it now pulls Alpha-VLLM/Lumina-mGPT-7B-768 tokenizer files)."
        )
    return hf_dir


@contextmanager
def _rynnvla_cwd():
    _ensure_official_ckpts_layout()
    prev = os.getcwd()
    os.chdir(VENDOR / "rynnvla-002")
    try:
        yield
    finally:
        os.chdir(prev)


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


def _load_xllmx(ckpt: Path, force_sdpa: bool = True):
    """Official class for every published RynnVLA-002 card we pull.

    ``VLA_model_256/libero_goal`` ``config.json``:

        architectures: [ChameleonXLLMXForConditionalGeneration_ck_action_head]

    ``evals_libero/eval_libero_goal_his_2_third_view_wrist_w_state_5_256_abiw_discrete.sh``
    loads that class, then ``ItemProcessor`` + ``generate_dis_ma``. The HF
    ``model.vqmodel.encoder.*`` warning is expected: image tokens come from
    Meta ``vqgan.ckpt`` via ``ItemProcessor``, not from the LM's unused VQVAE.
    The published World / Action-World 512 cards use the same class.
    Do not override ``max_position_embeddings`` (VLA is 4096; world is 8192).
    Official WorldVLA ``requirements.txt`` pins ``transformers==4.43.0``.
    """
    _on_path()
    if not (VENDOR / "rynnvla-002" / "model" / "__init__.py").is_file():
        raise ImportError(
            f"vendor WorldVLA missing at {VENDOR}. "
            "In the rynn-worldvla venv: bash setup.sh"
        )
    from model import ChameleonXLLMXForConditionalGeneration_ck_action_head

    kwargs: dict[str, Any] = dict(
        torch_dtype=torch.bfloat16,
        mask_image_logits=False,
        dropout=0.05,
        z_loss_weight=1e-5,
        action_dim=7,
        time_horizon=5,
        device_map="cpu",
    )
    if force_sdpa:
        kwargs["attn_implementation"] = "sdpa"
    try:
        model = ChameleonXLLMXForConditionalGeneration_ck_action_head.from_pretrained(
            str(ckpt), **kwargs
        )
    except TypeError:
        kwargs.pop("attn_implementation", None)
        model = ChameleonXLLMXForConditionalGeneration_ck_action_head.from_pretrained(
            str(ckpt), **kwargs
        )
    model.eval()
    if torch.cuda.is_available():
        model = model.to("cuda")
    return model


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
    tok.sep_token_id = SEP_ID
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


def unnorm_action(action) -> np.ndarray:
    action = np.asarray(action, dtype=np.float64).reshape(-1)[:7]
    return (action + 1.0) / 2.0 * (_ACTION_MAX - _ACTION_MIN + 1e-8) + _ACTION_MIN


def _tensor_to_list(x) -> list:
    if x is None:
        return []
    if hasattr(x, "detach"):
        x = x.detach().cpu().float().numpy()
    arr = np.asarray(x)
    return arr.tolist()


class RynnSession:
    def __init__(self):
        self.tokenizer = _load_chameleon_tokenizer()
        self.vla = None
        self.world = None
        self._proc_vla = None
        self._proc_world = None
        self.last_act: dict[str, Any] | None = None
        self.force_sdpa = True
        rung = ROOT / ".rung"
        if rung.exists() and "flash_attn=1" in rung.read_text(encoding="utf-8"):
            self.force_sdpa = False
        _ensure_official_ckpts_layout()
        self._hf_tok_dir = _ensure_hf_tokenizer_dir()

    def _ensure_vla(self):
        if self.vla is None:
            self.vla = _load_xllmx(find_vla_ckpt(), force_sdpa=self.force_sdpa)
        return self.vla

    def _ensure_world(self):
        if self.world is None:
            self.world = _load_xllmx(find_world_ckpt(), force_sdpa=self.force_sdpa)
        return self.world

    def _item_processor_vla(self):
        if self._proc_vla is None:
            _on_path()
            from data.pre_tokenize_action_state import ItemProcessor

            with _rynnvla_cwd():
                self._proc_vla = ItemProcessor(
                    tokenizer=str(_ensure_hf_tokenizer_dir()),
                    target_size=VLA_RESOLUTION,
                )
        return self._proc_vla

    def _item_processor_world(self):
        if self._proc_world is None:
            _on_path()
            from data.pre_tokenize_action import ItemProcessor

            with _rynnvla_cwd():
                self._proc_world = ItemProcessor(
                    tokenizer=str(_ensure_hf_tokenizer_dir()),
                    target_size=WORLD_RESOLUTION,
                )
        return self._proc_world

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

    def act(
        self,
        third: Image.Image,
        wrist: Image.Image | None,
        instruction: str,
        state: np.ndarray | None = None,
    ) -> dict[str, Any]:
        """Official discrete LIBERO-goal railroad.

        ``get_action_Chameleon_dis_awm_ck_discrete_action`` in
        ``libero_util/Chameleon_utils.py``: ItemProcessor (state + wrist,
        256) then ``model.generate_dis_ma``. Not a text-only ``<|action|>``
        string. GIF frames have no proprio; default state is zeros(8).
        """
        if wrist is None:
            raise ValueError("this checkpoint is with_wrist; pass the wrist frame")
        model = self._ensure_vla()
        proc = self._item_processor_vla()
        if state is None:
            state = np.zeros(8, dtype=np.float64)
            state_note = "dummy zeros(8); GIF frames have no eef/gripper state"
        else:
            state = np.asarray(state, dtype=np.float64).reshape(-1)
            state_note = "caller-supplied"

        # First LIBERO step: empty history → current third + wrist only.
        # Official: get_action_Chameleon_dis_awm_ck_discrete_action
        torch.manual_seed(0)
        np.random.seed(0)
        tokens = None
        try:
            # Keep a copy of the official token ids for the notebook.
            human_val = (
                f"What action should the robot take to {instruction}?"
                + "<|state|>"
                + "<|image|>" * 2
            )
            conv = {
                "conversations": [{"from": "human", "value": human_val}],
                "image": [third, wrist],
                "action": [],
                "state": state,
            }
            tokens = proc.process_item(conv, training_mode=False)
        except Exception as exc:  # noqa: BLE001
            rec = {
                "sandbox": "rynn_worldvla",
                "turn": "act",
                "instruction": instruction,
                "reply": f"ItemProcessor failed: {exc}",
                "think": {"error": str(exc)},
                "action_ids": [],
                "third": "shown",
                "wrist": True,
            }
            append_log(rec)
            self.last_act = rec
            return rec

        generation_config = GenerationConfig(
            max_new_tokens=ACTION_STEPS * 12,
            max_length=model.config.max_position_embeddings,
            temperature=1,
            top_k=None,
            do_sample=False,
            eos_token_id=[SEP_ID],
        )
        input_ids = torch.tensor(tokens, dtype=torch.int64, device=model.device).unsqueeze(0)
        produced, chunks = _generate_dis_ma(model, input_ids, generation_config)
        n_act = sum(1 for i in produced if ACTION_START_ID < i < ACTION_END_ID)
        env_actions = []
        for ch in chunks:
            vec = np.asarray(_tensor_to_list(ch), dtype=np.float64).reshape(-1)
            if vec.size >= 7:
                env_actions.append(unnorm_action(vec[:7]))
        first = env_actions[0].tolist() if env_actions else None
        rec = {
            "sandbox": "rynn_worldvla",
            "turn": "act",
            "instruction": instruction,
            "reply": (
                f"{len(env_actions)} action chunk(s), {n_act} bin tokens of "
                f"{len(produced)}: {produced[:48]}"
                + (f"\n\nfirst env action (7-d): {first}" if first is not None else "")
            ),
            "think": {
                "class": "ChameleonXLLMXForConditionalGeneration_ck_action_head",
                "his": HIS_TYPE,
                "n_prompt_tokens": len(tokens),
                "produced_ids": produced[:64],
                "n_action_bin_tokens": n_act,
                "n_chunks": len(env_actions),
                "state_note": state_note,
                "vq_warning": (
                    "expected: model.vqmodel.* is unused; "
                    "ItemProcessor reads vqgan.ckpt"
                ),
                "official_fn": "get_action_Chameleon_dis_awm_ck_discrete_action",
            },
            "action_ids": produced,
            "actions_env": [a.tolist() for a in env_actions],
            "third": "shown",
            "wrist": True,
        }
        append_log(rec)
        self.last_act = rec
        return rec

    def dream(
        self,
        third: Image.Image,
        wrist: Image.Image | None,
        action_ids: list[int] | None = None,
        actions_env: list | None = None,
    ) -> dict[str, Any]:
        """Official world-model query: current third+wrist + action → next frames.

        ``get_action_Chameleon_dis_awm_g_video_wrist`` then
        ``item_processor.decode_image`` (Meta VQGAN).
        """
        if wrist is None:
            raise ValueError("world-model eval is bi-view; pass the wrist frame")
        model = self._ensure_world()
        proc = self._item_processor_world()
        if actions_env is None and self.last_act and self.last_act.get("actions_env"):
            actions_env = self.last_act["actions_env"]
        if actions_env:
            action = np.asarray(actions_env[0], dtype=np.float64).reshape(-1)[:7]
            action_note = "from act()"
        else:
            action = np.zeros(7, dtype=np.float64)
            action_note = "dummy zeros(7); pass actions_env from act()"

        from libero_util.Chameleon_utils import get_action_Chameleon_dis_awm_g_video_wrist

        torch.manual_seed(0)
        np.random.seed(0)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        third_path = LOG_DIR / "dream_input_third.png"
        wrist_path = LOG_DIR / "dream_input_wrist.png"
        third.save(third_path)
        wrist.save(wrist_path)
        next_front = LOG_DIR / "dream_next_third.png"
        next_wrist = LOG_DIR / "dream_next_wrist.png"
        try:
            g_front, g_wrist = get_action_Chameleon_dis_awm_g_video_wrist(
                model,
                "",
                proc,
                [third],
                [wrist],
                [action],
                "1a2i",
            )
            if g_front is not None:
                g_front.save(next_front)
            if g_wrist is not None:
                g_wrist.save(next_wrist)
            next_path = str(next_front) if g_front is not None else "no IMG start/end pair"
        except Exception as exc:  # noqa: BLE001
            next_path = f"vq-decode-failed: {exc}"
            g_front = None
        rec = {
            "sandbox": "rynn_worldvla",
            "turn": "dream",
            "reply": (
                "decoded next third+wrist PNGs"
                if g_front is not None
                else f"no decoded PNG ({next_path})"
            ),
            "think": {
                "class": "ChameleonXLLMXForConditionalGeneration_ck_action_head",
                "action_note": action_note,
                "action_env": action.tolist(),
                "unused_action_ids": (action_ids or [])[:16],
            },
            "input_frame": str(third_path),
            "input_wrist": str(wrist_path),
            "next_frame": next_path,
            "next_wrist": str(next_wrist) if g_wrist is not None else None,
            "official_script": "vendor/WorldVLA/rynnvla-002/exps_libero_world_model/eval_world_model_goal.sh",
        }
        append_log(rec)
        return rec


def _generate_dis_ma(model, input_ids, generation_config):
    """Official ``generate_dis_ma`` plus the raw new-token ids.

    Vendor helper drops the ids after decoding bin centers and can raise
    ``UnboundLocalError`` if no ``10004`` is emitted.
    """
    from model.chameleon import ChameleonForConditionalGeneration

    model.init_input_ids = None
    res = ChameleonForConditionalGeneration.generate(
        model,
        input_ids=input_ids,
        generation_config=generation_config,
        output_hidden_states=True,
        training=False,
        return_dict_in_generate=True,
    )
    dis_tokens = res["sequences"][:, input_ids.shape[1] :][0]
    decoded = model.decode_token_ids_to_actions(dis_tokens)
    sequences = []
    start_index = None
    for i, token in enumerate(dis_tokens):
        tid = int(token)
        if tid == ACTION_START_ID:
            start_index = i
        elif tid == ACTION_END_ID and start_index is not None:
            sequences.append(decoded[start_index + 1 : i])
            start_index = None
    return dis_tokens.detach().cpu().tolist(), sequences
