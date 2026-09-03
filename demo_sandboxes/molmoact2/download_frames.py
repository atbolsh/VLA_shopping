#!/usr/bin/env python3
"""Pull the official Think-LIBERO sample cameras into screenshot/.

These are libero_10 / episode 0 / frame 0 from
allenai/MolmoAct2-Think-LIBERO (assets/sample_agentview_rgb.png and
sample_wrist_rgb.png). Not the orange/blue placeholders in assets/.

    source .venv/bin/activate
    python download_frames.py
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = "allenai/MolmoAct2-Think-LIBERO"
OUT = ROOT / "screenshot"
FILES = (
    "assets/sample_agentview_rgb.png",
    "assets/sample_wrist_rgb.png",
)


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        load_dotenv = None
    if load_dotenv is not None:
        load_dotenv(ROOT / ".env")
        return
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip().strip("'").strip('"'))


def _ok_png(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 10_000


def main() -> int:
    _load_env()
    OUT.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    local_root = ROOT / "weights" / "MolmoAct2-Think-LIBERO"
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        hf_hub_download = None

    for name in FILES:
        dest = OUT / Path(name).name
        if _ok_png(dest):
            print(f"already {dest} ({dest.stat().st_size} B)", flush=True)
            continue
        src = local_root / name
        if _ok_png(src):
            shutil.copy2(src, dest)
            print(f"copied {src} -> {dest} ({dest.stat().st_size} B)", flush=True)
            continue
        if hf_hub_download is None:
            print("need huggingface_hub to fetch official frames", file=sys.stderr)
            return 1
        path = Path(
            hf_hub_download(repo_id=REPO, filename=name, token=token)
        )
        shutil.copy2(path, dest)
        print(f"downloaded {name} -> {dest} ({dest.stat().st_size} B)", flush=True)
        if not _ok_png(dest):
            print(f"refusing tiny frame {dest}", file=sys.stderr)
            return 1

    print(f"screenshot/ ready: {sorted(p.name for p in OUT.glob('*.png'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
