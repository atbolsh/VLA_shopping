# Next session (look, then small sandboxes)

Decided 2026-09-02. Do **not** start this in the window that wrote the note. The next agent (or you) starts here.

This is a **look-then-sandbox** order, not a rewrite of the scorecard. InternVLA-N1 is still the Path N buy. RynnVLA is still honorable. The point of going Rynn first is to *see* the vision-decoder / overnight-pixels family before committing a weekend to Habitat or LIBERO.

**Do not download the twelve-card zoo.** Watch, then one small install at a time.

## Look (this order)

### 1. RynnVLA-001 / 002 + WorldVLA

Same DAMO family. Watch for: next-frame generation, action-conditioned video, wrist-cam generation (002), ego-human-video pretrain (001). There is **no hosted playground**. Videos and HF GIFs are the look.

| What | URL |
|---|---|
| RynnVLA-001 blog (videos in-page) | https://huggingface.co/blog/Alibaba-DAMO-Academy/rynnvla-001 |
| RynnVLA-001 GitHub (YouTube + Bilibili badges) | https://github.com/alibaba-damo-academy/RynnVLA-001 |
| RynnVLA-001 weights | https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-001-7B-Trajectory |
| WorldVLA HF (action GIFs + world-model GIFs) | https://huggingface.co/Alibaba-DAMO-Academy/WorldVLA |
| WorldVLA / RynnVLA-002 code | https://github.com/alibaba-damo-academy/WorldVLA |
| RynnVLA-002 HF (LIBERO VLA + world-model tables) | https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-002 |
| Papers | [001](https://arxiv.org/abs/2509.15212), [WorldVLA](https://arxiv.org/abs/2506.21539), [002](https://arxiv.org/abs/2511.17502) |

Ask while watching: can this thing show you *what happens if I take this action* as pixels? That is the overnight-loop reason it jumped the look queue.

### 2. MolmoAct2

| What | URL |
|---|---|
| Blog / videos | https://allenai.org/blog/molmoact2 |
| Think-LIBERO card | https://huggingface.co/allenai/MolmoAct2-Think-LIBERO |
| SO-100/101 card | https://huggingface.co/allenai/MolmoAct2-SO100_101 |
| Code | https://github.com/allenai/molmoact2 |
| Card in this repo | [`../candidates/molmoact2.md`](../candidates/molmoact2.md) |

No hosted net. Watch Think / traces / SO-10x. Compare to Rynn: MolmoAct2 reasons in depth tokens; it does **not** decode a future RGB frame.

### 3. InternVLA-N1

| What | URL |
|---|---|
| **Hosted Gradio** (the one real interactive VLA-nav) | https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo |
| Project page / videos | https://internrobotics.github.io/internvla-n1.github.io/ |
| S2 card | https://huggingface.co/InternRobotics/InternVLA-N1-System2 |
| DualVLN (recommended whole system) | https://huggingface.co/InternRobotics/InternVLA-N1-DualVLN |
| Card in this repo | [`../candidates/internvla-n1.md`](../candidates/internvla-n1.md) |

S1 **does** get fresh RGB (DualVLN) or RGB-D (NavDP*). Pixel-goal is the S2→S1 *handoff*, not S1’s only input. See [`08_community_gems.md`](08_community_gems.md) only for the M1 contrast; do not re-open that.

## Then: small sandboxes (one at a time)

After the three looks. Success is “it moved in a public env,” not a new scorecard.

| Order | Sandbox | Success |
|---|---|---|
| A | InternNav Gradio (already open from look 3) if it still works | Follow one English instruction in a house without clicking actions. |
| B | MolmoAct2-Think-LIBERO **or** `lerobot-eval` on the LeRobot MolmoAct2/LIBERO card | One LIBERO task completes. |
| C | WorldVLA or RynnVLA-002 **LIBERO** checkpoint from their GitHub | One LIBERO suite, and if cheap: one *action → next frame* sample so you see the decoder. |

Do **not** install Habitat, Isaac, or an SO-101 until A/B/C have a winner you still care about.

Smoke-0 reasoning prompts and the older three-path deep dives stay in [`04_test_plan.md`](04_test_plan.md). Run those only after a sandbox you like.
