# Demos and playgrounds

Hosted interactive demos are rare. Most "demos" are project-page videos. This list is only things that actually exist.

**Next-session order:** EO-1 → ChatVLA → WALL-OSS → ECoT-OpenVLA. First crop **rejected 2026-09-04**. InternVLA-N1 is never the next box. Script: [`09_next_session.md`](09_next_session.md). Sibling log: [`10_sibling_list.md`](10_sibling_list.md).

## Hosted interactive (browser)

| What | URL | Tied to |
|---|---|---|
| **InternNav eval (Gradio)** | https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo | InternVLA-N1 — hosted space was 401; DualVLN **rejected 2026-09-04**. Do not hunt clones. |
| Gemini ER + MuJoCo WASM | https://avikde.github.io/vla-pipeline/ | Not a candidate. Slow Gemini planner, classical IK. Useful as a "what Path K feels like" toy. Needs a Gemini key or uses a cached plan. |

JARVIS-VLA / MineStudio is **local**, not hosted. Sibling first-look: [`10_sibling_list.md`](10_sibling_list.md).

RynnVLA / WorldVLA / MolmoAct2 have **no** hosted net. Their "interactive" is HF card GIFs plus a later local LIBERO sandbox.

## Project-page video (watch before installing)

| Page | Watch for |
|---|---|
| https://huggingface.co/blog/Alibaba-DAMO-Academy/rynnvla-001 | RynnVLA-001 — ego-video pretrain → VLA. YouTube/Bilibili on the [GitHub README](https://github.com/alibaba-damo-academy/RynnVLA-001) |
| https://huggingface.co/Alibaba-DAMO-Academy/WorldVLA | WorldVLA — action GIFs and action→next-frame GIFs |
| https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-002 | RynnVLA-002 — LIBERO + wrist generation / world-model tables |
| https://allenai.org/blog/molmoact2 | SO-10x, traces, Think |
| https://internrobotics.github.io/internvla-n1.github.io/ | House-scale nav, dual system |
| https://navila-bot.github.io/ | Go2 / H1, language macros |
| https://openhelix-robot.github.io/ | CALVIN dual-system |
| https://fast-in-slow.github.io/ | Embedded S1, 20+ Hz |
| https://opendrivelab.github.io/RoboDual/ | Generalist + specialist |
| https://one-two-vla.github.io/ | Reason ↔ act flips, cocktails |
| https://microsoft.github.io/Magma/ | UI + WidowX |
| https://www.figure.ai/news/helix | The closed ceiling, 200 Hz S1 |
| https://www.physicalintelligence.company/blog/pi0 | π0 folding / kitchen |
| https://www.physicalintelligence.company/blog/pi05 | Open-world π0.5 |
| https://developer.nvidia.com/isaac/gr00t | GR00T embodiments |
| https://research.nvidia.com/labs/gear/dreamgen/ | Overnight dreams (this is the self-teaching video) |
| https://declare-lab.github.io/nora | NORA (honorable) |

## Local playgrounds (install, then click)

| Playground | URL | Notes |
|---|---|---|
| InternNav | https://github.com/InternRobotics/InternNav | DualVLN **rejected 2026-09-04** (`→→→→`). Do not reopen. |
| EO-1 official generate | https://github.com/EO-Robotics/EO1 | Next crop. Text + action from `IPEC-COMMUNITY/EO-1-3B`. |
| ChatVLA `evaluate_robot.py` | https://github.com/midea-ai/ChatVLA_public | Next crop. v1 weights only (`zzymeow/ChatVLA`). |
| WALL-OSS / wall-x | https://github.com/X-Square-Robot/wall-x | Next crop. Uni-CoT claim; official scripts are action-first. |
| ECoT-OpenVLA | https://github.com/MichalZawalski/embodied-CoT | Next crop. TASK/PLAN/SUBTASK then action. |
| JARVIS-VLA + MineStudio | https://github.com/CraftJarvis/JarvisVLA | **Rejected 2026-09-03.** Mouth dead. Sandbox deleted. |
| WorldVLA / RynnVLA-002 LIBERO | https://github.com/alibaba-damo-academy/WorldVLA | **Rejected 2026-09-04.** Sandbox deleted. |
| NaVILA-Bench | https://github.com/yang-zj1026/NaVILA-Bench | Isaac Lab VLN |
| LIBERO via LeRobot | `lerobot-eval --env.type=libero ...` | π0.5, MolmoAct2, GR00T |
| CALVIN | http://calvin.cs.uni-freiburg.de/ | OpenHelix, RoboDual |
| GraspVLA-playground | https://github.com/MiYanDoris/GraspVLA-playground | LIBERO + Objaverse randomization; not a shortlist model |
| vla_ros2 Gradio | https://github.com/rsasaki0109/vla_ros2 | Local `localhost:7860`; SmolVLA / optional π0 / GR00T adapters |

## What does not exist (do not hunt)

- A public Helix or Gemini Robotics weights playground.
- A browser demo of OpenHelix / FiS / MolmoAct2 / RynnVLA / WorldVLA that runs the real net.
- An official SO-101 web teleop that also runs a 7B VLA in the cloud (LeRobot is local).
