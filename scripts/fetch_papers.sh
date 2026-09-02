#!/usr/bin/env bash
# Download shopping-list PDFs into papers/pdfs/. Safe to re-run.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/papers/pdfs"
mkdir -p "$DEST"
UA="Mozilla/5.0 (compatible; LVA-shopping/1.0; research notes)"

fetch() {
  local id="$1"
  local name="$2"
  local out="$DEST/${id}_${name}.pdf"
  if [[ -f "$out" && -s "$out" ]]; then
    echo "have $out"
    return 0
  fi
  echo "get  $out"
  curl -fsSL -L -A "$UA" --retry 3 --retry-delay 2 "https://arxiv.org/pdf/${id}.pdf" -o "$out"
}

fetch 2505.03912 openhelix
fetch 2410.08001 robodual
fetch 2506.01953 fis_vla
fetch 2412.04453 navila
fetch 2503.14734 groot_n1
fetch 2410.24164 pi0
fetch 2504.16054 pi05
fetch 2506.07339 real_time_chunking
fetch 2605.02881 molmoact2
fetch 2508.07917 molmoact
fetch 2502.13130 magma
fetch 2505.11917 onetwovla
fetch 2406.09246 openvla
fetch 2506.01844 smolvla
fetch 2504.19854 nora
fetch 2405.04798 lcb
fetch 2410.05273 hirt

# InternVLA-N1 tech report (not arXiv).
N1="$DEST/internvla_n1_techreport.pdf"
if [[ ! -f "$N1" ]]; then
  echo "get  $N1"
  curl -fsSL -L -A "$UA" "https://internrobotics.github.io/internvla-n1.github.io/static/pdfs/InternVLA_N1.pdf" -o "$N1" \
    || echo "WARN: InternVLA-N1 PDF failed"
fi

echo "done"
