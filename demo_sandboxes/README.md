# Demo sandboxes (vast.ai 5090 only)

Five independent projects. Each has its own `setup.sh`, `requirements.txt`, harness, and notebook. **Do not run any of these on the notes machine** (`LVA_shopping` workstation). Rent a box, copy the repo (or just this directory plus the repo-root `.env`), run `setup.sh` there.

The hosted InternNav Gradio ([InternRobotics/InternNav-Eval-Demo](https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo)) is down as of 2026-09-03 (401; thin UI over a remote backend). Do not use the unofficial sleeping clone. InternVLA-N1 is the official inference-only notebook in `internvla_n1/`.

## Box

- Template: Vast **Blackwell / CUDA 12.8** ([RTX 5 series](https://docs.vast.ai/rtx-5-series)).
- Default: **1× RTX 5090**, ~80 GB disk (weights are ~15–25 GB *per* sandbox you install).
- `internvla_n1` only: **2× RTX 5090** (DualVLN on `cuda:0`, System-2 chat on `cuda:1`).

Put `export HF_TOKEN=...` in the **repo-root** `.env` (copy [`.env.example`](../.env.example)). Each `setup.sh` symlinks it. The token is optional for these public cards; it only avoids Hub rate limits.

Every `setup.sh` aborts unless `nvidia-smi` reports an RTX 5090, or you set `FORCE_SETUP=1` on purpose.

## Try order (on the box)

| Order | Folder | Disk (weights, rough) | What you learn |
|---|---|---|---|
| 1 | [`jarvis_vqa`](jarvis_vqa/README.md) | ~16 GB | Leftover Qwen mouth on a screenshot |
| 2 | [`molmoact2`](molmoact2/README.md) | ~20 GB Think + ~16 GB Molmo2-ER | Depth-token think + official VQA |
| 3 | [`internvla_n1`](internvla_n1/README.md) | ~16 GB DualVLN + ~16 GB System2 | Pixel-goal + S2 text (2×5090) |
| 4 | [`rynn_worldvla`](rynn_worldvla/README.md) | ~16–25 GB | Action / next-frame / leftover BPE |
| 5 | [`jarvis_minestudio`](jarvis_minestudio/README.md) | same 7B as #1 if you reuse the cache | JDK 8 + vLLM + kbd/mouse |

Install **one folder at a time**. Do not `pip install` from this README.

After a sandbox works, append a `## Pull log` on the matching candidate card and leftover-English / mouth verdicts on [`notes/10_sibling_list.md`](../notes/10_sibling_list.md).
