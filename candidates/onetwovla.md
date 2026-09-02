---
id: onetwovla
name: OneTwoVLA
tier: B-near-dual-mature
org: Tsinghua / Gao lab
params_b: 3.3
params_note: Instantiated on π0 (PaliGemma + action expert). One net, two modes.
backbone: π0 VLM (PaliGemma)
system1: π0 flow-matching expert, used when the net is in act mode
dual_class: behavioral_switch
dual_note: Adaptively reasons (System Two text) or acts (System One). Recovers from mistakes by flipping back to reason. Philosophically close to "re-engage S2 on surprise" (AINav / sibling triggers). Not two perceivers.
open_weights: false
license: code MIT-ish / check repo
hf:
  - https://huggingface.co/datasets/Richard-Nai/onetwovla-dataset
code:
  - https://github.com/Fanqi-Lin/OneTwoVLA
  - https://github.com/Fanqi-Lin/OneTwoVLA-UMI-Client
paper:
  - arXiv:2505.11917
project: https://one-two-vla.github.io/
videos:
  - https://one-two-vla.github.io/
interactive: []
envs:
  - authors' real UMI kitchen / cocktail / hotpot
  - no public Habitat/LIBERO eval advertised
robots:
  - UMI / their real arms
overnight: Automatic synthetic embodied-reasoning VL data (grounding + long-horizon plans) with no human labels, co-trained with robot data. Second-best night factory after DreamGen.
reasoning_vs_gemma4_12b: below_ok
scores:
  dual: 4
  reasoning: 3
  size_fit: 5
  env_play: 2
  cheap_robot: 2
  overnight: 4
  openness: 3
pull_priority: 10
survey_date: 2026-09-02
---

# OneTwoVLA

Parseable spec: [`../notes/06_option_specs.md`](../notes/06_option_specs.md#10-onetwovla).

- **Network:** π0 instantiation. Code [Fanqi-Lin/OneTwoVLA](https://github.com/Fanqi-Lin/OneTwoVLA). Data [onetwovla-dataset](https://huggingface.co/datasets/Richard-Nai/onetwovla-dataset). **No clear one-click policy card** at survey time.
- **Finetune just to start?** **Yes.** Train scripts + UMI client; no policy card; no public sim env. Videos only.
- **World:** Authors' real kitchen / UMI. No public Habitat/LIBERO loop. $0 to watch videos.
- **Paper:** `2505.11917_onetwovla.pdf`

A **recipe** more than a product: teach a π0-class net when to talk and when to move, and synthesize the reasoning data. Policy weights were not a clear one-click HF card at survey time (datasets yes, UMI client yes). Confirm before promising a download.

## Why it is on the list

- Adaptive reason/act is the sibling re-engagement trigger, learned.
- Synthetic VL pipeline is the other overnight story (language dreams, not video dreams).
- Project page is one of the better demo-video sites.

## Gaps vs the brief

- Lives on PaliGemma-sized π0. Reasoning lift comes from extra data, not a 12B core.
- No installable public 3D benchmark loop comparable to InternNav or LIBERO.
- Openness is code+data, weights uncertain.

## First pull

Watch the page. Steal the synthesizer if Path K needs night-time language data. Do not block the shortlist on a missing ckpt.

## Pull log
