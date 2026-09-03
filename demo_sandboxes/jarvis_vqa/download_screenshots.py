#!/usr/bin/env python3
"""Pull official Minecraft frames into screenshot/ for the leftover-mouth notebook.

Source is only CraftJarvis/minecraft-vla-sft **valid** (~1k rows, ~28 MB).
This script never downloads the 106 GB train split.

Run on the 5090 box, from this folder, with the sandbox venv active:

    source .venv/bin/activate
    python download_screenshots.py
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = "CraftJarvis/minecraft-vla-sft"
CACHE = ROOT / "weights" / "minecraft-vla-sft-valid"
OUT = ROOT / "screenshot"
DEFAULT_LIMIT = 80


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


def _ensure(mod: str, spec: str) -> None:
    try:
        __import__(mod)
    except ImportError:
        import subprocess

        print(f"installing {spec}", flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", spec])


def _slug(text: str, max_len: int = 48) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._")
    return (cleaned or "frame")[:max_len]


def _task(labels) -> str:
    if not labels:
        return "unknown"
    names = [x for x in labels if isinstance(x, str)]
    for name in names:
        if ":" in name:
            return name
    for name in names:
        if name not in {"trajectory", "RT2"}:
            return name
    return names[0]


def _image_bytes(raw) -> bytes | None:
    if raw is None:
        return None
    if isinstance(raw, (list, tuple)):
        raw = raw[0] if raw else None
    if raw is None:
        return None
    if isinstance(raw, memoryview):
        raw = raw.tobytes()
    if isinstance(raw, str):
        import base64

        raw = base64.b64decode(raw)
    data = bytes(raw)
    if data.startswith(b"\xff\xd8") or data.startswith(b"\x89PNG"):
        return data
    return None


def _valid_names(list_repo_files) -> list[str]:
    names = list_repo_files(REPO, repo_type="dataset")
    valid = [
        n
        for n in names
        if n.startswith("data/valid") or Path(n).name.startswith("valid-")
    ]
    if not valid:
        raise SystemExit(
            f"No data/valid* files on {REPO}. Refusing to touch train (106 GB)."
        )
    return sorted(valid)


def _pick_diverse(rows: list[dict], limit: int) -> list[dict]:
    by_task: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_task[_task(row.get("label"))].append(row)
    picked: list[dict] = []
    while len(picked) < limit and by_task:
        for task in list(by_task):
            bucket = by_task[task]
            if not bucket:
                by_task.pop(task, None)
                continue
            picked.append(bucket.pop(0))
            if len(picked) >= limit:
                break
    return picked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    _load_env()
    _ensure("huggingface_hub", "huggingface-hub==0.28.1")
    _ensure("pyarrow", "pyarrow")

    from huggingface_hub import hf_hub_download, list_repo_files
    import pyarrow.parquet as pq

    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    existing = sorted(
        p for p in out.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    if existing and not args.force and len(existing) >= args.limit:
        print(f"already have {len(existing)} frames in {out} (use --force to redo)")
        return 0

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    CACHE.mkdir(parents=True, exist_ok=True)
    print(f"listing {REPO} (valid split only)", flush=True)
    names = _valid_names(list_repo_files)
    print("valid files:", ", ".join(names), flush=True)
    local_parquets: list[Path] = []
    for name in names:
        path = hf_hub_download(
            repo_id=REPO,
            filename=name,
            repo_type="dataset",
            local_dir=str(CACHE),
            token=token,
        )
        local_parquets.append(Path(path))
        print(f"cached {path}", flush=True)

    rows: list[dict] = []
    for parquet_path in local_parquets:
        table = pq.read_table(parquet_path, columns=["id", "label", "image_bytes"])
        rows.extend(table.to_pylist())
    print(f"valid rows: {len(rows)}", flush=True)
    if not rows:
        raise SystemExit("valid split was empty")

    picked = _pick_diverse(rows, args.limit)
    saved = 0
    for i, row in enumerate(picked):
        data = _image_bytes(row.get("image_bytes"))
        if data is None:
            print(f"skip {row.get('id')}: not an image", flush=True)
            continue
        ext = ".png" if data.startswith(b"\x89PNG") else ".jpg"
        task = _slug(_task(row.get("label")))
        ident = _slug(str(row.get("id") or i), max_len=24)
        dest = out / f"{i:03d}_{task}_{ident}{ext}"
        if dest.exists() and not args.force:
            saved += 1
            continue
        dest.write_bytes(data)
        saved += 1
        print(f"wrote {dest.name}", flush=True)

    print(f"screenshot/ now has {saved} frames (wanted {args.limit})")
    return 0 if saved else 1


if __name__ == "__main__":
    raise SystemExit(main())
