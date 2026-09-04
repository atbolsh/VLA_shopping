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


def _read_safetensor_shards(ckpt: Path) -> tuple[dict[str, torch.Tensor], dict[str, Any]]:
    """Read every tensor the index lists. Fail if a shard is a stub or a key is absent."""
    from safetensors.torch import load_file

    index_path = ckpt / "model.safetensors.index.json"
    single = ckpt / "model.safetensors"
    if index_path.is_file():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        weight_map: dict[str, str] = index["weight_map"]
        shards = sorted(set(weight_map.values()))
        sd: dict[str, torch.Tensor] = {}
        bytes_on_disk = 0
        for shard in shards:
            path = ckpt / shard
            if not path.is_file():
                raise FileNotFoundError(path)
            bytes_on_disk += path.stat().st_size
            part = load_file(str(path), device="cpu")
            overlap = set(sd).intersection(part)
            if overlap:
                raise RuntimeError(f"duplicate tensor keys across shards: {sorted(overlap)[:8]}")
            sd.update(part)
        missing = [k for k in weight_map if k not in sd]
        extra = [k for k in sd if k not in weight_map]
        if missing:
            raise RuntimeError(f"index keys missing from shards: {missing[:12]}")
        if extra:
            raise RuntimeError(f"shard keys not in index: {extra[:12]}")
        expected = int((index.get("metadata") or {}).get("total_size") or 0)
    elif single.is_file():
        sd = load_file(str(single), device="cpu")
        bytes_on_disk = single.stat().st_size
        expected = bytes_on_disk
        shards = ["model.safetensors"]
    else:
        raise FileNotFoundError(f"no safetensors under {ckpt}")
    if bytes_on_disk < 8_000_000_000:
        raise RuntimeError(
            f"{ckpt} shards are only {bytes_on_disk} bytes (need ~14GB). "
            "Download is incomplete or an LFS pointer."
        )
    return sd, {
        "n_tensors": len(sd),
        "n_shards": len(shards),
        "bytes_on_disk": bytes_on_disk,
        "index_total_size": expected,
    }


def _vqgan_encoder_tensors() -> tuple[dict[str, torch.Tensor], Path]:
    """Meta VQGAN tensors, keyed as ``model.vqmodel.*``.

    Official convert copies every non-decoder key, then ``strict=False``.
    This ckpt also has ``custom_layer.*``, which HF ``ChameleonVQVAE`` does
    not define. Those extras stay out of the live module; every *live*
    ``model.vqmodel`` Parameter must still come from this file.
    """
    path = find_chameleon_tokenizer_dir() / "vqgan.ckpt"
    try:
        blob = torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:
        blob = torch.load(path, map_location="cpu")
    except Exception:
        blob = torch.load(path, map_location="cpu", weights_only=False)
    raw = blob["state_dict"] if isinstance(blob, dict) and "state_dict" in blob else blob
    mapped = {}
    for k, v in raw.items():
        if "decoder" in k or str(k).startswith("loss"):
            continue
        if not isinstance(v, torch.Tensor):
            continue
        mapped[f"model.vqmodel.{k}"] = v.contiguous()
    if not mapped:
        raise RuntimeError(f"no encoder tensors in {path}")
    return mapped, path


def _construct_model(config):
    from model import ChameleonXLLMXForConditionalGeneration_ck_action_head

    try:
        from accelerate import init_empty_weights

        with init_empty_weights():
            return ChameleonXLLMXForConditionalGeneration_ck_action_head(config)
    except Exception:
        return ChameleonXLLMXForConditionalGeneration_ck_action_head(config)


def _assert_live_matches_source(model, source: dict[str, torch.Tensor]) -> dict[str, Any]:
    """Every file tensor is on the module; every Parameter came from a file."""
    live = model.state_dict()
    skipped = sorted(k for k in source if k not in live)
    if skipped:
        raise RuntimeError(
            f"{len(skipped)} checkpoint tensors were not loaded (skipped): {skipped[:20]}"
        )
    param_names = [n for n, _ in model.named_parameters()]
    unloaded = [n for n in param_names if n not in source]
    if unloaded:
        raise RuntimeError(
            f"{len(unloaded)} Parameters have no file source (still random): {unloaded[:20]}"
        )
    meta = [
        n
        for n, p in model.named_parameters()
        if p.device.type == "meta"
    ]
    if meta:
        raise RuntimeError(f"{len(meta)} Parameters still on meta (never assigned): {meta[:20]}")
    mismatches = []
    for name, ref in source.items():
        tensor = live[name]
        if getattr(tensor, "device", None) is not None and tensor.device.type == "meta":
            mismatches.append(f"{name} still meta")
            continue
        if tuple(tensor.shape) != tuple(ref.shape):
            mismatches.append(f"{name} shape {tuple(tensor.shape)} != {tuple(ref.shape)}")
            continue
        if tensor.data_ptr() == ref.data_ptr() and tensor.device == ref.device:
            continue
        a = tensor.detach().float().cpu()
        b = ref.detach().to(device="cpu", dtype=tensor.dtype).float()
        if not torch.equal(a, b):
            delta = float((a - b).abs().max().item())
            mismatches.append(f"{name} max_abs={delta}")
    if mismatches:
        raise RuntimeError(f"{len(mismatches)} live tensors != files: {mismatches[:12]}")
    return {"n_verified": len(source), "n_parameters": len(param_names)}


def _load_xllmx(ckpt: Path, force_sdpa: bool = True):
    """Load published shards + vqgan.ckpt into the official class, strictly.

    Do not use ``from_pretrained`` here: it leaves ``model.vqmodel.*`` random
    (those keys are not in the VLA shards) and ``device_map`` can skip assigns.
    We read the safetensors ourselves, merge Meta ``vqgan.ckpt``, then
    ``load_state_dict(..., assign=True, strict=True)`` and compare every tensor
    to the files.
    """
    _on_path()
    if not (VENDOR / "rynnvla-002" / "model" / "__init__.py").is_file():
        raise ImportError(
            f"vendor WorldVLA missing at {VENDOR}. "
            "In the rynn-worldvla venv: bash setup.sh"
        )
    from model import ChameleonXLLMXConfig

    shard_sd, shard_info = _read_safetensor_shards(ckpt)
    vq_all, vq_path = _vqgan_encoder_tensors()

    config = ChameleonXLLMXConfig.from_pretrained(str(ckpt))
    if force_sdpa:
        config._attn_implementation = "sdpa"
    model = _construct_model(config)
    live_names = set(model.state_dict())
    vq_sd = {k: v for k, v in vq_all.items() if k in live_names}
    vq_extra = sorted(k for k in vq_all if k not in live_names)
    vq_live = [n for n in live_names if n.startswith("model.vqmodel.")]
    vq_unfilled = sorted(n for n in vq_live if n not in vq_sd)
    if vq_unfilled:
        raise RuntimeError(
            f"{len(vq_unfilled)} live model.vqmodel tensors have no vqgan source: "
            f"{vq_unfilled[:20]}"
        )
    overlap = set(shard_sd).intersection(vq_sd)
    if overlap:
        raise RuntimeError(f"VLA shards already contain VQ keys: {sorted(overlap)[:8]}")
    source = dict(shard_sd)
    source.update(vq_sd)
    shard_unmapped = sorted(k for k in shard_sd if k not in live_names)
    if shard_unmapped:
        raise RuntimeError(
            f"{len(shard_unmapped)} VLA shard tensors have no module slot "
            f"(would be skipped): {shard_unmapped[:20]}"
        )
    incompatible = model.load_state_dict(source, assign=True, strict=False)
    if incompatible.unexpected_keys:
        raise RuntimeError(
            f"{len(incompatible.unexpected_keys)} file tensors have no module slot "
            f"(skipped): {list(incompatible.unexpected_keys)[:20]}"
        )
    param_set = {n for n, _ in model.named_parameters()}
    missing_params = [k for k in incompatible.missing_keys if k in param_set]
    if missing_params:
        raise RuntimeError(
            f"{len(missing_params)} Parameters not in the files: {missing_params[:20]}"
        )
    report = _assert_live_matches_source(model, source)
    if not hasattr(model, "action_head"):
        raise RuntimeError("loaded class has no action_head")
    ah = float(model.action_head.action_token_embeddings.weight.float().norm().item())
    if ah == 0.0:
        raise RuntimeError("action_head embeddings are all zeros after load")
    model._rynn_load_report = {
        "ckpt": str(ckpt),
        "class": type(model).__name__,
        "shards": shard_info,
        "vqgan": str(vq_path),
        "n_vq_tensors": len(vq_sd),
        "vq_extra_not_on_module": vq_extra,
        "action_head_emb_norm": ah,
        **report,
    }
    print(
        "load verified",
        type(model).__name__,
        "tensors",
        report["n_verified"],
        "shard_bytes",
        shard_info["bytes_on_disk"],
        "vq",
        len(vq_sd),
        "vq_extra",
        vq_extra,
        "action_head_norm",
        f"{ah:.3f}",
    )
    model.eval()
    model = model.to(dtype=torch.bfloat16)
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
            pad_token_id=PAD,
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
                "load": getattr(model, "_rynn_load_report", None),
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
        """002 world-model query: current third+wrist + action → next frames.

        Trained prompt (``data/dataset.py`` task_type='world', with_wrist, and
        ``data/world_model_bi_views_conv_generation.py``, his=1):

            "Generate the next image based on the provided sequence of
            historical images and corresponding actions.<|image|><|image|><|action|>"

        with gpt = ``<|image|><|image|>``. The older vendor helper
        ``get_action_Chameleon_dis_awm_g_video_wrist`` uses a *different*
        WorldVLA-era prompt ("Generate the image based on the current image
        and the action.") — off-distribution for the RynnVLA-002 cards, and it
        produced malformed image blocks here. We build the trained conversation
        and call ``generate`` the way vendor ``generate_img`` does
        (``att_mask=None``, eos 8710), then decode each 8197…8196 block.
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

        torch.manual_seed(0)
        np.random.seed(0)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        third_path = LOG_DIR / "dream_input_third.png"
        wrist_path = LOG_DIR / "dream_input_wrist.png"
        third.save(third_path)
        wrist.save(wrist_path)

        conv = {
            "conversations": [
                {
                    "from": "human",
                    "value": (
                        "Generate the next image based on the provided sequence "
                        "of historical images and corresponding actions."
                        "<|image|><|image|><|action|>"
                    ),
                },
            ],
            "image": [third, wrist],
            "action": [action],
        }
        tokens = proc.process_item(conv, training_mode=False)
        generation_config = GenerationConfig(
            max_new_tokens=3000,
            max_length=model.config.max_position_embeddings,
            temperature=1,
            top_k=None,
            do_sample=False,
            eos_token_id=[SEP_ID],
            pad_token_id=PAD,
        )
        from model.chameleon import ChameleonForConditionalGeneration

        # prepare_inputs_for_generation drops training/att_mask kwargs, so
        # forward always runs its eval branch: generate_att_mask_3 over the
        # accumulated init_input_ids. Resetting the accumulator is mandatory
        # (vendor generate_img forgets to; generate_dis_ma resets it).
        model.init_input_ids = None
        input_ids = torch.tensor(tokens, dtype=torch.int64, device=model.device).unsqueeze(0)
        with torch.inference_mode():
            res = ChameleonForConditionalGeneration.generate(
                model,
                input_ids=input_ids,
                attention_mask=torch.ones_like(input_ids),
                generation_config=generation_config,
                return_dict_in_generate=True,
            )
        new_ids = res["sequences"][0, input_ids.shape[1]:].detach().cpu().tolist()
        blocks = _extract_image_blocks(new_ids)

        decoded: list[tuple[str, Image.Image]] = []
        block_errors: list[str] = []
        names = ("dream_next_third.png", "dream_next_wrist.png")
        for i, block in enumerate(blocks[:2]):
            try:
                img = proc.decode_image(list(block))
                out = LOG_DIR / names[i]
                img.save(out)
                decoded.append((str(out), img))
            except Exception as exc:  # noqa: BLE001
                block_errors.append(f"block {i} (len {len(block)}): {exc}")
        g_front_path = decoded[0][0] if len(decoded) >= 1 else None
        g_wrist_path = decoded[1][0] if len(decoded) >= 2 else None

        n_img_range = sum(1 for i in new_ids if IMG_LO <= i <= IMG_HI)
        rec = {
            "sandbox": "rynn_worldvla",
            "turn": "dream",
            "reply": (
                f"decoded {len(decoded)} of {len(blocks)} image block(s); "
                f"{n_img_range} image-range tokens of {len(new_ids)} generated"
                + (f"; decode errors: {block_errors}" if block_errors else "")
            ),
            "think": {
                "class": "ChameleonXLLMXForConditionalGeneration_ck_action_head",
                "prompt": "Generate the next image based on the provided sequence of historical images and corresponding actions.",
                "action_note": action_note,
                "action_env": action.tolist(),
                "n_prompt_tokens": len(tokens),
                "n_new_tokens": len(new_ids),
                "n_img_range_tokens": n_img_range,
                "block_lens": [len(b) for b in blocks],
                "block_errors": block_errors,
                "unused_action_ids": (action_ids or [])[:16],
            },
            "input_frame": str(third_path),
            "input_wrist": str(wrist_path),
            "next_frame": g_front_path or "no decodable front block",
            "next_wrist": g_wrist_path,
            "official_script": "vendor/WorldVLA/rynnvla-002/exps_libero_world_model/eval_world_model_goal.sh",
        }
        append_log(rec)
        return rec


def _extract_image_blocks(ids: list[int]) -> list[list[int]]:
    """Complete ``8197 … 8196`` spans, inclusive, in generation order."""
    IMG_START, IMG_END = 8197, 8196
    blocks: list[list[int]] = []
    start = None
    for i, t in enumerate(ids):
        if t == IMG_START:
            start = i
        elif t == IMG_END and start is not None:
            blocks.append(ids[start : i + 1])
            start = None
    return blocks


def _generate_dis_ma(model, input_ids, generation_config):
    """Official ``generate_dis_ma`` plus the raw new-token ids.

    Vendor helper drops the ids after decoding bin centers and can raise
    ``UnboundLocalError`` if no ``10004`` is emitted. ``init_input_ids``
    must be reset: forward's eval branch accumulates it for
    ``generate_att_mask_3`` on every step.
    """
    from model.chameleon import ChameleonForConditionalGeneration

    model.init_input_ids = None
    attn = torch.ones_like(input_ids)
    res = ChameleonForConditionalGeneration.generate(
        model,
        input_ids=input_ids,
        attention_mask=attn,
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
