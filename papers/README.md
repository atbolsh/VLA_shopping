# Papers

PDFs in `pdfs/`, named `<arxiv-id>_<shortname>.pdf`. Survey date 2026-09-02.

Sibling copies (same files may already live in `../../stateful_realtime_thinking/papers/pdfs/`): GR00T N1, OpenHelix, π0, RTC.

| File | Paper | Why it is here |
|---|---|---|
| `2505.03912_openhelix.pdf` | OpenHelix survey + model | Dual-system definition this repo uses; Path K kit |
| `2410.08001_robodual.pdf` | RoboDual | 7B true dual, action-space handoff |
| `2506.01953_fis_vla.pdf` | Fast-in-Slow | Embedded S1; activation-as-plan |
| `2412.04453_navila.pdf` | NaVILA | Hierarchical nav dual, Go2 |
| `2503.14734_groot_n1.pdf` | GR00T N1 | Dual-ish humanoid VLA; N1.7 is the pull |
| `2410.24164_pi0.pdf` | π0 | Flow-matching VLA that π0.5 / OneTwoVLA sit on |
| `2504.16054_pi05.pdf` | π0.5 | Open-world π; hierarchy not in open weights |
| `2506.07339_real_time_chunking.pdf` | RTC | Overlap think and act |
| `2605.02881_molmoact2.pdf` | MolmoAct2 | Cheap-robot + Think + Molmo2-ER |
| `2508.07917_molmoact.pdf` | MolmoAct v1 | Predecessor, 7B action-reasoning |
| `2502.13130_magma.pdf` | Magma-8B | Generalist 8B baseline |
| `2505.11917_onetwovla.pdf` | OneTwoVLA | Behavioral switch + synthetic VL |
| `2406.09246_openvla.pdf` | OpenVLA | RoboDual dependency |
| `2506.01844_smolvla.pdf` | SmolVLA | Negative control / arm bring-up |
| `2504.19854_nora.pdf` | NORA | 3B Qwen2.5-VL, no dual |
| `2405.04798_lcb.pdf` | Latent Codes as Bridges | `<ACT>` token origin |
| `2410.05273_hirt.pdf` | HiRT | Earlier true dual |
| `dreamgen_page.md` | DreamGen project notes | Overnight factory (PDF if the arXiv id is confirmed locally) |

Non-arXiv / HTML:

| Link | What |
|---|---|
| https://internrobotics.github.io/internvla-n1.github.io/static/pdfs/InternVLA_N1.pdf | InternVLA-N1 tech report |
| https://www.figure.ai/news/helix | Helix blog (no paper) |
| https://research.nvidia.com/labs/gear/dreamgen/ | DreamGen |
| https://nvidia-cosmos.github.io/cosmos-cookbook/recipes/end2end/gr00t-dreams/post-training.html | Dreams cookbook |

PDFs live in `pdfs/` and **are tracked in git** (~240 MB). Re-fetch with `scripts/fetch_papers.sh` if a file is missing (the script sends a user-agent; bare curl gets arXiv 403).

If a download failed, the row stays in this table and the PDF is absent.
