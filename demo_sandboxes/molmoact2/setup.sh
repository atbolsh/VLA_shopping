#!/usr/bin/env bash
# Run only on the rented 5090 box. Do not execute on the notes machine.
set -euo pipefail

echo "============================================================"
echo " MOLMOACT2 setup"
echo " Run only on the rented 5090 box. Do not execute on the notes machine."
echo "============================================================"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
WITH_LEROBOT=0
for a in "$@"; do [[ "$a" == "--with-lerobot" ]] && WITH_LEROBOT=1; done

if [[ "${FORCE_SETUP:-}" != "1" ]]; then
  if ! command -v nvidia-smi >/dev/null 2>&1 || ! nvidia-smi --query-gpu=name --format=csv,noheader | grep -qi "5090"; then
    echo "No RTX 5090. FORCE_SETUP=1 to override." >&2
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
for c in python3.12 python3.11 python3; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
[[ -n "$PY" ]] || { echo "Need Python 3.11 or 3.12"; exit 1; }
echo "Using $($PY --version)"

[[ -d .venv ]] || "$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip wheel

mkdir -p vendor
# allenai/molmoact2 points a few test PNGs at Git LFS objects that 404.
# We need the Python, not the camera fixtures. Skip smudge always.
export GIT_LFS_SKIP_SMUDGE=1
if [[ ! -d vendor/molmoact2/.git ]]; then
  _try git clone --depth 1 https://github.com/allenai/molmoact2.git vendor/molmoact2
fi
if [[ ! -f vendor/molmoact2/pyproject.toml ]]; then
  echo "vendor/molmoact2 checkout incomplete (usually a dead LFS pointer). Restoring without LFS."
  _try git -C vendor/molmoact2 checkout -f HEAD
fi
if [[ ! -f vendor/molmoact2/pyproject.toml ]]; then
  echo "vendor/molmoact2 still missing pyproject.toml after restore." >&2
  exit 1
fi

CU128="https://download.pytorch.org/whl/cu128"
TORCH_RUNG=""
# Always pip into this folder's .venv. uv sync would land packages in
# vendor/molmoact2/.venv and, if pyproject still says cu121, hijack the index.
pyproject="vendor/molmoact2/pyproject.toml"
if grep -q 'cu121' "$pyproject" || grep -q '2.5.1' "$pyproject"; then
  echo "vendor pyproject still has cu121/2.5.1 — not calling uv."
fi
if _try python -m pip install "torch==2.11.0" "torchvision==0.26.0" --index-url "$CU128"; then
  TORCH_RUNG="2.11.0+cu128"
elif _try python -m pip install "torch==2.9.1" --index-url "$CU128"; then
  _try python -m pip install torchvision --index-url "$CU128"
  TORCH_RUNG="2.9.1+cu128"
else
  echo "Molmo 5090 torch rungs failed." >&2
  exit 1
fi
if ! _try python -m pip install "transformers==4.57.1"; then
  _try python -m pip install "transformers>=4.57,<4.58"
fi
_try python -m pip install -r requirements.txt

python - <<'PY'
import torch, sys
print("torch", torch.__version__, "cuda", torch.version.cuda, torch.cuda.get_device_name(0))
arch = torch.cuda.get_arch_list()
print("arch", arch)
if not any(a.startswith("sm_12") for a in arch):
    sys.exit("FAIL: no sm_120")
import transformers
print("transformers", transformers.__version__)
assert transformers.__version__.startswith("4.57"), transformers.__version__
PY

mkdir -p weights logs
if [[ -n "${HF_TOKEN:-}" ]]; then
  export HF_TOKEN
  export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
fi
python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("allenai/MolmoAct2-Think-LIBERO", local_dir="weights/MolmoAct2-Think-LIBERO", local_dir_use_symlinks=False)
snapshot_download("allenai/Molmo2-ER", local_dir="weights/Molmo2-ER", local_dir_use_symlinks=False)
print("downloaded Think-LIBERO + Molmo2-ER")
PY

python -m ipykernel install --user --name molmoact2 --display-name "molmoact2"

LEROBOT=0
if [[ "$WITH_LEROBOT" == "1" ]]; then
  ver="$($PY -c 'import sys; print(sys.version_info.minor)')"
  if [[ "$ver" -lt 12 ]]; then
    echo "lerobot==0.5.1 wants Python >=3.12 — skipping closed-loop venv."
  else
    "$PY" -m venv .venv-lerobot
    # shellcheck disable=SC1091
    source .venv-lerobot/bin/activate
    python -m pip install -U pip
    _try python -m pip install "torch==2.11.0" "torchvision==0.26.0" --index-url "$CU128" || true
    _try python -m pip install "lerobot==0.5.1" || echo "WARNING: lerobot install failed"
    deactivate
    # shellcheck disable=SC1091
    source .venv/bin/activate
    LEROBOT=1
  fi
fi

{
  echo "torch=$TORCH_RUNG"
  echo "transformers=4.57.x"
  echo "lerobot_venv=$LEROBOT"
} > .rung
echo "MOLMOACT2 setup done. Rung:"
cat .rung
