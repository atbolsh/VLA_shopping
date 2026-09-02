---
id: navila
name: NaVILA
tier: A-true-dual-7b
org: UCSD / USC / NVIDIA
params_b: 8
params_note: VILA-style VLM on Llama-3-8B (a8cheng/navila-llama3-8b-8f). System 1 is a separate vision locomotion RL policy in Isaac Lab, not counted in the 8B.
backbone: VILA / Llama-3-8B (SigLIP), 8-frame video
system1: vision-based locomotion policy (Go2, H1) trained in Isaac Lab; consumes mid-level language like "moving forward 75cm"
dual_class: true_hierarchical
dual_note: Textbook option-selector. S2 emits temporally extended language skills; S1 is a high-rate closed-loop walker that actually sees. This is sibling thread F (SayCan) plus a modern VLA planner.
open_weights: true
license: check HF
hf:
  - https://huggingface.co/a8cheng/navila-llama3-8b-8f
  - https://huggingface.co/a8cheng/navila-siglip-llama3-8b-v1.5-pretrain
  - https://huggingface.co/collections/a8cheng/navila-legged-robot-vision-language-action-model-for-naviga-67cfc82b83017babdcefd4ad
code:
  - https://github.com/AnjieCheng/NaVILA
  - https://github.com/yang-zj1026/NaVILA-Bench
paper:
  - arXiv:2412.04453
project: https://navila-bot.github.io/
videos:
  - https://navila-bot.github.io/
interactive: []
envs:
  - Habitat VLN-CE
  - VLN-CE-Isaac / NaVILA-Bench
robots:
  - Unitree Go2
  - Unitree H1
overnight: Trained on mixed human touring video + sim nav + QA. No dream loop. Human-video IDs are released; raw YouTube is DIY.
reasoning_vs_gemma4_12b: below_ok
scores:
  dual: 5
  reasoning: 3
  size_fit: 5
  env_play: 5
  cheap_robot: 3
  overnight: 2
  openness: 5
pull_priority: 5
survey_date: 2026-09-02
---

# NaVILA

Parseable spec: [`../notes/06_option_specs.md`](../notes/06_option_specs.md#5-navila).

- **Network:** S2 [navila-llama3-8b-8f](https://huggingface.co/a8cheng/navila-llama3-8b-8f). S1 = Isaac Lab locomotion policy in [AnjieCheng/NaVILA](https://github.com/AnjieCheng/NaVILA).
- **Finetune just to start?** **No.** Habitat VLN-CE, then NaVILA-Bench. New game later: yes for twitch.
- **World:** Habitat VLN-CE + [NaVILA-Bench](https://github.com/yang-zj1026/NaVILA-Bench), $0. Robot: [Unitree Go2](https://www.unitree.com/go2) **from $1,600** (+ freight).
- **Paper:** `2412.04453_navila.pdf`

Best **legged** dual system, and the cleanest "S2 speaks English macros, S1 twitches" picture. Llama-3-8B is better than Llama-2-7B, still probably under Gemma 4 12B.

## Why it is on the list

- Mid-level language actions (`forward 75cm`, turn amounts) are exactly sibling Option 1, learned rather than hardcoded.
- S1 is a real-time vision locomotion policy with its own eyes — OpenHelix-true dual, hierarchical flavor.
- Two installable 3D worlds: Habitat (easy-ish VLN-CE) and Isaac Lab (honest physics).
- Real Go2 / H1 videos on the project page. Go2 is the cheapest serious mobile robot on this list.

## Gaps vs the brief

- Go2 is not $120. It is "relatively inexpensive" only next to a humanoid.
- Planner is Llama-3-8B VILA, not a 2026 reasoning king.
- Overlaps InternVLA-N1. Prefer N1 if you stay in Habitat and want a stronger VLM; prefer NaVILA if you want a dog.

## First pull

Project-page videos, then Habitat R2R eval with `navila-llama3-8b-8f`. Isaac bench second.

## Pull log
