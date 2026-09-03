#!/usr/bin/env bash
# Run only on the rented 5090 box. Do not execute on the notes machine.
set -euo pipefail

echo "============================================================"
echo " JARVIS-VQA setup"
echo " Run only on the rented 5090 box. Do not execute on the notes machine."
echo "============================================================"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

if [[ "${FORCE_SETUP:-}" != "1" ]]; then
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "nvidia-smi missing. This script is for a 5090 box. FORCE_SETUP=1 to override." >&2
    exit 1
  fi
  if ! nvidia-smi --query-gpu=name --format=csv,noheader | grep -qi "5090"; then
    echo "No RTX 5090 reported by nvidia-smi:" >&2
    nvidia-smi --query-gpu=name --format=csv,noheader >&2 || true
    echo "FORCE_SETUP=1 to override." >&2
    exit 1
  fi
fi

_try() {
  echo "+ $*"
  "$@"
}

find_env_root() {
  local d="$HERE"
  if command -v git >/dev/null 2>&1; then
    local top
    top="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ -n "${top}" && ( -f "${top}/.env" || -f "${top}/.env.example" ) ]]; then
      echo "$top"
      return 0
    fi
  fi
  while [[ "$d" != "/" ]]; do
    if [[ -f "$d/.env" || -f "$d/.env.example" ]]; then
      echo "$d"
      return 0
    fi
    d="$(dirname "$d")"
  done
  return 1
}

ENV_ROOT="$(find_env_root || true)"
if [[ -z "${ENV_ROOT:-}" ]]; then
  echo "Could not find repo-root .env / .env.example by walking parents." >&2
  exit 1
fi
if [[ ! -f "${ENV_ROOT}/.env" ]]; then
  echo "No ${ENV_ROOT}/.env — copy .env.example and set HF_TOKEN if you have one." >&2
  exit 1
fi
ln -sfn "${ENV_ROOT}/.env" "${HERE}/.env"
set -a
# shellcheck disable=SC1091
source "${HERE}/.env"
set +a

PY=""
for c in python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1; then
    PY="$c"
    break
  fi
done
if [[ -z "$PY" ]]; then
  echo "Need python3.10 (official JarvisVLA) or python3." >&2
  exit 1
fi
echo "Using $($PY --version)"

if [[ ! -d .venv ]]; then
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip wheel

CU128="https://download.pytorch.org/whl/cu128"

install_torch() {
  local spec="$1"
  if [[ "$spec" == "latest" ]]; then
    _try python -m pip install torch torchvision --index-url "$CU128"
  else
    _try python -m pip install "torch==${spec}" --index-url "$CU128"
    _try python -m pip install torchvision --index-url "$CU128"
  fi
}

TORCH_RUNG=""
if install_torch latest; then
  TORCH_RUNG="latest-cu128"
elif install_torch 2.9.1; then
  TORCH_RUNG="2.9.1+cu128"
elif install_torch 2.8.0; then
  TORCH_RUNG="2.8.0+cu128"
else
  echo "All torch rungs failed." >&2
  exit 1
fi

TF_RUNG=""
if _try python -m pip install "transformers==4.49.0"; then
  TF_RUNG="4.49.0"
elif _try python -m pip install "transformers==4.45.2"; then
  TF_RUNG="4.45.2"
elif _try python -m pip install transformers; then
  TF_RUNG="unpinned"
else
  echo "transformers install failed." >&2
  exit 1
fi

_try python -m pip install -r requirements.txt

python - <<'PY'
import torch, sys
print("torch", torch.__version__, "cuda", torch.version.cuda)
print("device", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")
arch = torch.cuda.get_arch_list() if torch.cuda.is_available() else []
print("arch", arch)
ok = any(a in ("sm_120", "sm_121") or a.startswith("sm_12") for a in arch)
if not ok:
    print("FAIL: no sm_120-class arch in", arch, file=sys.stderr)
    sys.exit(1)
PY

mkdir -p weights logs
if [[ -n "${HF_TOKEN:-}" ]]; then
  export HF_TOKEN
  export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
fi
if [[ ! -d weights/JarvisVLA-Qwen2-VL-7B ]]; then
  python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download(
    "CraftJarvis/JarvisVLA-Qwen2-VL-7B",
    local_dir="weights/JarvisVLA-Qwen2-VL-7B",
    local_dir_use_symlinks=False,
)
print("downloaded CraftJarvis/JarvisVLA-Qwen2-VL-7B")
PY
fi

python -m ipykernel install --user --name jarvis-vqa --display-name "jarvis-vqa"
python download_screenshots.py
printf 'torch=%s\ntransformers=%s\n' "$TORCH_RUNG" "$TF_RUNG" > .rung
echo "JARVIS-VQA setup done. Rung:"
cat .rung
echo "Open demo.ipynb with kernel jarvis-vqa. Pick a frame from screenshot/."
