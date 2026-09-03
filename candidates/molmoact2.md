---
id: molmoact2
name: MolmoAct2 / MolmoAct2-Think
tier: B-near-dual-mature
org: Ai2
params_b: 5
params_note: HF lists the SO-100/101 checkpoint at 5B. Backbone is Molmo2-ER plus a same-depth flow-matching action expert (L=36). Confirm exact split at pull; predecessor MolmoAct was 7B.
backbone: Molmo2-ER (embodied-reasoning Molmo 2)
system1: flow-matching action expert, conditioned on per-layer VLM KV; Think variant adds adaptive 10x10 depth tokens
dual_class: near_expert
dual_note: Not OpenHelix-true-dual. Think mode is a real slow-reason / fast-act split in time — depth tokens are only regenerated where RGB changed (cosine 0.996). That is the closest "watch the scene, stay silent" trick on a cheap-robot VLA.
open_weights: true
license: Apache-style / check HF (Ai2 is usually fully open)
hf:
  - https://huggingface.co/allenai/MolmoAct2
  - https://huggingface.co/allenai/MolmoAct2-SO100_101
  - https://huggingface.co/allenai/MolmoAct2-Think-LIBERO
  - https://huggingface.co/allenai/MolmoAct2-DROID
code:
  - https://github.com/allenai/molmoact2
  - https://github.com/allenai/molmoact
paper:
  - arXiv:2605.02881
  - arXiv:2508.07917
project: https://allenai.org/blog/molmoact2
videos:
  - https://allenai.org/blog/molmoact2
interactive: []
envs:
  - LIBERO
  - SimplerEnv (MolmoAct v1)
  - RoboEval
robots:
  - SO-100 / SO-101 (official finetune)
  - DROID Franka
  - Bimanual YAM
overnight: No world-model loop. They do VLM-relabel of robot datasets (Qwen3.5-27B) — a night-time *annotation* factory, not a dream factory.
reasoning_vs_gemma4_12b: near
scores:
  dual: 3
  reasoning: 4
  size_fit: 5
  env_play: 4
  cheap_robot: 5
  overnight: 2
  openness: 5
pull_priority: 3
survey_date: 2026-09-02
---

# MolmoAct2 / MolmoAct2-Think

Parseable spec: [`../notes/06_option_specs.md`](../notes/06_option_specs.md#3-molmoact2--molmoact2-think).

- **Network:** [allenai/MolmoAct2](https://huggingface.co/allenai/MolmoAct2); Think [MolmoAct2-Think-LIBERO](https://huggingface.co/allenai/MolmoAct2-Think-LIBERO); arm [MolmoAct2-SO100_101](https://huggingface.co/allenai/MolmoAct2-SO100_101).
- **Finetune just to start?** **No.** Think-LIBERO on [LIBERO](https://libero-project.github.io/). Your own arm/table later: light finetune.
- **World:** LIBERO $0. SO-101 DIY follower **$121.94** ([BOM](https://github.com/TheRobotStudio/SO-ARM100)).
- **Paper:** `2605.02881_molmoact2.pdf`

Best 2026 **open + cheap-robot + spatial reasoning** VLA. Dual purity is only "near," but Think's adaptive depth is philosophically close to VideoLLM-online's trained silence: do not re-reason the parts of the scene that did not change.

## Why it is on the list

- Official **SO-100/101** checkpoint trained on 1,222 public LeRobot datasets (filtered). That is criterion 4 done properly.
- Molmo2-ER is an embodied-reasoning VLM. The paper claims it beats GPT-5 and Gemini Robotics ER-1.5 on 13 *embodied* benches. That is not the same as Gemma-12B coding/planning, but it is the opposite of a dumb 3B PaliGemma.
- Fully open: weights, code, data, even a FAST tokenizer reimplementation.
- LIBERO numbers are at the top of the open pile (97.2% avg in the paper).

## Gaps vs the brief

- Near-dual, not Helix-shaped. The action expert rides the VLM KV; it does not have an independent 200 Hz camera loop.
- Navigation-in-a-house is not the native domain (tabletop / arm).
- 5B on the HF card is smaller than a 7B-class S2 — good for size, slightly more e4B-risk on *general* reasoning. Run Smoke 0.

## First pull

Third in the next-session **look** queue ([`09_next_session.md`](../notes/09_next_session.md)): watch the [blog](https://allenai.org/blog/molmoact2) after JARVIS-VLA and Chameleon/Rynn/WorldVLA, before InternVLA-N1 Gradio. Then `allenai/MolmoAct2-Think-LIBERO` as sandbox B. Read the adaptive-depth cache API; that is the bit that maps onto the sibling problem. SO-101 later.

## Pull log

```text
pulled: 2026-09-03
gpu: 1x RTX 5090
vram_gb: 32 (Think and Molmo2-ER OOM if both resident)
reasoning_smoke: not_run (Ask answered a table VQA; not Smoke 0)
env_smoke: not_tried (no closed-loop LIBERO)
notes: Molmo2-ER Ask talks. Think-LIBERO predict_action returned depth + a 10x7 action chunk on the official sample. Caution-sentence inject into task= did not produce follow-ups or a still arm. Do not treat Think as a talking S2. Sibling talk requires a separate gate (Molmo2-ER or Gemma 4 12B), not more prompt text on predict_action.
```
