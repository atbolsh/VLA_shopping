---
id: magma-8b
name: Magma-8B
tier: C-kit-or-reference
org: Microsoft
params_b: 8
params_note: Llama-3-8B-Instruct + vision, Set-of-Mark / Trace-of-Mark pretraining. Single AR model. 4-bit ~7 GB.
backbone: Llama-3-8B-Instruct
system1: none (action tokens / traces)
dual_class: single
dual_note: Not dual. On the list because criterion 3 (general pretraining: UI + robot + VL) is unusually broad for an 8B, and because a later S1 could be bolted on.
open_weights: true
license: MIT (check card)
hf:
  - https://huggingface.co/microsoft/Magma-8B
code:
  - https://github.com/microsoft/Magma
paper:
  - arXiv:2502.13130
project: https://microsoft.github.io/Magma/
videos:
  - https://microsoft.github.io/Magma/
interactive: []
envs:
  - SimplerEnv
  - LIBERO
  - UI / Mind2Web-style
robots:
  - WidowX few-shot in the paper
overnight: none
reasoning_vs_gemma4_12b: below_ok
scores:
  dual: 1
  reasoning: 3
  size_fit: 5
  env_play: 4
  cheap_robot: 2
  overnight: 2
  openness: 4
pull_priority: 11
survey_date: 2026-09-02
---

# Magma-8B

Parseable spec: [`../notes/06_option_specs.md`](../notes/06_option_specs.md#11-magma-8b).

- **Network:** Single net, [microsoft/Magma-8B](https://huggingface.co/microsoft/Magma-8B). No System 1.
- **Finetune just to start?** **No.** Released 8B on SimplerEnv / LIBERO / UI. No S1. Real WidowX later: few-shot FT.
- **World:** [SimplerEnv](https://github.com/simpler-env/SimplerEnv), LIBERO, $0.
- **Paper:** `2502.13130_magma.pdf`

The **generalist 8B** to smoke-test if you ever want one net that can click a GUI *and* move an arm. Not a twitch architecture. Llama-3-8B should beat OpenHelix's LLaVA and lose to Gemma 4 12B.

## Why it is on the list

- Criterion 3 is not only "robot bench." Magma is pretrained for spatial traces and UI marks on mixed internet data.
- Easy HF download, SimplerEnv / LIBERO recipes, 4-bit fits a 12 GB card.
- Honest single-system baseline so dual-system wins are not just "we added a second net."

## Gaps vs the brief

- No quick-twitch. 1.1 s/step in their table.
- No cheap-robot ckpt.

## First pull

Only for Smoke 0 and as a possible Path K S2 if Gemma is too heavy and Qwen2.5-VL is not wanted.

## Pull log
