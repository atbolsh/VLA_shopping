#!/usr/bin/env python3
"""Pull official (or clearly labelled stand-in) frames into screenshot/."""

from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "screenshot"
FILES = (
    ("top.jpg", "https://raw.githubusercontent.com/EO-Robotics/EO1/main/demo_data/example1.jpg"),
    ("left_wrist.jpg", "https://raw.githubusercontent.com/EO-Robotics/EO1/main/demo_data/example1.jpg"),
    ("right_wrist.jpg", "https://raw.githubusercontent.com/EO-Robotics/EO1/main/demo_data/example1.jpg"),
)


def _load_env() -> None:
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


def main() -> int:
    _load_env()
    OUT.mkdir(parents=True, exist_ok=True)
    for dest_name, url in FILES:
        dest = OUT / dest_name
        if dest.is_file() and dest.stat().st_size > 10_000:
            print(f"already {dest} ({dest.stat().st_size} B)", flush=True)
            continue
        print(f"GET {url}", flush=True)
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as exc:  # noqa: BLE001
            print(f"download failed: {exc}", file=sys.stderr)
            return 1
        print(f"wrote {dest} ({dest.stat().st_size} B)", flush=True)
    print(f"screenshot/ ready: {sorted(p.name for p in OUT.iterdir())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
