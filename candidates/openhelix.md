---
id: openhelix
name: OpenHelix
tier: A-true-dual-7b
org: Westlake / OpenHelix-robot
params_b: 7
params_note: LLaVA-1.5-7B frozen + 3D Diffuser Actor specialist + linear 4096→512 projector + learned <ACT> token. MIT.
backbone: LLaVA-1.5-7B
system1: 3D Diffuser Actor (RGB + proprio + point cloud), pretrained then finetuned
dual_class: true_async
dual_note: The open reproduction of Helix-style dual systems, plus the taxonomy this repo uses. Async eval script `asy10`. S1 has its own sensors. This is the kit.
open_weights: true
license: MIT
hf:
  - https://huggingface.co/OpenHelix/openhelix
code:
  - https://github.com/OpenHelix-robot/OpenHelix
paper:
  - arXiv:2505.03912
project: https://openhelix-robot.github.io/
videos:
  - https://openhelix-robot.github.io/
interactive: []
envs:
  - CALVIN ABC-D
robots:
  - CALVIN Franka tabletop (sim)
overnight: none
reasoning_vs_gemma4_12b: below_reject
scores:
  dual: 5
  reasoning: 2
  size_fit: 5
  env_play: 4
  cheap_robot: 1
  overnight: 2
  openness: 5
pull_priority: 7
survey_date: 2026-09-02
---

# OpenHelix

Parseable spec: [`../notes/06_option_specs.md`](../notes/06_option_specs.md#7-openhelix).

- **Network:** Frozen LLaVA-1.5-7B + 3DDA `policy.pth` in [OpenHelix/openhelix](https://huggingface.co/OpenHelix/openhelix). Code: [OpenHelix-robot/OpenHelix](https://github.com/OpenHelix-robot/OpenHelix).
- **Finetune just to start?** **No.** Released ckpt on [CALVIN](http://calvin.cs.uni-freiburg.de/) (merge shards). Gemma graft later: train the projector.
- **World:** [CALVIN](http://calvin.cs.uni-freiburg.de/), $0. No SO-101.
- **Paper:** `2505.03912_openhelix.pdf`

Do not pull this for intelligence. Pull it as **the reference implementation** of a true dual system, and as the cheapest way to attach someone else's S1 to Gemma 4 12B.

## Why it is on the list

- Short survey + ablation of every design knob (which latent, freeze vs LoRA, pre-align the projector or the run collapses).
- Checkpoints on HF; CALVIN SOTA among dual systems in their table (avg length 4.08 at EP_LEN=360).
- Training is prompt-tune of one token while the 7B stays frozen. That is the Path K mechanism.

## Gaps vs the brief

- LLaVA-1.5-7B is the rejected-reasoning class.
- CALVIN only. No house, no SO-101.
- Checkpoint merge step (safetensors → `pytorch_model.bin`) is fiddly. Read their README before blaming the model.

## First pull

Paper + project page, then CALVIN eval if Path K is live. The projector pre-align warning in §1.5 of the paper is mandatory reading before any Gemma graft.

## Pull log
