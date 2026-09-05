# Demo sandboxes (vast.ai Blackwell: RTX 5090 or RTX 5000)

Four independent projects. Each has its own `setup.sh`, `requirements.txt`, harness, and notebook. **Do not run any of these on the notes machine** (`LVA_shopping` workstation). Rent a box, copy the repo (or just this directory plus the repo-root `.env`), run `setup.sh` there.

The 2026-09-03/04 crop (JARVIS, Molmo, Rynn, InternVLA-N1) was **rejected** and **deleted**. InternVLA-N1 is never the next box.

Success is: the **same policy weights** print a readable English intermediate goal **and** an action. No second VLM. No RoboBrain / Pelican-VL / System-2-only chat.

None of these four are interruptible (no async S1). **Start with EO-1.** EO-1 and ECoT stills are on-distribution (official demo / Bridge). ChatVLA and WALL-OSS use labelled stand-in frames.

## Box

- Template: Vast **Blackwell / CUDA 12.8** ([RTX 5 series](https://docs.vast.ai/rtx-5-series)).
- Default: **1× RTX 5090 or RTX 5000** (same CUDA 12.8 / `sm_120`; 5000 has more VRAM), ~80 GB disk (weights are ~6–16 GB *per* sandbox you install).

Put `export HF_TOKEN=...` in the **repo-root** `.env` (copy [`.env.example`](../.env.example)). Each `setup.sh` symlinks it. The token is optional for these public cards; it only avoids Hub rate limits.

Every `setup.sh` aborts unless `nvidia-smi` reports an RTX 5090 or RTX 5000 (including RTX PRO 5000), or you set `FORCE_SETUP=1` on purpose. Ada “RTX 5000” cards fail the later `sm_120` check.

## Try order (on the box)

| Order | Folder | Disk (weights, rough) | What you learn |
|---|---|---|---|
| 1 | [`eo1`](eo1/README.md) | ~8 GB | Official `processor.generate`: text **and** action from `EO-1-3B`. Closed-loop: `play.ipynb` on WidowX / Bridge. |
| 2 | [`chatvla`](chatvla/README.md) | ~6 GB | Official `evaluate` on ChatVLA-1. ChatVLA-2 has no robot weights. |
| 3 | [`wall_oss`](wall_oss/README.md) | ~8 GB | Uni-CoT claim on `wall-oss-flow`. Official scripts are action-first. |
| 4 | [`ecot_openvla`](ecot_openvla/README.md) | ~14 GB | TASK/PLAN/SUBTASK English + Bridge action. Closed-loop: `play.ipynb`. |

Install **one folder at a time**. Do not `pip install` from this README.

After a sandbox works, append leftover-English / mouth verdicts on [`notes/10_sibling_list.md`](../notes/10_sibling_list.md) and the next-session note.