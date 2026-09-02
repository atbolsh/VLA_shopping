# Demos and playgrounds

Hosted interactive demos are rare. Most "demos" are project-page videos. This list is only things that actually exist.

## Hosted interactive (browser)

| What | URL | Tied to |
|---|---|---|
| **InternNav eval (Gradio)** | https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo | InternVLA-N1 — **the one real hosted VLA-nav playground** |
| Gemini ER + MuJoCo WASM | https://avikde.github.io/vla-pipeline/ | Not a candidate. Slow Gemini planner, classical IK. Useful as a "what Path K feels like" toy. Needs a Gemini key or uses a cached plan. |

## Project-page video (watch before installing)

| Page | Watch for |
|---|---|
| https://internrobotics.github.io/internvla-n1.github.io/ | House-scale nav, dual system |
| https://navila-bot.github.io/ | Go2 / H1, language macros |
| https://openhelix-robot.github.io/ | CALVIN dual-system |
| https://fast-in-slow.github.io/ | Embedded S1, 20+ Hz |
| https://opendrivelab.github.io/RoboDual/ | Generalist + specialist |
| https://one-two-vla.github.io/ | Reason ↔ act flips, cocktails |
| https://allenai.org/blog/molmoact2 | SO-10x, traces, Think |
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
| InternNav | https://github.com/InternRobotics/InternNav | Habitat / Isaac; official N1 loop |
| NaVILA-Bench | https://github.com/yang-zj1026/NaVILA-Bench | Isaac Lab VLN |
| LIBERO via LeRobot | `lerobot-eval --env.type=libero ...` | π0.5, MolmoAct2, GR00T |
| CALVIN | http://calvin.cs.uni-freiburg.de/ | OpenHelix, RoboDual |
| GraspVLA-playground | https://github.com/MiYanDoris/GraspVLA-playground | LIBERO + Objaverse randomization; not a shortlist model |
| vla_ros2 Gradio | https://github.com/rsasaki0109/vla_ros2 | Local `localhost:7860`; SmolVLA / optional π0 / GR00T adapters |

## What does not exist (do not hunt)

- A public Helix or Gemini Robotics weights playground.
- A browser demo of OpenHelix / FiS / MolmoAct2 that runs the real net.
- An official SO-101 web teleop that also runs a 7B VLA in the cloud (LeRobot is local).
