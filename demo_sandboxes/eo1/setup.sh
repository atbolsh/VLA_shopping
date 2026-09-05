#!/usr/bin/env bash
# Run only on a rented Blackwell box (RTX 5090 or RTX 5000). Not the notes machine.
set -euo pipefail

echo "============================================================"
echo " EO-1 setup"
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

_try python -m pip install "transformers>=4.49,<4.58"

if ! _try python -m pip install -r requirements.txt; then
  echo "requirements.txt failed (often torchcodec). Installing Hub import-time deps, then lerobot --no-deps."
  _try python -m pip install accelerate safetensors "huggingface-hub>=0.34.2,<1.0" pillow numpy einops sentencepiece protobuf \
    qwen-vl-utils ipykernel ipywidgets jupyter python-dotenv requests "transformers>=4.49,<4.58" \
    "datasets>=2.19.0,<=3.6.0" "diffusers>=0.27.2" "jsonlines>=4.0.0" "draccus==0.10.0" \
    "opencv-python-headless>=4.9.0" "av>=14.2.0"
  _try python -m pip install "lerobot==0.3.3" --no-deps
fi

# lerobot floats huggingface-hub to 1.x; transformers 4.57 needs <1.0.
_try python -m pip install "huggingface-hub>=0.34.2,<1.0"

# lerobot may replace the cu128 wheel with a CPU/cu126 build. Put ours back.
if [[ "$TORCH_RUNG" == "2.7.0+cu128" ]]; then
  _try python -m pip install "torch==2.7.0" "torchvision==0.22.0" --index-url "$CU128"
elif [[ "$TORCH_RUNG" == "2.8.0+cu128" ]]; then
  _try python -m pip install "torch==2.8.0" --index-url "$CU128"
  _try python -m pip install torchvision --index-url "$CU128"
fi

python - <<'PY'
import torch, sys
print("torch", torch.__version__, torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")
arch = torch.cuda.get_arch_list() if torch.cuda.is_available() else []
print("arch", arch)
if not any(a.startswith("sm_12") for a in arch):
    sys.exit("FAIL: no sm_120")
import lerobot
from lerobot.configs.types import FeatureType, NormalizationMode, PolicyFeature
from lerobot.policies.normalize import Normalize, Unnormalize
print("lerobot", getattr(lerobot, "__version__", "?"))
import huggingface_hub
from packaging.version import Version
print("huggingface_hub", huggingface_hub.__version__)
if Version(huggingface_hub.__version__) >= Version("1.0"):
    sys.exit("FAIL: huggingface-hub>=1.0 breaks transformers 4.57")
PY

mkdir -p vendor weights logs screenshot
if [[ -n "${HF_TOKEN:-}" ]]; then
  export HF_TOKEN
  export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
fi
export GIT_LFS_SKIP_SMUDGE=1

python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("IPEC-COMMUNITY/EO-1-3B", local_dir="weights/EO-1-3B", local_dir_use_symlinks=False)
print("downloaded IPEC-COMMUNITY/EO-1-3B")
PY


python download_frames.py
python -m ipykernel install --user --name eo1 --display-name "eo1"
{
  echo "torch=$TORCH_RUNG"
  echo "lerobot=0.3.3"
  echo "kernel=eo1"
} > .rung
echo "EO-1 setup done. Rung:"
cat .rung
echo "Open demo.ipynb with kernel eo1."
