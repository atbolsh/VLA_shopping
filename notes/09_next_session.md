# Next session (look, then small sandboxes)

Decided 2026-09-02; same-evening revision after the sibling/game-player pass. Do **not** start this in the window that wrote the note. The next agent (or you) starts here.

This is a **look-then-sandbox** order, not a rewrite of the twelve-card scorecard. InternVLA-N1 is still the Path N buy. JARVIS-VLA is **not** a shopping card; it is the sibling (talk + 3D game) first look.

**Do not download the twelve-card zoo.** Watch, then one small install at a time.

Sibling scorecard + Doom/closed zoo: [`10_sibling_list.md`](10_sibling_list.md).

## Look (this order)

### 1. JARVIS-VLA (sibling first)

Open 7B Minecraft VLA. `single`, hitchy (~5.5 FPS), leftover Qwen chat. Custom S1 later is the same job as Path K.

| What | URL |
|---|---|
| Weights | https://huggingface.co/CraftJarvis/JarvisVLA-Qwen2-VL-7B |
| Code / rollout | https://github.com/CraftJarvis/JarvisVLA |
| Env | https://github.com/CraftJarvis/MineStudio |
| Project | https://craftjarvis.github.io/JarvisVLA/ |
| Paper | https://arxiv.org/abs/2503.16365 |
| Sibling card | [`10_sibling_list.md`](10_sibling_list.md) |

Ask while looking: does a screenshot still get an English answer? If action SFT ate the mouth, you know before a weekend of JDK 8.

### 2. RynnVLA-001 / 002 + WorldVLA (Chameleon)

Same DAMO family. You like the vision decoder. Official loop emits actions / next frames, not chat. **Note-goal (not a Cursor official goal):** leftover English from the VLA weights, decoder kept. Spec: [`11_chameleon_talk_harness.md`](11_chameleon_talk_harness.md). No code this window. Base Meta Chameleon can emit text; do not confuse that with this checkpoint.

Watch for: next-frame generation, action-conditioned video, wrist-cam generation (002), ego-human-video pretrain (001). There is **no hosted playground**. Videos and HF GIFs are the look.

| What | URL |
|---|---|
| RynnVLA-001 blog (videos in-page) | https://huggingface.co/blog/Alibaba-DAMO-Academy/rynnvla-001 |
| RynnVLA-001 GitHub (YouTube + Bilibili badges) | https://github.com/alibaba-damo-academy/RynnVLA-001 |
| RynnVLA-001 weights | https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-001-7B-Trajectory |
| WorldVLA HF (action GIFs + world-model GIFs) | https://huggingface.co/Alibaba-DAMO-Academy/WorldVLA |
| WorldVLA / RynnVLA-002 code | https://github.com/alibaba-damo-academy/WorldVLA |
| RynnVLA-002 HF (LIBERO VLA + world-model tables) | https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-002 |
| Papers | [001](https://arxiv.org/abs/2509.15212), [WorldVLA](https://arxiv.org/abs/2506.21539), [002](https://arxiv.org/abs/2511.17502) |

Ask while watching: can this thing show you *what happens if I take this action* as pixels? That is why it is entry 2, not a footnote.

### 3. MolmoAct2

| What | URL |
|---|---|
| Blog / videos | https://allenai.org/blog/molmoact2 |
| Think-LIBERO card | https://huggingface.co/allenai/MolmoAct2-Think-LIBERO |
| SO-100/101 card | https://huggingface.co/allenai/MolmoAct2-SO100_101 |
| Code | https://github.com/allenai/molmoact2 |
| Card in this repo | [`../candidates/molmoact2.md`](../candidates/molmoact2.md) |

No hosted net. Watch Think / traces / SO-10x. Compare to Rynn: MolmoAct2 reasons in depth tokens; it does **not** decode a future RGB frame. Unlike JARVIS-VLA / Rynn, the Molmo2-ER backbone *can* do VQA if you ask.

### 4. InternVLA-N1

| What | URL |
|---|---|
| **Hosted Gradio** (down as of 2026-09-03: 401 / remote backend) | https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo — do not hunt clones. Local sandbox: [`../demo_sandboxes/internvla_n1`](../demo_sandboxes/internvla_n1/README.md) |
| Project page / videos | https://internrobotics.github.io/internvla-n1.github.io/ |
| S2 card | https://huggingface.co/InternRobotics/InternVLA-N1-System2 |
| DualVLN (recommended whole system) | https://huggingface.co/InternRobotics/InternVLA-N1-DualVLN |
| Card in this repo | [`../candidates/internvla-n1.md`](../candidates/internvla-n1.md) |

S1 **does** get fresh RGB (DualVLN) or RGB-D (NavDP*). Pixel-goal is the S2→S1 *handoff*, not S1’s only input. Product loop is mute. See [`08_community_gems.md`](08_community_gems.md) only for the M1 contrast; do not re-open that.

## Then: small sandboxes (one at a time)

After the looks. Success is “it answered or it moved,” not a new scorecard.

| Order | Sandbox | Success |
|---|---|---|
| S | JARVIS-VLA: screenshot VQA, then one MineStudio rollout | English leftover mouth *or* you log that SFT ate it; agent clicks in Minecraft. |
| A | InternNav official inference-only notebook (`demo_sandboxes/internvla_n1`) — hosted Gradio is down | Follow one English instruction on their sample RGB stream; see pixel-goal + S2 text. |
| B | MolmoAct2-Think-LIBERO **or** `lerobot-eval` on the LeRobot MolmoAct2/LIBERO card | One LIBERO task completes. |
| C | WorldVLA or RynnVLA-002 **LIBERO** from their GitHub | One LIBERO suite, one *action → next frame* sample, **and** one harness attempt at leftover English (usable reply or a logged miss). |

Do **not** install Habitat, Isaac, or an SO-101 until a sandbox has a winner you still care about. Gemma+STEVE-1 waits until S’s mouth is dead or you want Path K in Minecraft.

Smoke-0 reasoning prompts and the older three-path deep dives stay in [`04_test_plan.md`](04_test_plan.md). Run those only after a sandbox you like.
