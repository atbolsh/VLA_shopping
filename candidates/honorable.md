# Honorable mentions (not full cards)

These came up while shopping. They are dependencies, negative controls, or next-year revisits — not first pulls.

| id | params | why it appeared | why it is not a primary |
|---|---|---|---|
| **SmolVLA** | ~450M (SigLIP + SmolLM2-135M + diffusion) | LeRobot default on SO-101; [paper](https://arxiv.org/abs/2506.01844); local playgrounds exist | Planner is smaller than the Gemma e4B you rejected. Use only to verify the arm wires. |
| **NORA / NORA-1.5** | 3B Qwen2.5-VL | Modern VLM, OXE, FAST tokens, [demos](https://declare-lab.github.io/nora), [code](https://github.com/declare-lab/nora) | Right VLM family, wrong size, no dual loop. |
| **OpenVLA 7B** | 7B Llama-2 | [arXiv:2406.09246](https://arxiv.org/abs/2406.09246); backbone of RoboDual | Single-system, old core. Download as a dependency. |
| **LCB** | LLaVA-7B + 3DDA | [arXiv:2405.04798](https://arxiv.org/abs/2405.04798); invented `<ACT>` | OpenHelix is the maintained descendant. |
| **HiRT** | InstructBLIP-7B + RT-1 | [arXiv:2410.05273](https://arxiv.org/abs/2410.05273) | True dual, weaker stack than OpenHelix/RoboDual. |
| **InternVLA-A1 / Vesta** | Qwen3-VL-8B planners | 2026 embodied-reasoning VLMs | Less turnkey "play in a house" than InternVLA-N1. Revisit if N1's action space is too nav-specific. |
| **Gemini Robotics ER** | closed | [browser SPA toy](https://avikde.github.io/vla-pipeline/) | Architecture demo only. |
| **π0.5 paper hierarchy** | n/a | Subtask tokens in the paper | Not in openpi. |
| **GraspVLA** | mid-size | [LIBERO playground](https://github.com/MiYanDoris/GraspVLA-playground) | Grasp specialist, not a general dual planner. |

## SmolVLA links (hardware bring-up only)

- HF: `lerobot/smolvla_base`
- Paper: https://arxiv.org/abs/2506.01844
- Local browser playground (ROS2/Gazebo, not hosted): https://github.com/rsasaki0109/vla_ros2
