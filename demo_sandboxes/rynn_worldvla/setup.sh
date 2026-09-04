#!/usr/bin/env bash
# Run only on the rented 5090 box. Do not execute on the notes machine.
set -euo pipefail

echo "============================================================"
echo " RYNN / WORLDVLA setup"
echo " Run only on the rented 5090 box. Do not execute on the notes machine."
echo "============================================================"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
WITH_LIBERO=0
for a in "$@"; do
  [[ "$a" == "--with-libero" ]] && WITH_LIBERO=1
done

if [[ "${FORCE_SETUP:-}" != "1" ]]; then
  if ! command -v nvidia-smi >/dev/null 2>&1 || ! nvidia-smi --query-gpu=name --format=csv,noheader | grep -qi "5090"; then
    echo "No RTX 5090. FORCE_SETUP=1 to override." >&2
    nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || true
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
  echo "Frozen-stack torch rungs failed." >&2
  exit 1
fi

_try python -m pip install -r requirements.txt
python - <<'PY'
import transformers
assert transformers.__version__.startswith("4.43"), transformers.__version__
print("transformers locked", transformers.__version__)
PY

FLASH=0
if _try python -m pip install flash-attn --no-build-isolation; then
  FLASH=1
else
  echo "flash-attn skipped; harness will force SDPA."
fi

python - <<'PY'
import torch, sys
print("torch", torch.__version__, "cuda", torch.version.cuda, torch.cuda.get_device_name(0))
arch = torch.cuda.get_arch_list()
print("arch", arch)
if not any(a.startswith("sm_12") for a in arch):
    sys.exit("FAIL: no sm_120")
PY

mkdir -p vendor
if [[ ! -d vendor/WorldVLA/.git ]]; then
  _try git clone --depth 1 https://github.com/alibaba-damo-academy/WorldVLA.git vendor/WorldVLA
fi
# editable after torch is locked
_try python -m pip install -e vendor/WorldVLA --no-deps || echo "WARNING: WorldVLA editable install skipped (layout may use rynnvla-002/)."

python - <<'PY'
import transformers
assert transformers.__version__.startswith("4.43"), transformers.__version__
print("transformers still", transformers.__version__)
PY

if [[ "$WITH_LIBERO" == "1" ]]; then
  echo "Optional LIBERO stage"
  export MUJOCO_GL="${MUJOCO_GL:-egl}"
  _try python -m pip install "mujoco==3.3.5" "robosuite==1.4.0" "bddl==3.6.0" "gym==0.26.2" || true
  if [[ ! -d vendor/LIBERO/.git ]]; then
    _try git clone --depth 1 https://github.com/Lifelong-Robot-Learning/LIBERO.git vendor/LIBERO
  fi
  _try python -m pip install -e vendor/LIBERO || echo "WARNING: LIBERO install failed."
fi

mkdir -p weights logs
if [[ -n "${HF_TOKEN:-}" ]]; then
  export HF_TOKEN
  export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
fi

python - <<'PY'
from huggingface_hub import snapshot_download
from pathlib import Path

# Tokenizer (token map in notes/11). One VLA suite + one world-model suite.
snapshot_download(
    "Alibaba-DAMO-Academy/WorldVLA",
    allow_patterns=["chameleon/tokenizer/**", "chameleon/tokenizer/*"],
    local_dir="weights/WorldVLA",
)
snapshot_download(
    "Alibaba-DAMO-Academy/RynnVLA-002",
    allow_patterns=[
        "VLA_model_256/libero_goal/**",
        "World_model_512/libero_goal/**",
        "Action_World_model_512/libero_goal/**",
    ],
    local_dir="weights/RynnVLA-002",
)
# Official ItemProcessor tokenizer. Not the 7B weights — json/config only.
try:
    snapshot_download(
        "Alpha-VLLM/Lumina-mGPT-7B-768",
        allow_patterns=[
            "tokenizer.json",
            "tokenizer_config.json",
            "special_tokens_map.json",
            "tokenizer.model",
        ],
        local_dir="weights/Lumina-mGPT-7B-768",
    )
except Exception as exc:
    print("WARNING: Lumina tokenizer download skipped:", exc)
print("weights present")
print("done download")
PY

# ItemProcessor hardcodes ../ckpts/chameleon/tokenizer from rynnvla-002.
mkdir -p vendor/WorldVLA/ckpts vendor/WorldVLA/rynnvla-002/ckpts
if [[ -d weights/WorldVLA/chameleon ]]; then
  ln -sfn "${HERE}/weights/WorldVLA/chameleon" vendor/WorldVLA/ckpts/chameleon
  ln -sfn "${HERE}/weights/WorldVLA/chameleon" vendor/WorldVLA/rynnvla-002/ckpts/chameleon
fi
if [[ -f weights/Lumina-mGPT-7B-768/tokenizer.json ]]; then
  snap_dir="vendor/WorldVLA/ckpts/models--Alpha-VLLM--Lumina-mGPT-7B-768/snapshots/9624463a82ea5ce814af9b561dcd08a31082c3af"
  mkdir -p "$(dirname "$snap_dir")"
  ln -sfn "${HERE}/weights/Lumina-mGPT-7B-768" "$snap_dir"
fi

python download_frames.py
python -m ipykernel install --user --name rynn-worldvla --display-name "rynn-worldvla"
{
  echo "torch=$TORCH_RUNG"
  echo "transformers=4.43.0"
  echo "flash_attn=$FLASH"
  echo "libero=$WITH_LIBERO"
} > .rung
echo "RYNN/WORLDVLA setup done. Rung:"
cat .rung
