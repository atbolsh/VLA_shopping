# Path N: InternVLA-N1 vs NaVILA (and why GR00T is not in this path)

Both are **vision-and-language navigation** stacks with a slow planner and a fast body. They are not the same product.

## Same job

You give an English instruction (“go to the kitchen / the red chair”). A System 2 looks at camera frames and decides *where to go*. A System 1 keeps the robot moving without a full re-plan every tick. Both start without finetuning: Habitat VLN-CE is the shared first env. Both have an Isaac follow-on.

## Different handoff

| | **InternVLA-N1** | **NaVILA** |
|---|---|---|
| Dual class | `true_async` — S2 and S1 jointly trained, async | `true_hierarchical` — S2 speaks English macros, S1 is a walker |
| What S2 emits | Pixel-goals / high-level VLN features into DualVLN or NavDP* | Mid-level language: `moving forward 75cm`, turn amounts |
| What S1 is | A **learned nav controller** (DualVLN = RGB; NavDP* = RGB-D) | A **locomotion RL policy** (vision, Isaac Lab → real legs) |
| Closest sibling analog | Helix / OpenHelix (latent or controller, not words) | SayCan / Option 1 (`[FORWARD 75]` as English) |
| S2 backbone | **Qwen2.5-VL-7B** (better shot at Gemma-12B-class planning) | **Llama-3-8B VILA**, 8-frame video (fine, older) |
| Body it assumes | Generic VLN agent (Habitat capsule / wheeled-ish). Real VLN via InternNav / InternUtopia. **Not** a published Go2 walker. | **Unitree Go2 or H1.** S1 is a quadruped/humanoid gait that also avoids obstacles. |
| First env | [InternNav](https://github.com/InternRobotics/InternNav) + Habitat; [Gradio](https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo) | Habitat [VLN-CE](https://github.com/jacobkrantz/VLN-CE); then [NaVILA-Bench](https://github.com/yang-zj1026/NaVILA-Bench) |
| Data scale | InternData-N1: ~3k scenes, 830k VLN | Smaller mix: R2R/RxR/EnvDrop + human touring video + QA |
| Physics honesty | Habitat first (can cheat thin gaps). Isaac/InternUtopia if you want honesty. | Same Habitat start, but they **built** VLN-CE-Isaac because Habitat lets agents slip through a 10 cm sofa gap a Go2 cannot. |
| Cheap metal | None official | Go2 from **$1,600** + freight |
| Interactive demo | Yes | Project-page video only |

InternVLA-N1 is the better **planner + house-scale VLN product**. NaVILA is the better **“S2 talks, S1 walks on real legs”** picture, and the only Path N stack with a robot you can actually buy.

If you want to shop Path N in software this week: InternVLA-N1 (Gradio, then InternNav). If you already want a dog in the loop: NaVILA.

## GR00T does not do this job

Isaac GR00T N1.7 is a **manipulation / humanoid-skills** VLA. Published evals are LIBERO, RoboCasa tabletop/kitchen, SimplerEnv, DROID, SO-100, G1 arms.

It is **not** a VLN model: no Habitat house tours, no “follow the instruction through the building,” no InternNav-style nav benchmark.

Caveats, so this does not get overstated:

- RoboCasa includes **mobile-manipulator** kitchen tasks (base moves so the arm can reach). That is “scoot the base in a kitchen,” not language navigation through a house.
- The `UNITREE_G1_SONIC` tag + GEAR-SONIC controller does **whole-body loco-manipulation** (walk while using the hands). Walking is a side effect of a humanoid skill policy, not Path N.

Use GR00T on Path R. Do not use it to shop navigation.
