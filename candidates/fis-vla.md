---
id: fis-vla
name: FiS-VLA (Fast-in-Slow)
tier: A-true-dual-7b
org: (Fast-in-Slow authors; code CHEN-H01)
params_b: 7
params_note: Llama-2-7B VLM. System 1 is the last transformer blocks of the same net, plus high-rate state / RGB / point cloud. No second 7B.
backbone: Llama-2-7B (OpenVLA / HybridVLA lineage)
system1: repurposed final VLM blocks + diffusion, async high-rate extras
dual_class: true_embedded
dual_note: The interesting architecture. S1 is literally inside S2, still fed fresher/faster sensors. 21.9 Hz without chunks, 117 Hz with chunk 8. Dual-aware co-training is supposed to keep S2's reasoning representation intact — verify that, because Llama-2.
open_weights: true
license: check GitHub
hf:
  - https://huggingface.co/haosad/fisvla
code:
  - https://github.com/CHEN-H01/Fast-in-Slow
paper:
  - arXiv:2506.01953
project: https://fast-in-slow.github.io/
videos:
  - https://fast-in-slow.github.io/
interactive: []
envs:
  - RLBench
  - real-robot tasks in the paper
robots:
  - paper real-arm (not SO-101)
overnight: none
reasoning_vs_gemma4_12b: below_reject
scores:
  dual: 5
  reasoning: 2
  size_fit: 5
  env_play: 4
  cheap_robot: 2
  overnight: 2
  openness: 5
pull_priority: 6
survey_date: 2026-09-02
---

# FiS-VLA (Fast-in-Slow)

Parseable spec: [`../notes/06_option_specs.md`](../notes/06_option_specs.md#6-fis-vla-fast-in-slow).

- **Network:** One 7B, [haosad/fisvla](https://huggingface.co/haosad/fisvla). Last blocks *are* S1. Code: [CHEN-H01/Fast-in-Slow](https://github.com/CHEN-H01/Fast-in-Slow).
- **Finetune just to start?** **No.** `haosad/fisvla` + [RLBench](https://github.com/stepjam/RLBench). New backbone/env later: yes.
- **World:** [RLBench](https://github.com/stepjam/RLBench), $0. No SO-101.
- **Paper:** `2506.01953_fis_vla.pdf`

The dual-system paper to **read** even if the checkpoint is not the one you deploy. Embedding S1 in the last blocks of an intact S2 is the closest published object to "the plan lives in residual activations while a cheap loop runs."

## Why it is on the list

- True dual by the OpenHelix perception test, but not a bolted-on specialist.
- Project page has demos; HF checkpoint exists (`haosad/fisvla`).
- Co-training claim: teach S1 to act without wrecking S2 features. That is the exact risk of Path K if you fine-tune Gemma end-to-end.

## Gaps vs the brief

- Llama-2-7B. Reasoning smoke will fail. Do not buy this for the brain.
- RLBench + CoppeliaSim is more annoying than LIBERO.
- No cheap-robot checkpoint.

## First pull

Watch the page. If Path K is the winner, steal the *training recipe*, not the Llama.

## Pull log
