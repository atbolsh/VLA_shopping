#!/usr/bin/env bash
# Run only on the rented 5090 box. Do not execute on the notes machine.
set -euo pipefail

echo "============================================================"
echo " INTERNVLA-N1 setup (2x5090)"
echo " Run only on the rented 5090 box. Do not execute on the notes machine."
echo "============================================================"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

if [[ "${FORCE_SETUP:-}" != "1" ]]; then
  if ! command -v nvidia-smi >/dev/null 2>&1 || ! nvidia-smi --query-gpu=name --format=csv,noheader | grep -qi "5090"; then
    echo "No RTX 5090. FORCE_SETUP=1 to override." >&2
    exit 1
  fi
  n="$(nvidia-smi --query-gpu=name --format=csv,noheader | grep -ci 5090 || true)"
  if [[ "$n" -lt 2 ]]; then
    echo "WARNING: this sandbox expects 2x5090 (DualVLN cuda:0, System2 cuda:1). Found $n."
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
for c in python3.10 python3; do command -v "$c" >/dev/null 2>&1 && PY="$c" && break; done
[[ -n "$PY" ]] || { echo "Need python3.10 (not 3.9 — their flash-attn wheel is cu124)."; exit 1; }
echo "Using $($PY --version) — official notebook was 3.9; we stay on 3.10 for cu128 wheels."

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
  echo "Intern frozen-stack torch rungs failed." >&2
  exit 1
fi

_try python -m pip install -r requirements.txt

FLASH=0
if _try python -m pip install flash-attn --no-build-isolation; then
  FLASH=1
else
  echo "flash-attn skipped; agent init will drop flash_attention_2 (official notebook allows this)."
fi

python - <<'PY'
import torch, sys, transformers
print("torch", torch.__version__, torch.cuda.get_device_name(0))
print("arch", torch.cuda.get_arch_list())
print("transformers", transformers.__version__)
assert transformers.__version__.startswith("4.51"), transformers.__version__
if not any(a.startswith("sm_12") for a in torch.cuda.get_arch_list()):
    sys.exit("FAIL: no sm_120")
PY

mkdir -p vendor
if [[ ! -d vendor/InternNav/.git ]]; then
  _try git clone --depth 1 https://github.com/InternRobotics/InternNav.git vendor/InternNav
fi
(cd vendor/InternNav && git submodule update --init --recursive)
_try python -m pip install -e vendor/InternNav

# Official sample RGB stream (no Habitat).
if [[ -f vendor/InternNav/assets/realworld_sample_data.tar.gz ]]; then
  mkdir -p assets
  tar -xvf vendor/InternNav/assets/realworld_sample_data.tar.gz -C assets || \
    tar -xvf vendor/InternNav/assets/realworld_sample_data.tar.gz -C vendor/InternNav/assets || true
fi

mkdir -p weights logs
if [[ -n "${HF_TOKEN:-}" ]]; then
  export HF_TOKEN
  export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
fi
python - <<'PY'
from huggingface_hub import snapshot_download
from pathlib import Path
snapshot_download("InternRobotics/InternVLA-N1-DualVLN", local_dir="weights/InternVLA-N1-DualVLN", local_dir_use_symlinks=False)
snapshot_download("InternRobotics/InternVLA-N1-System2", local_dir="weights/InternVLA-N1-System2", local_dir_use_symlinks=False)
# Official notebook names this DepthAnything card.
try:
    snapshot_download(
        "depth-anything/Depth-Anything-V2-Metric-Hypersim-Small",
        local_dir="weights/Depth-Anything-V2-Metric-Hypersim-Small",
        local_dir_use_symlinks=False,
    )
except Exception as exc:
    print("DepthAnything download skipped:", exc)
# Their notebook also looks under scripts/eval/checkpoints/checkpoints
dst = Path("vendor/InternNav/scripts/eval/checkpoints/checkpoints")
dst.mkdir(parents=True, exist_ok=True)
print("downloads done")
PY

python -m ipykernel install --user --name internvla-n1 --display-name "internvla-n1"
{
  echo "torch=$TORCH_RUNG"
  echo "transformers=4.51.0"
  echo "flash_attn=$FLASH"
  echo "gpu0=dualvln"
  echo "gpu1=system2"
} > .rung
echo "INTERNVLA-N1 setup done. Rung:"
cat .rung
echo "Hosted Gradio is down; this notebook is the official local replacement."
