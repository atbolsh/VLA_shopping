#!/usr/bin/env bash
# Run only on the rented 5090 box. Do not execute on the notes machine.
set -euo pipefail

echo "============================================================"
echo " JARVIS-MINESTUDIO setup"
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
    echo "No RTX 5090 reported by nvidia-smi." >&2
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
if [[ -z "${ENV_ROOT:-}" || ! -f "${ENV_ROOT}/.env" ]]; then
  echo "Need repo-root .env (copy .env.example)." >&2
  exit 1
fi
ln -sfn "${ENV_ROOT}/.env" "${HERE}/.env"
set -a
# shellcheck disable=SC1091
source "${HERE}/.env"
set +a

# --- JDK 8 ---
if ! java -version 2>&1 | grep -q '1\.8'; then
  if command -v conda >/dev/null 2>&1; then
    _try conda install --yes --channel=conda-forge openjdk=8 || true
  fi
  if ! java -version 2>&1 | grep -q '1\.8'; then
    if command -v apt-get >/dev/null 2>&1; then
      echo "Trying apt openjdk-8-jdk (may need sudo)."
      sudo apt-get update && sudo apt-get install -y openjdk-8-jdk || apt-get install -y openjdk-8-jdk || true
    fi
  fi
fi
java -version || echo "WARNING: Java not confirmed as 1.8. MineStudio may fail."

# --- display ---
if command -v Xvfb >/dev/null 2>&1; then
  echo "Xvfb present."
elif command -v apt-get >/dev/null 2>&1; then
  sudo apt-get install -y xvfb mesa-utils || apt-get install -y xvfb || echo "WARNING: install xvfb yourself."
else
  echo "WARNING: no Xvfb. Try MINESTUDIO_GPU_RENDER=1 + VirtualGL."
fi

PY=""
for c in python3.10 python3; do
  command -v "$c" >/dev/null 2>&1 && PY="$c" && break
done
[[ -n "$PY" ]] || { echo "Need python3.10"; exit 1; }

[[ -d .venv ]] || "$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip wheel

assert_sm120() {
  python - <<'PY'
import torch, sys
print("torch", torch.__version__, "cuda", torch.version.cuda)
print("device", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")
arch = torch.cuda.get_arch_list() if torch.cuda.is_available() else []
print("arch", arch)
if not any(a.startswith("sm_12") for a in arch):
    print("FAIL: no sm_120-class arch", arch, file=sys.stderr)
    sys.exit(1)
PY
}

VLLM_RUNG=""
if _try python -m pip install vllm; then
  VLLM_RUNG="current"
elif _try python -m pip install "vllm==0.10.2"; then
  VLLM_RUNG="0.10.2"
elif _try python -m pip install "vllm==0.9.2"; then
  VLLM_RUNG="0.9.2"
else
  VLLM_RUNG="degraded-hf-generate"
  echo "vLLM failed. Installing latest cu128 torch for the HF one-step fallback."
  _try python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
  _try python -m pip install transformers
fi

if [[ "$VLLM_RUNG" != "degraded-hf-generate" ]]; then
  assert_sm120
fi

if _try python -m pip install minestudio; then
  echo "minestudio from PyPI"
elif _try python -m pip install "git+https://github.com/CraftJarvis/MineStudio.git"; then
  echo "minestudio from git"
else
  echo "WARNING: minestudio install failed. Simulator cells will not run."
fi

_try python -m pip install -r requirements.txt

mkdir -p vendor
if [[ ! -d vendor/JarvisVLA/.git ]]; then
  _try git clone --depth 1 https://github.com/CraftJarvis/JarvisVLA.git vendor/JarvisVLA
fi
_try python -m pip install -e vendor/JarvisVLA --no-deps

assert_sm120 || {
  echo "sm_120 lost after vendor install — refusing to continue." >&2
  exit 1
}

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
print("downloaded weights")
PY
fi

python -m ipykernel install --user --name jarvis-minestudio --display-name "jarvis-minestudio"
printf 'vllm=%s\n' "$VLLM_RUNG" > .rung
echo "JARVIS-MINESTUDIO setup done. Rung:"
cat .rung
if [[ "$VLLM_RUNG" == "degraded-hf-generate" ]]; then
  echo "DEGRADED: notebook will use HF generate, not vllm serve."
else
  echo "Start the server with: bash serve.sh"
fi
