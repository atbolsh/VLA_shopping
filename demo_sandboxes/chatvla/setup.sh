#!/usr/bin/env bash
# Run only on a rented Blackwell box (RTX 5090 or RTX 5000). Not the notes machine.
set -euo pipefail

echo "============================================================"
echo " ChatVLA-1 setup"
echo " Run only on a rented Blackwell box (RTX 5090 or RTX 5000). Not the notes machine."
echo "============================================================"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

if [[ "${FORCE_SETUP:-}" != "1" ]]; then
  if ! command -v nvidia-smi >/dev/null 2>&1 || ! nvidia-smi --query-gpu=name --format=csv,noheader | grep -qiE '5090|RTX[[:space:]]*(PRO[[:space:]]*)?5000'; then
    echo "Need RTX 5090 or RTX 5000 (Blackwell). FORCE_SETUP=1 to override." >&2
    nvidia-smi --query-gpu=name --format=csv,noheader >&2 || true
    exit 1
  fi
fi

_try() { echo "+ $*"; "$@"; }

find_env_root() {
  local d="$HERE"
  if command -v git >/dev/null 2>&1; then
    local top
    top="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ -n "${top}" && ( -f "${top}/.env" || -f "${top}/.env.example" ) ]]; then
      echo "$top"; return 0
    fi
  fi
  while [[ "$d" != "/" ]]; do
    [[ -f "$d/.env" || -f "$d/.env.example" ]] && { echo "$d"; return 0; }
    d="$(dirname "$d")"
  done
  return 1
}

ENV_ROOT="$(find_env_root || true)"
[[ -n "${ENV_ROOT:-}" && -f "${ENV_ROOT}/.env" ]] || { echo "Need repo-root .env"; exit 1; }
ln -sfn "${ENV_ROOT}/.env" "${HERE}/.env"
set -a
# shellcheck disable=SC1091
source "${HERE}/.env"
set +a

PY=""
for c in python3.12 python3.11 python3.10 python3; do
  command -v "$c" >/dev/null 2>&1 && PY="$c" && break
done
[[ -n "$PY" ]] || { echo "Need python3.10+"; exit 1; }
echo "Using $($PY --version)"

[[ -d .venv ]] || "$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip wheel

CU128="https://download.pytorch.org/whl/cu128"
TORCH_RUNG=""
if _try python -m pip install "torch==2.7.0" "torchvision==0.22.0" --index-url "$CU128"; then
  TORCH_RUNG="2.7.0+cu128"
elif _try python -m pip install "torch==2.8.0" --index-url "$CU128"; then
  _try python -m pip install torchvision --index-url "$CU128"
  TORCH_RUNG="2.8.0+cu128"
else
  echo "cu128 torch rungs failed." >&2
  exit 1
fi

_try python -m pip install "transformers>=4.45,<4.52"

_try python -m pip install -r requirements.txt

python - <<'PY'
import torch, sys
print("torch", torch.__version__, torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")
arch = torch.cuda.get_arch_list() if torch.cuda.is_available() else []
print("arch", arch)
if not any(a.startswith("sm_12") for a in arch):
    sys.exit("FAIL: no sm_120")
PY

mkdir -p vendor weights logs screenshot
if [[ -n "${HF_TOKEN:-}" ]]; then
  export HF_TOKEN
  export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
fi
export GIT_LFS_SKIP_SMUDGE=1

if [[ ! -d vendor/ChatVLA_public/.git ]]; then
  _try git clone --depth 1 https://github.com/midea-ai/ChatVLA_public.git vendor/ChatVLA_public
fi
python - <<'PY'
from huggingface_hub import snapshot_download
from pathlib import Path
import shutil
snapshot_download("zzymeow/ChatVLA", local_dir="weights/ChatVLA", local_dir_use_symlinks=False)
# Official README: checkpoint must have preprocessor_config.json + chat_template.json
need = ("preprocessor_config.json", "chat_template.json")
w = Path("weights/ChatVLA")
if not all((w / n).is_file() for n in need):
    snapshot_download("Qwen/Qwen2-VL-2B-Instruct", local_dir="weights/Qwen2-VL-2B-Instruct", local_dir_use_symlinks=False)
    q = Path("weights/Qwen2-VL-2B-Instruct")
    for n in need:
        if not (w / n).is_file() and (q / n).is_file():
            shutil.copy2(q / n, w / n)
            print("copied", n, "from Qwen2-VL-2B-Instruct")
print("downloaded zzymeow/ChatVLA")
PY


python download_frames.py
python -m ipykernel install --user --name chatvla --display-name "chatvla"
{
  echo "torch=$TORCH_RUNG"
  echo "kernel=chatvla"
} > .rung
echo "ChatVLA-1 setup done. Rung:"
cat .rung
echo "Open demo.ipynb with kernel chatvla."
