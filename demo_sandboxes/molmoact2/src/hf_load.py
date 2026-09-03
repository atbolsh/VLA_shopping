"""HF load shims for MolmoAct2 on transformers 4.57.x.

The Think-LIBERO / Molmo2 tokenizer_config stores extra_special_tokens as a
list. ProcessorMixin in 4.57 calls .keys() on that field (it wants a dict of
attribute names). The tokens themselves already live in the tokenizer vocab;
we drop the list so AutoProcessor can finish.
"""

from __future__ import annotations

import json
from pathlib import Path


def sanitize_tokenizer_config(weights: Path | str) -> None:
    path = Path(weights) / "tokenizer_config.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    extra = data.get("extra_special_tokens")
    if isinstance(extra, list):
        data["extra_special_tokens"] = {}
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_processor(weights: Path | str, **kwargs):
    from transformers import AutoProcessor

    sanitize_tokenizer_config(weights)
    kwargs.setdefault("trust_remote_code", True)
    kwargs.setdefault("extra_special_tokens", {})
    return AutoProcessor.from_pretrained(str(weights), **kwargs)
