---
id: helix-closed
name: Helix (Figure)
tier: C-kit-or-reference
org: Figure AI
params_b: 7
params_note: 7B VLM at 7–9 Hz produces a latent; 80M visuomotor transformer at 200 Hz consumes that latent plus fresh images. Blog only. No paper, no weights.
backbone: undisclosed 7B VLM
system1: 80M transformer, own camera stream
dual_class: closed_reference
dual_note: The architecture ceiling the sibling notes and OpenHelix both point at. S1 has its own perception. This is what "true dual" means. Cannot be pulled.
open_weights: false
license: closed
hf: []
code: []
paper: []
project: https://www.figure.ai/news/helix
videos:
  - https://www.figure.ai/news/helix
interactive: []
envs: []
robots:
  - Figure humanoid (not for sale as a kit)
overnight: unknown
reasoning_vs_gemma4_12b: unknown
scores:
  dual: 5
  reasoning: 3
  size_fit: 5
  env_play: 1
  cheap_robot: 1
  overnight: 1
  openness: 1
pull_priority: 12
survey_date: 2026-09-02
---

# Helix (Figure)

Parseable spec: [`../notes/06_option_specs.md`](../notes/06_option_specs.md#12-helix-figure--closed-reference).

- **Network:** 7B VLM + 80M / 200 Hz policy. **No weights.**
- **Finetune just to start?** **Cannot.** No weights, no env.
- **World:** Figure humanoid. Not for sale as a kit.
- **Paper:** none. [figure.ai/news/helix](https://www.figure.ai/news/helix)

Watch the video so the open clones have something to be clones *of*. Then ignore it for purchasing.

The useful numbers: **7B is enough** for their S2, **80M is enough** for a 200 Hz S1, and S1 must see the current frame. That is the size excuse for staying under 10B and the design constraint for Path K.

## Pull log
