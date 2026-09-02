---
id: gemma4-diy
name: Gemma 4 12B + stolen System 1
tier: C-kit-or-reference
org: user kit (Gemma 4 + OpenHelix/LCB/InternVLA-N1-S1)
params_b: 12
params_note: Keep the 12B you are already finetuning. Attach a 10M–1B S1. Stays under 20B. Training is LoRA or prompt-tune on a bridge token, not a from-scratch 12B run.
backbone: Gemma 4 12B (already in house)
system1: OpenHelix 3DDA / LCB 3DDA / InternVLA-N1 DualVLN / a 3-class CNN for CLOCK-ANTICLOCK-FORWARD
dual_class: kit
dual_note: This is sibling Option 5. Dual score is potential (5) only after the bridge exists.
open_weights: true
license: Gemma + whichever S1
hf: []
code:
  - https://github.com/OpenHelix-robot/OpenHelix
  - https://github.com/InternRobotics/InternNav
paper:
  - arXiv:2505.03912
  - arXiv:2405.04798
project: ../stateful_realtime_thinking/notes/02_design_options.md
videos: []
interactive: []
envs:
  - gold game (native)
  - CALVIN if the 3DDA head is kept
  - Habitat if InternVLA-N1 S1 is kept
robots:
  - whatever S1 already speaks; SO-101 if the head is a LeRobot policy
overnight: Daytime gold-game traces collapse to macros (sibling Options 1+2). Optional later Cosmos dreams. This is the most honest overnight loop because the data is yours.
reasoning_vs_gemma4_12b: above
scores:
  dual: 5
  reasoning: 5
  size_fit: 4
  env_play: 4
  cheap_robot: 3
  overnight: 4
  openness: 5
pull_priority: 2
survey_date: 2026-09-02
---

# Gemma 4 12B + stolen System 1

Parseable spec: [`../notes/06_option_specs.md`](../notes/06_option_specs.md#2-gemma-4-12b--stolen-system-1-kit).

- **Network:** Your Gemma 4 12B + OpenHelix 3DDA / InternVLA-N1 DualVLN / a CLOCK head you train.
- **Finetune just to start?** **Yes.** No released Gemma+S1 policy. Watch OpenHelix/CALVIN or InternVLA-N1/Habitat instead.
- **World:** Your gold game, or CALVIN/Habitat if you keep their S1. $0 until you buy an arm.
- **Paper:** `2505.03912_openhelix.pdf`, `2405.04798_lcb.pdf`

This is not a downloadable VLA. It is the option that **does not throw away** the only model on the table that already cleared your reasoning bar.

## Why it is on the list

Every true-dual 7B paper from 2024–early 2025 uses a language core you would have rejected if it showed up as a Gemma. OpenHelix even freezes LLaVA and only trains an `<ACT>` token + projector — that recipe is **backbone-agnostic** on paper. LCB is the same idea. InternVLA-N1 publishes System 2 and System 1 as separate HF cards, which is the other way to steal a body.

Sibling recommended path was macros+guards first, dual head later. This card is that later step, named so it can lose or win against off-the-shelf VLAs in the scorecard.

## Gaps vs the brief

- Not off-the-shelf. Weeks of bridge work.
- 12B is above the "ideally <10B" wish. Excuse: you already rejected the 4B class; 12B is the smallest brain you trust. The twitch net should stay tiny.
- No vendor demo, because it does not exist until you build it.

## First pull

Do **not** start here on day one. Pull InternVLA-N1 and OpenHelix so the S1 half is a known quantity. Then decide whether to swap S2.

## Pull log
