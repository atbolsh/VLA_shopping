# LVA / VLA shopping

**Build-out (decided 2026-09-05): EO-1 + LIBERO.** Not Bridge visual matching. Not ChatVLA, WALL-OSS, or ECoT.

Why this pair:

- **Mouth already works.** The same `IPEC-COMMUNITY/EO-1-3B` weights print readable English on their VL-eval railroad (`chat.ipynb`). That was the crop’s bar. ChatVLA / WALL-OSS were never opened; ECoT is blocked on a kernel/`timm` mess and a Llama-2-7B core you already reject.
- **Published control numbers, and they are high.** Their LIBERO suite is 98.2% after a lightweight finetune — the number every other VLA quotes. Official railroad: `experiments/2_libero` and LeRobot `lerobot-eval --env.type=libero`.
- **LIBERO is a real 3D physics gym you can stay in.** MuJoCo / robosuite Franka, four suites, many language tasks, long-horizon. Bridge *visual matching* is also physics (SAPIEN), but the shipped WidowX exam is **four short scenes**. BridgeData V2 (the real videos in EO-1’s pretrain) is a dataset, not a playable world. You are choosing the lounge, knowing the raw 3B *saw* Bridge in pretrain and *reports* LIBERO after a modest tune.
- **Data and eval are actually available.** LIBERO demos, LeRobot env, and their tune scripts exist. Bridge VM needs SimplerEnv + Vulkan; that install is what you walked away from.

This is not Path N and not Gemma 4 12B. Planner is 3B. Not interruptible. The 3B Hub dump is a generalist; LIBERO act needs their LIBERO `robot_config` / finetune, not the empty Hub config and not the WidowX wrapper in `play.ipynb`.

Sandbox: [`demo_sandboxes/eo1`](demo_sandboxes/eo1/README.md). Crop log: [`notes/09_next_session.md`](notes/09_next_session.md).

---

Notes for picking a **Vision-Language-Action** model (literature name: VLA; here: LVA) that already splits **slow plan** from **quick twitch**, stays near the 7B class, and can live in a 3D world — ideally one that can later invent its own overnight training data.

This repo does **not** download weights. It is the shopping list. Cards are written so a later agent can update scores after the first pull (`notes/04_test_plan.md`).

Sibling problem statement (why dual-loop at all): [`../stateful_realtime_thinking`](../stateful_realtime_thinking/README.md).

## Start here

1. [`notes/06_option_specs.md`](notes/06_option_specs.md) — **the parseable list.** Every option has the same four headings: Network (links), Action (do you train S1?), World (env/robot/price), Paper.
2. [`notes/00_brief.md`](notes/00_brief.md) — your four constraints.
3. [`notes/01_taxonomy.md`](notes/01_taxonomy.md) — what "true dual" means. π0 and GR00T are useful and **not** Helix.
4. [`notes/02_scorecard.md`](notes/02_scorecard.md) or the canvas — pick **one** path. Do not clone twelve repos.
5. **Next window:** [`notes/09_next_session.md`](notes/09_next_session.md) — EO-1, ChatVLA, WALL-OSS, ECoT-OpenVLA only. First crop rejected. InternVLA-N1 is never the next box.

Env/robot/demo lists: [`notes/03_envs_and_robots.md`](notes/03_envs_and_robots.md), [`notes/05_demos.md`](notes/05_demos.md). Community / decoder-head sweep: [`notes/08_community_gems.md`](notes/08_community_gems.md). Sibling (talk + 3D game) list: [`notes/10_sibling_list.md`](notes/10_sibling_list.md).

Machine-facing cards: [`candidates/`](candidates/) (YAML frontmatter + `schema/candidate.schema.json`). Agent conventions: [`AGENTS.md`](AGENTS.md).

## Three paths (do not average them)

| Path | Buy | If you care most about |
|---|---|---|
| **N — navigation** | [InternVLA-N1](candidates/internvla-n1.md) | Architecture card only. **Tried 2026-09-04 and rejected** (DualVLN S2 printed `→→→→`). Do not reopen. Backup on paper: [NaVILA](candidates/navila.md) on a Go2. |
| **K — keep your brain** | [Gemma 4 12B + stolen S1](candidates/gemma4-diy.md) | Criterion 3. Every 2024 dual-system 7B uses LLaVA/Llama-2, which is the e4B failure mode. Steal OpenHelix's `<ACT>` bridge or InternVLA-N1's S1. Read [OpenHelix](candidates/openhelix.md) and [FiS-VLA](candidates/fis-vla.md) as kits, not oracles. |
| **R — cheap robot + nights** | [MolmoAct2-Think](candidates/molmoact2.md) on SO-101, or [GR00T N1.7](candidates/groot-n17.md) + DreamGen | A ~$122 DIY follower arm ([BOM](https://github.com/TheRobotStudio/SO-ARM100)), or the only published "daytime demos → overnight dreams → morning policy" factory. π0.5 is the smoother LeRobot on-ramp and a worse planner. |

Helix ([video](https://www.figure.ai/news/helix)) is the closed picture of Path N/K done right: 7B @ ~8 Hz, 80M @ 200 Hz, S1 has its own eyes.

## The 7B-class true duals (criterion 1 + 2)

Start the list here, as requested. **None of these beat Gemma 4 12B on general reasoning.** That is the point of Path K.

| Model | S2 | S1 | Playable world |
|---|---|---|---|
| InternVLA-N1 | Qwen2.5-VL-7B | DualVLN / NavDP* | Habitat + Isaac, Gradio |
| NaVILA | Llama-3-8B VILA | locomotion RL | Habitat, Isaac Lab, Go2 |
| FiS-VLA | Llama-2-7B | last VLM blocks | RLBench |
| OpenHelix | LLaVA-1.5-7B | 3D Diffuser Actor | CALVIN |
| RoboDual | OpenVLA-7B | DiT specialist | CALVIN |

## Size excuses (criterion 1)

Nothing here needs to be >20B. The dangerous direction is *down*: 2B–3B VLMs (GR00T's Cosmos-Reason2, π0's PaliGemma, NORA, SmolVLA) will likely fail the same test that killed Gemma 4 e4B. Valid extras above the daytime budget: a Cosmos-Predict2.5 world model **used only at night**, or a 27B relabeler (MolmoAct2's pipeline) that never sits in the control loop.

## Layout

```
notes/           human narrative
candidates/      one card per model + index.yaml + honorable.md
schema/          JSON Schema for card frontmatter
papers/          bibliography + pdfs/
scripts/         fetch_papers.sh
AGENTS.md        how a later agent should edit this
```

## Next session

**EO-1 + LIBERO.** Crop of four is closed. First crop (JARVIS, Molmo-Think, Rynn, InternVLA-N1 DualVLN) stays **rejected**.

Full note: [`notes/09_next_session.md`](notes/09_next_session.md). Sandbox: [`demo_sandboxes/eo1`](demo_sandboxes/eo1/README.md). **Do not run `setup.sh` on this notes machine.**
