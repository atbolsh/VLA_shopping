# Environments and cheap robots

Installability matters more than leaderboard points. This is the playable set that actually shows up on the candidate cards.

## 3D environments (software)

### InternNav + Habitat + Isaac Sim — best nav playground

- Code: https://github.com/InternRobotics/InternNav
- Docs: https://internrobotics.github.io/user_guide/internnav/
- What you get: VLN-CE in Habitat, Isaac Sim scenes, InternData-N1 (~3k scenes, 830k VLN trajectories), InternVLA-N1 agents.
- Pain: Habitat-sim + Isaac Sim is a real install (conda `habitat-sim`, NVIDIA Isaac). Not a one-pip toy.
- Hosted taste: [InternNav-Eval-Demo](https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo) (Gradio) — was 401. DualVLN **rejected 2026-09-04**. Do not reopen as the next box.
- Matches the gold game better than any tabletop benchmark **if** you still want nav after the English-while-acting crop.

### NaVILA-Bench (Isaac Lab) + Habitat VLN-CE

- Isaac eval: https://github.com/yang-zj1026/NaVILA-Bench
- Upstream Habitat VLN-CE: https://github.com/jacobkrantz/VLN-CE
- Why: physics-realistic gaps (Habitat will let an agent slip through a 10 cm sofa gap; Isaac will not). Good honesty check for "real world navigation."

### LIBERO — easiest VLA eval that is still 3D

- Site: https://libero-project.github.io/
- LeRobot one-liner: `lerobot-eval --policy.path=... --env.type=libero --env.task=libero_object`
- Tabletop Franka, language-conditioned lifelong tasks. Used by π0.5, MolmoAct2, GR00T N1.7-LIBERO.
- Simple, detailed enough, not a house.

### CALVIN ABC-D — dual-system papers' home

- Site: http://calvin.cs.uni-freiburg.de/
- Used by OpenHelix, RoboDual. Long-horizon language tabletop.
- Install is older and fussier than LIBERO. Worth it if you are reproducing OpenHelix before swapping S2.

### RoboCasa + Isaac Lab-Arena

- https://robocasa.ai/ — procedural kitchens, many tasks, used in GR00T / π0 evals.
- Lightwheel ports exist inside LeRobot EnvHub / Isaac Lab-Arena (250+ tasks).
- Best "many environments" story that is still one install family (Isaac).

### SimplerEnv

- https://github.com/simpler-env/SimplerEnv
- Google Robot (Fractal) + WidowX (Bridge). Magma, MolmoAct, GR00T all report here.
- Good for zero-shot visual generalization, bad as a world to *live* in.

### RLBench (FiS-VLA)

- https://github.com/stepjam/RLBench
- CoppeliaSim. FiS-VLA's public sim eval.

### LeRobot built-in gyms

- PushT, ALOHA sim extras. Fine for bringing up a policy; not a detailed 3D world.

### What you should *not* start with

- Full Isaac humanoid + Newton stack on day one.
- Commercial game wrappers (SIMA) — no weights.
- His own gold game, until a candidate can emit macros or a latent goal. Port later.

## Inexpensive robots (hardware)

| Platform | Ballpark | Native checkpoints | Notes |
|---|---|---|---|
| **SO-101** (LeRobot) | **$121.94 US DIY follower** (you print the frame); **$229.88 DIY leader+follower**; vendor kits ~$200–$740 | MolmoAct2-SO100_101, GR00T SO100 example, π0.5 / SmolVLA via LeRobot | Official BOM: [SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100). Docs: [HF SO-101](https://huggingface.co/docs/lerobot/en/so101). "$120/arm" was this follower BOM, not a boxed robot. |
| SO-100 | same generation, older BOM | same | Still in dataset names. |
| LeKiwi | SO arm + mobile base, still hobby $ | LeRobot robot type | Closer to "navigate then manipulate." |
| Koch v1.1 | similar hobby arm | LeRobot | Older sibling of SO-100. |
| Unitree Go2 | **From $1,600** Air list ([shop.unitree.com](https://shop.unitree.com)); Pro ~$2,800; freight $399–$1,000 extra. EDU quote-only. | NaVILA locomotion | Only cheap-*ish* quadruped with a published dual-system nav stack. |
| Unitree G1 / H1 | not cheap | GR00T, NaVILA H1 | Excuse: official humanoid of the GR00T world. Do not buy to *shop*. |
| Franka / WidowX / ALOHA | lab money | almost everyone | Use in sim (LIBERO, CALVIN, SimplerEnv). |
| HopeJR / Reachy Mini / OpenARM | hobby–mid | LeRobot lists them | Weaker VLA checkpoint coverage than SO-101. |

If you want metal: **one SO-101 follower** first (~$122 DIY parts), add a leader when you are ready to teleop your own daytime data. Sim (InternNav or LIBERO) before any purchase. Full numbers: [`06_option_specs.md`](06_option_specs.md#what-120--arm-meant).

## Overnight data factories (criterion 4 adjacent)

| Factory | Input | Output | Ties to |
|---|---|---|---|
| **GR00T-Dreams / Cosmos** | few real demos + image/text prompt | video "dreams" → IDM/LAPA actions → VLA finetune | `groot-n17` |
| OneTwoVLA synthesizer | images, no human labels | embodied VQA + long-horizon plans | `onetwovla` |
| InternData-N1 / VL-LN dialog pipeline | scenes | 830k VLN + dialog-augmented traj | `internvla-n1` |
| RoboCasa procedural | kitchen grammar | unlimited tabletop scenes | GR00T / π0 eval |
| His own gold-game replay | daytime ticks | collapse to macros / silence labels | any S2, sibling Options 1–4 |

DreamGen is the only stack that already matches "daytime experience → overnight artificial data → morning policy" as a published blueprint. That is why a 3B near-dual (GR00T) stays on the shortlist despite a 2B language core.
