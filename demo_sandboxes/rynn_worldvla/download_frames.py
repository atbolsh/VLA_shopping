#!/usr/bin/env python3
"""Pull official RynnVLA-002 LIBERO frames into screenshot/.

First frame of the WorldVLA README pair
``pickuptheblackbowlandplaceitontheplate_{front,wrist}.gif``
(matches the notebook instruction). Not the orange/blue placeholders.

    source .venv/bin/activate
    python download_frames.py
"""

from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
VENDOR_ASSETS = ROOT / "vendor" / "WorldVLA" / "rynnvla-002" / "assets"
OUT = ROOT / "screenshot"
GITHUB = (
    "https://raw.githubusercontent.com/alibaba-damo-academy/WorldVLA/"
    "main/rynnvla-002/assets/"
)
PAIRS = (
    ("pickuptheblackbowlandplaceitontheplate_front.gif", "sample_third.png"),
    ("pickuptheblackbowlandplaceitontheplate_wrist.gif", "sample_wrist.png"),
)


def _ok_png(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 10_000:
        return False
    im = Image.open(path)
    return len(set(im.convert("RGB").getdata())) > 16


def _first_frame(gif: Path, dest: Path) -> None:
    im = Image.open(gif)
    im.seek(0)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(dest)


def _fetch_gif(name: str) -> Path:
    local = VENDOR_ASSETS / name
    if local.is_file() and local.stat().st_size > 10_000:
        return local
    dest = OUT / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {name}", flush=True)
    urllib.request.urlretrieve(GITHUB + name, dest)
    return dest


def main() -> int:
    os.chdir(ROOT)
    OUT.mkdir(parents=True, exist_ok=True)
    for gif_name, png_name in PAIRS:
        dest = OUT / png_name
        if _ok_png(dest):
            print(f"already {dest} ({dest.stat().st_size} B)", flush=True)
            continue
        gif = _fetch_gif(gif_name)
        _first_frame(gif, dest)
        print(f"{gif.name} frame 0 -> {dest} ({dest.stat().st_size} B)", flush=True)
        if not _ok_png(dest):
            print(f"refusing tiny/flat frame {dest}", file=sys.stderr)
            return 1
    print(f"screenshot/ ready: {sorted(p.name for p in OUT.glob('*.png'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
