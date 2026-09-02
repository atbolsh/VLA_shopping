---
id: robodual
name: RoboDual
tier: A-true-dual-7b
org: OpenDriveLab
params_b: 7
params_note: OpenVLA-7B generalist (Llama-2) + DiT specialist. Two HF cards.
backbone: OpenVLA-7B (Prismatic / Llama-2-7B)
system1: DiT specialist, RGB+depth+tactile+proprio, trained from scratch, guided by generalist action+lang latents
dual_class: true_async
dual_note: Explicit coarse actions from S2, not only a latent. Good counterpoint to OpenHelix's <ACT> token. Async recommended.
open_weights: true
license: check GitHub
hf:
  - https://huggingface.co/qwbu/RoboDual-OpenVLA-Generalist
  - https://huggingface.co/qwbu/RoboDual-Specialist
code:
  - https://github.com/OpenDriveLab/RoboDual
paper:
  - arXiv:2410.08001
project: https://opendrivelab.github.io/RoboDual/
videos:
  - https://opendrivelab.github.io/RoboDual/
interactive: []
envs:
  - CALVIN
robots:
  - paper real-robot (not SO-101)
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
pull_priority: 9
survey_date: 2026-09-02
---

# RoboDual

Parseable spec: [`../notes/06_option_specs.md`](../notes/06_option_specs.md#9-robodual).

- **Network:** S2 [RoboDual-OpenVLA-Generalist](https://huggingface.co/qwbu/RoboDual-OpenVLA-Generalist) (needs [openvla-7b](https://huggingface.co/openvla/openvla-7b)). S1 [RoboDual-Specialist](https://huggingface.co/qwbu/RoboDual-Specialist).
- **Finetune just to start?** **No.** Both HF cards on [CALVIN](http://calvin.cs.uni-freiburg.de/). New tabletop later: train S1.
- **World:** [CALVIN](http://calvin.cs.uni-freiburg.de/), $0. No SO-101.
- **Paper:** `2410.08001_robodual.pdf`

The other 7B true-dual kit. Prefer OpenHelix unless you specifically want **coarse actions** (not a single `<ACT>` vector) as the S2→S1 handoff — that maps more cleanly onto sibling Option 1 macros.

## Why it is on the list

- Open weights for both halves.
- Uses a robot-pretrained VLA (OpenVLA) as S2, which OpenHelix's survey flags as better for instruction following.
- Architecture became the default "VLM + DiT" story that later papers copy.

## Gaps vs the brief

- Llama-2-7B / OpenVLA reasoning.
- CALVIN-centric.
- Needs a local OpenVLA path in their scripts.

## First pull

Only if OpenHelix's latent bridge feels wrong and you want action-space handoff. Otherwise skip.

## Pull log
