#!/usr/bin/env bash
# Optional. Installs SimplerEnv (WidowX / Bridge visual matching) into this sandbox venv.
# Run on the rented Blackwell box, after setup.sh. Not the notes machine.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

if [[ ! -f .venv/bin/activate ]]; then
  echo "Need .venv from setup.sh first." >&2
  exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

mkdir -p vendor
if [[ ! -d vendor/SimplerEnv/.git ]]; then
  git clone --depth 1 --recurse-submodules https://github.com/simpler-env/SimplerEnv.git vendor/SimplerEnv
fi

python -m pip install "numpy>=1.24,<2" "transforms3d" "gymnasium"
python -m pip install -e vendor/SimplerEnv/ManiSkill2_real2sim
python -m pip install -e vendor/SimplerEnv

python - <<'PY'
import simpler_env
print("simpler_env tasks", [t for t in simpler_env.ENVIRONMENTS if t.startswith("widowx")])
PY

echo "SimplerEnv ready. Open play.ipynb (kernel ecot-openvla)."
echo "Headless Vulkan issues: see https://github.com/simpler-env/SimplerEnv#troubleshooting"
