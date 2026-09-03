#!/usr/bin/env bash
# Optional closed loop in the *separate* .venv-lerobot. Not the Think/VQA env.
# Run only on the rented 5090 box.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
if [[ ! -d .venv-lerobot ]]; then
  echo "No .venv-lerobot. Re-run: bash setup.sh --with-lerobot (Python >=3.12)." >&2
  exit 1
fi
# shellcheck disable=SC1091
source .venv-lerobot/bin/activate
export MUJOCO_GL="${MUJOCO_GL:-egl}"
export PYOPENGL_PLATFORM="${PYOPENGL_PLATFORM:-egl}"
exec lerobot-eval \
  --policy.type=molmoact2 \
  --policy.checkpoint_path="${HERE}/weights/MolmoAct2-Think-LIBERO" \
  --policy.norm_tag=libero \
  --policy.inference_action_mode=continuous \
  --env.type=libero \
  --env.task=libero_object \
  --eval.n_episodes=1
