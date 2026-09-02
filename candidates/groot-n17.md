---
id: groot-n17
name: Isaac GR00T N1.7
tier: B-near-dual-mature
org: NVIDIA
params_b: 3
params_note: 2B Cosmos-Reason2-2B (Qwen3-VL lineage) + ~1B flow-matching action transformer. N1.5/N1.6 used Eagle-2B. Always load the gated Cosmos-Reason2-2B first.
backbone: nvidia/Cosmos-Reason2-2B
system1: 32-layer flow-matching DiT, action chunk 16, few denoising steps
dual_class: near_expert
dual_note: Marketed as dual-system (slow VLA, fast whole-body). OpenHelix argues GR00T N1 is not a true dual because S1 lacks independent real-time perception. Treat N1.7 the same unless the code shows a second camera path.
open_weights: true
license: NVIDIA (research/commercial support on GA; gated HF)
hf:
  - https://huggingface.co/nvidia/GR00T-N1.7-3B
  - https://huggingface.co/nvidia/GR00T-N1.7-LIBERO
  - https://huggingface.co/nvidia/Cosmos-Reason2-2B
code:
  - https://github.com/NVIDIA/Isaac-GR00T
paper:
  - arXiv:2503.14734
  - https://research.nvidia.com/labs/gear/dreamgen/
project: https://developer.nvidia.com/isaac/gr00t
videos:
  - https://developer.nvidia.com/isaac/gr00t
  - https://research.nvidia.com/labs/gear/dreamgen/
interactive: []
envs:
  - Isaac Lab / Isaac Lab-Arena
  - LIBERO
  - RoboCasa
  - SimplerEnv
  - RoboLab
robots:
  - SO-100 example in the repo
  - DROID
  - Unitree G1, AgiBot, Fourier GR-1 (pretrain tags)
overnight: GR00T-Dreams + Cosmos-Predict2.5 is the only turnkey "few daytime demos → night-time neural trajectories → morning VLA" pipeline on this list. This is why a 3B near-dual stays in the top five.
reasoning_vs_gemma4_12b: below_ok
scores:
  dual: 3
  reasoning: 2
  size_fit: 5
  env_play: 5
  cheap_robot: 4
  overnight: 5
  openness: 4
pull_priority: 4
survey_date: 2026-09-02
---

# Isaac GR00T N1.7

Parseable spec: [`../notes/06_option_specs.md`](../notes/06_option_specs.md#4-isaac-gr00t-n17).

- **Network:** [GR00T-N1.7-3B](https://huggingface.co/nvidia/GR00T-N1.7-3B) = gated [Cosmos-Reason2-2B](https://huggingface.co/nvidia/Cosmos-Reason2-2B) + 1B action transformer. LIBERO: [GR00T-N1.7-LIBERO](https://huggingface.co/nvidia/GR00T-N1.7-LIBERO).
- **Finetune just to start?** **No.** GR00T-N1.7-LIBERO (gated Cosmos-Reason2 first). New embodiment / Dreams later: finetune.
- **World:** LIBERO / RoboCasa / Isaac Lab, $0. SO-100 example uses the **$121.94** follower BOM.
- **Paper:** `2503.14734_groot_n1.pdf` (N1 paper; N1.7 is the release)

Best **self-teaching stack**, weakest **planner**. If the thesis is overnight artificial data, this is the thing to steal even if the 2B VLM fails Smoke 0.

## Why it is on the list

- GA release, documented embodiments, LIBERO/RoboCasa/SimplerEnv scripts in one repo.
- DreamGen: post-train Cosmos-Predict2.5 on a handful of teleop trajectories, generate video dreams, filter with Cosmos-Reason, invert to actions (IDM or LAPA), finetune GR00T. NVIDIA used this to build N1.5 in ~36 hours of GPU instead of months of teleop.
- SO-100 is a first-class example (`demo_data/cube_to_bowl_5`, `NEW_EMBODIMENT`).
- Isaac Lab is the "many environments" answer if you are willing to live in NVIDIA's house.

## Gaps vs the brief

- **Cosmos-Reason2-2B is in the e4B danger zone.** Physical-AI tuned, yes; general planning/coding, probably not. If Smoke 0 fails, keep DreamGen and throw the 2B planner away (Path K + Dreams).
- Dual purity is contested (see OpenHelix).
- Gated HF + Isaac Sim weight. Not a laptop afternoon.

## First pull

Request Cosmos-Reason2-2B access, then `GR00T-N1.7-LIBERO` eval. Read the Dreams cookbook before buying a humanoid.

## Pull log
