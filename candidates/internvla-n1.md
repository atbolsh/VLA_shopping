---
id: internvla-n1
name: InternVLA-N1
tier: A-true-dual-7b
org: InternRobotics
params_b: 8
params_note: System 2 is a finetuned Qwen2.5-VL-7B (HF lists ~8B). System 1 is NavDP* or DualVLN, much smaller, jointly trained.
backbone: Qwen2.5-VL-7B-Instruct
system1: NavDP* (RGB-D) or DualVLN (RGB), async nav controller
dual_class: true_async
dual_note: Joint-trained S2 (pixel-goal / high-level VLN reasoning) and S1 (low-level nav). Asynchronous. Matches OpenHelix's "S1 sees fresh observations" test.
open_weights: true
license: check HF card at pull (InternRobotics)
hf:
  - https://huggingface.co/InternRobotics/InternVLA-N1-System2
  - https://huggingface.co/InternRobotics/InternVLA-N1-DualVLN
  - https://huggingface.co/InternRobotics/InternVLA-N1-w-NavDP
code:
  - https://github.com/InternRobotics/InternNav
paper:
  - https://internrobotics.github.io/internvla-n1.github.io/static/pdfs/InternVLA_N1.pdf
project: https://internrobotics.github.io/internvla-n1.github.io/
videos:
  - https://internrobotics.github.io/internvla-n1.github.io/
interactive:
  - https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo
envs:
  - InternNav + Habitat VLN-CE
  - Isaac Sim / InternUtopia
  - InternData-N1 (3k+ scenes, 830k VLN)
robots:
  - real-world VLN deployments via InternUtopia / InternNav
  - not SO-100
overnight: InternData-N1 scale plus VL-LN dialog-augmented trajectory generation. Not a world-model dream loop, but it is a factory for nav data from scenes.
reasoning_vs_gemma4_12b: near
scores:
  dual: 5
  reasoning: 4
  size_fit: 5
  env_play: 5
  cheap_robot: 2
  overnight: 3
  openness: 5
pull_priority: 1
survey_date: 2026-09-02
---

# InternVLA-N1

Parseable spec (Network / Action / World / Paper): [`../notes/06_option_specs.md`](../notes/06_option_specs.md#1-internvla-n1).

- **Network:** S2 [InternVLA-N1-System2](https://huggingface.co/InternRobotics/InternVLA-N1-System2) (Qwen2.5-VL-7B). S1 [DualVLN](https://huggingface.co/InternRobotics/InternVLA-N1-DualVLN) (recommended) or [NavDP*](https://huggingface.co/InternRobotics/InternVLA-N1-w-NavDP).
- **Finetune just to start?** **No.** InternNav + Habitat, or the Gradio. New env later: yes.
- **World:** InternNav + Habitat, $0. No SO-101 ckpt.
- **Paper:** `papers/pdfs/internvla_n1_techreport.pdf`

Best **off-the-shelf** match to "navigate a detailed 3D world with a slow planner and a fast body," and the only true-dual 7B-class stack whose language core is newer than Llama-2.

## Why it is on the list

- System 2 is **Qwen2.5-VL-7B**, not LLaVA-1.5. That is the first backbone on this list that has a realistic chance of planning like Gemma 4 12B.
- Dual system is not a blog slogan: S2 and S1 are separate modules, async, jointly trained. DualVLN (RGB) is the current recommended whole-system checkpoint.
- InternNav is an actual installable playground (Habitat + Isaac), not a one-off eval script.
- There is a **hosted Gradio** eval space. Rare.

## Gaps vs the brief

- Action space is **navigation**, not fine tabletop dexterity and not your `[CLOCK]` ticks. Transfer to the gold game is conceptual (macros / mid-level commands), not a checkpoint.
- No SO-101 finetune. Cheap-robot score is low on purpose.
- Overnight story is "huge nav dataset + dialog augmentation," not Cosmos-style dreams.

## First pull

1. Open the Gradio space and the project page videos.
2. Reasoning smoke on the System 2 card alone (`InternVLA-N1-System2`).
3. If that holds, install InternNav Habitat eval before touching Isaac.

## Pull log
