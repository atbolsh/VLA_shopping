#!/usr/bin/env bash
# Run only on the rented 5090 box. Starts official vLLM serve for JarvisVLA.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi
# shellcheck disable=SC1091
source .venv/bin/activate
WEIGHTS="${HERE}/weights/JarvisVLA-Qwen2-VL-7B"
if [[ ! -d "$WEIGHTS" ]]; then
  echo "Missing $WEIGHTS — run setup.sh first." >&2
  exit 1
fi
if grep -q 'vllm=degraded' .rung 2>/dev/null; then
  echo "This install landed on degraded HF generate. Do not start vllm." >&2
  exit 1
fi
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
exec vllm serve "$WEIGHTS" --port 8000 --trust-remote-code --dtype bfloat16
