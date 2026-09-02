# LVA / VLA shopping

Notes for picking a **Vision-Language-Action** model (literature name: VLA; here: LVA) that already splits **slow plan** from **quick twitch**, stays near the 7B class, and can live in a 3D world — ideally one that can later invent its own overnight training data.

This repo does **not** download weights. It is the shopping list. Cards are written so a later agent can update scores after the first pull (`notes/04_test_plan.md`).

Sibling problem statement (why dual-loop at all): [`../stateful_realtime_thinking`](../stateful_realtime_thinking/README.md).

## Start here

1. [`notes/06_option_specs.md`](notes/06_option_specs.md) — **the parseable list.** Every option has the same four headings: Network (links), Action (do you train S1?), World (env/robot/price), Paper.
2. [`notes/00_brief.md`](notes/00_brief.md) — your four constraints.
3. [`notes/01_taxonomy.md`](notes/01_taxonomy.md) — what "true dual" means. π0 and GR00T are useful and **not** Helix.
4. [`notes/02_scorecard.md`](notes/02_scorecard.md) or the canvas — pick **one** path. Do not clone twelve repos.
5. **Next window:** [`notes/09_next_session.md`](notes/09_next_session.md) — look RynnVLA → MolmoAct2 → InternVLA-N1, then small sandboxes.

Env/robot/demo lists: [`notes/03_envs_and_robots.md`](notes/03_envs_and_robots.md), [`notes/05_demos.md`](notes/05_demos.md). Community / decoder-head sweep: [`notes/08_community_gems.md`](notes/08_community_gems.md).

Machine-facing cards: [`candidates/`](candidates/) (YAML frontmatter + `schema/candidate.schema.json`). Agent conventions: [`AGENTS.md`](AGENTS.md).

## Three paths (do not average them)

| Path | Buy | If you care most about |
|---|---|---|
| **N — navigation** | [InternVLA-N1](candidates/internvla-n1.md) | A house you can install (Habitat / InternNav), a real dual loop, a 7B-class planner that might match Gemma 4 12B. Hosted Gradio: [InternNav-Eval-Demo](https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo). Backup: [NaVILA](candidates/navila.md) on a Go2. |
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

## Next session (look, then sandboxes)

Scorecard pull numbers are shopping rank, not the next window. Next window:

1. Watch **RynnVLA-001 / 002 + WorldVLA** (videos / HF GIFs; no hosted playground).
2. Watch **MolmoAct2** ([blog](https://allenai.org/blog/molmoact2)).
3. Play **InternVLA-N1** ([Gradio](https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo) + homepage videos).
4. Then one small sandbox at a time: Gradio house, MolmoAct2-LIBERO, WorldVLA/RynnVLA-002 LIBERO. Habitat / SO-101 wait.

Full link list: [`notes/09_next_session.md`](notes/09_next_session.md). Later smokes: [`notes/04_test_plan.md`](notes/04_test_plan.md).
