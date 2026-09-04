# Brief

Survey date: 2026-09-02.

You already finetune **Gemma 4 12B** on a navigation-style game (fine `CLOCK` / `ANTICLOCK` / `FORWARD` ticks). That model reasons well enough and has **no** quick-twitch loop. Sibling writeup: [`../stateful_realtime_thinking`](../../stateful_realtime_thinking/README.md). Open-weight game-player shortlist (SIMA 2 excluded): [`10_sibling_list.md`](10_sibling_list.md). First crop **rejected 2026-09-04** (JARVIS, Molmo-Think, Rynn, InternVLA-N1 DualVLN). InternVLA-N1 is never the next box. Next window: **start with EO-1**, then ChatVLA → WALL-OSS → ECoT. Same weights must talk **and** act. None of these four are interruptible. EO-1 and ECoT stills are on-distribution; ChatVLA and WALL-OSS are stand-ins.

You want an off-the-shelf or minimally-finetuned **LVA** (your word; literature name is **VLA**, Vision-Language-Action) that can later sit in a loop that:

1. acts in a world during the day,
2. manufactures its own training data overnight from those experiences,
3. improves itself without a human writing every trajectory.

## Constraints (as scored)

1. **Size.** Prefer 7B-class. Hard cap 20B unless there is a training excuse (LoRA on a frozen giant, or a 2B world-model used only at night). You already rejected Gemma 4 e4B for weak reasoning, so "tiny and cute" is not a virtue on the planner.
2. **Dual loop already built in.** Sibling Option 5: slow language/plan, fast monitor/act. OpenHelix's test: System 1 must see **fresh pixels**, not only a stale latent. Action-chunk / flow-matching heads (π0, GR00T N1.7) are useful but are scored as *near-dual*.
3. **Reasoning.** Gemma 4 12B is the bar. Llama-2-7B / LLaVA-1.5-7B dual-system papers will lose this comparison. Qwen2.5-VL-7B and Molmo2-ER are the open backbones that have a chance.
4. **A world to play in.** Either many environments, or one detailed 3D env you can install. Bonus: a checkpoint for a cheap robot (SO-101 follower BOM **$121.94** if you print the frame — see `06_option_specs.md`). Navigation-shaped envs (Habitat, InternNav, Isaac VLN) are closer to the gold game than tabletop LIBERO.

## What this repo is for

Not pulling weights yet. Compile a balanced shortlist, keep papers local, and leave cards that both a human and a later agent can update after the first look-and-sandbox pass (`notes/09_next_session.md`, then `notes/04_test_plan.md`).
