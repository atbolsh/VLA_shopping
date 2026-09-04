# Sibling list (game players)

Survey date: 2026-09-02. This is **not** a twelfth shopping card and it does **not** rewrite [`02_scorecard.md`](02_scorecard.md).

The sibling writeup ([`../../stateful_realtime_thinking`](../../stateful_realtime_thinking/README.md)) is: slow plan, cheap twitch, the language core still talks. This note is the **open-weight** shortlist for that problem in a 3D game, plus the Doom / closed zoo so later-you does not re-litigate it.

**Hard filter for the scorecard:** the *policy* has downloadable weights. SIMA 2 can be the best companion on earth; you cannot fetch Gemini. Closed brains stay in [Seen, not scored](#seen-not-scored).

The parseable score table is below. The canvas mirrors it; do not invent a second ranking.

## First crop: rejected (2026-09-03 / 04)

This was the sibling four. All four failed the actual ask (English intermediate goals **while acting**). Sandboxes deleted. **InternVLA-N1 is never the next box.**

1. **JARVIS-VLA** — **rejected 2026-09-03.** Mouth dead (`action_tokens` only).
2. **Chameleon family (RynnVLA-001/002 + WorldVLA)** — **rejected 2026-09-04.** Mouth **garbage**. Dream/decoder not usable.
3. **MolmoAct2-Think** — **rejected 2026-09-03.** Think is depth + action. Molmo2-ER talks because it is a **different** net.
4. **InternVLA-N1 DualVLN** — **rejected 2026-09-04.** Official `step` S2 `llm_output` was **`→→→→`**, not English. `system2_ask` is a separate Qwen that cannot act.

Next window is **not** another sibling game-player. It is EO-1 / ChatVLA / WALL-OSS / ECoT-OpenVLA: [`09_next_session.md`](09_next_session.md).

Later, not this window: OmniJARVIS (gated); Gemma 4 12B + STEVE-1 (Path K).

### Mouth status (2026-09-03)

None of the **product** loops are a companion. Separate VLM cards still answer if you ask them.

| Surface | Talks to you? | Internal language? |
|---|---|---|
| JARVIS-VLA 7B | No | No. Action tokens only. |
| MolmoAct2-Think-LIBERO `predict_action` | No. Caution inject failed. | Depth codes + `generated_token_ids`, not English. |
| Molmo2-ER Ask | **Yes** (seen). Separate net; cannot act. | Ordinary VQA. |
| InternVLA-N1 DualVLN `step` | **No.** Rejected 2026-09-04. | **No.** Printed `→→→→`, not English. |
| InternVLA-N1 System2 `system2_ask` | Yes, and **irrelevant.** Separate Qwen; cannot act. | Ordinary Qwen generate. Disembodied planner — do not pull again. |
| RynnVLA-002 VLA (libero_goal) talk probe | **No** — 2026-09-04: banned-id greedy gave a prompt echo (` Use only commonality`) then a 2-token loop (`speaking`×∞). leftover_english = **garbage**. | Same weights act on the official railroad. Dream/decoder **not usable**. Family killed; do not reopen. |

**Finetune:** do not spend another weekend growing a mouth on these four. Path K (Gemma 4 12B + STEVE-1) is the mouth by construction. Next GPU hours are EO-1 / ChatVLA / WALL-OSS / ECoT, not a DualVLN gate.

## Scorecard (weights available)

Dual-class words are the same as [`../AGENTS.md`](../AGENTS.md). `reasoning_vs_gemma4_12b` uses the same enum. Llama-2-7B / LLaVA-1.5-7B default to `below_reject`.

| id | dual class | S1 eyes | chatty | clock | env | vs 12B | test |
|---|---|---|---|---|---|---|---|
| **jarvis-vla** | `single` | n/a (the 7B *is* the policy) | **mute** — leftover Qwen mouth is gone. 2026-09-03 VQA: only `<\|reserved_special_token_*\|>`, no English. Skip MineStudio. | hitchy single (~**5.5 FPS** 7B, chunk 1) | Minecraft / [MineStudio](https://github.com/CraftJarvis/MineStudio) | `below_ok` (Qwen2-VL-7B, not Gemma 4) | **1 (done)** |
| **rynn-worldvla** | `single` (generative prior) | n/a | **mute** — leftover-BPE **garbage**. Dream/decoder not usable. **Killed 2026-09-04** — not a usable option; do not keep hacking the harness. | robot LIBERO, not a game clock | LIBERO (not a video game) | `below_ok` / unknown; Chameleon-7B ≠ Gemma | **2 (killed)** |
| **omnijarvis** | periodic latent dual (not `true_async`) | **yes** — GROOT-style IL decoder \(\pi(a_t \mid o_{1:t}, z)\) | **paper_qa** — CoT + answers, then 5 FSQ behavior tokens | S2 parked; S1 rolls ~32 steps (fig. caption also says 128 = tokenizer trunk) | Minecraft | `below_reject` (LLaVA-1.5-7B) | later |
| **steve-1** | S1 only | **yes** | **mute** | ~20 FPS | MineRL / MineStudio | n/a | steal-S1 |
| **vpt** | S1 only | **yes** | **mute** | ~20 FPS | Minecraft (human kbd/mouse) | n/a | steal-S1 |
| **rocket-1** | `true_hierarchical` if you bring a VLM | **yes** (SAM-2 + policy on pixels+masks) | planner is yours | S1 real-time; S2 you call | Minecraft | depends on the VLM you plug | steal-S1 |
| **gemma-steve** | `kit` / `true_hierarchical` | **yes** (STEVE-1) | **by_construction** | S1 ticks; S2 when you say | MineStudio | `above` (your 12B) | kit (unlocked; not the next 5090 hour) |

**JARVIS-VLA is not S1/S2.** One Qwen2-VL forward → keyboard/mouse tokens (optional chunk of 2). They built it to *remove* OmniJARVIS’s extra grounding policy.

**OmniJARVIS is S1/S2**, Helix-*interface* (latent + S1 pixels), lockstep replan. Dual score would be **3** on the shopping rubric (S1 has eyes; clocks are not async).

**JARVIS-1** is the language-macro dual (`true_hierarchical`: English goals → STEVE-1). The planner is [API-era](#what-api-era-means). It is not in the table: you download STEVE-1, not a JARVIS-1 VLM.

### Links (scored)

| id | Weights | Code / loop | Paper |
|---|---|---|---|
| jarvis-vla | [`CraftJarvis/JarvisVLA-Qwen2-VL-7B`](https://huggingface.co/CraftJarvis/JarvisVLA-Qwen2-VL-7B) | [JarvisVLA](https://github.com/CraftJarvis/JarvisVLA), [MineStudio](https://github.com/CraftJarvis/MineStudio), [project](https://craftjarvis.github.io/JarvisVLA/) | [arXiv:2503.16365](https://arxiv.org/abs/2503.16365) |
| rynn-worldvla | [`RynnVLA-001-7B-Trajectory`](https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-001-7B-Trajectory), [`WorldVLA`](https://huggingface.co/Alibaba-DAMO-Academy/WorldVLA), [`RynnVLA-002`](https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-002) | [RynnVLA-001](https://github.com/alibaba-damo-academy/RynnVLA-001), [WorldVLA](https://github.com/alibaba-damo-academy/WorldVLA) | [001](https://arxiv.org/abs/2509.15212), [WorldVLA](https://arxiv.org/abs/2506.21539), [002](https://arxiv.org/abs/2511.17502) |
| omnijarvis | [`zhwang4ai/omnijarvis-llava1.5-7b-0524`](https://huggingface.co/zhwang4ai/omnijarvis-llava1.5-7b-0524) (gated, empty card — verify decoder weights before promising a weekend) | [omnijarvis.github.io](https://omnijarvis.github.io/), promised at [craftjarvis.org/OmniJARVIS](https://craftjarvis.org/OmniJARVIS/) | [arXiv:2407.00114](https://arxiv.org/abs/2407.00114) |
| steve-1 | [`CraftJarvis/MineStudio_STEVE-1.official`](https://huggingface.co/CraftJarvis/MineStudio_STEVE-1.official); original [download script](https://github.com/Shalev-Lifshitz/STEVE-1/blob/main/download_weights.sh) | [STEVE-1](https://github.com/Shalev-Lifshitz/STEVE-1) | [arXiv:2306.00937](https://arxiv.org/abs/2306.00937) |
| vpt | [openai/Video-Pre-Training](https://github.com/openai/Video-Pre-Training) (contractor weights via their script) | same repo | [arXiv:2206.11795](https://arxiv.org/abs/2206.11795) |
| rocket-1 | project claims code/demos; treat the **policy** as the download, the VLM as BYO | [ROCKET-1](https://craftjarvis.github.io/ROCKET-1) | [arXiv:2410.17856](https://arxiv.org/abs/2410.17856) |
| gemma-steve | your Gemma 4 12B + STEVE-1 | you write the text/CLIP handoff | Path K: [`../candidates/gemma4-diy.md`](../candidates/gemma4-diy.md) |

Env stack (all Minecraft players): [MineStudio](https://github.com/CraftJarvis/MineStudio), [MineDojo](https://github.com/MineDojo/MineDojo), [MineRL](https://github.com/minerllabs/minerl). Not `pip install && play`: OpenJDK 8, a display (`Xvfb` / VirtualGL), ~24 GB if you vLLM the 7B.

## Chameleon: you tried; stop

Meta [Chameleon](https://arxiv.org/abs/2405.09818) (the *base* 7B) is a mixed-modal LM: one vocab, next-token on **text or VQ image tokens**. That checkpoint can emit English.

**WorldVLA / RynnVLA are not that checkpoint in a chat UI.** The official harness tokenizes the frame and asks for action tokens and/or image tokens. No chat template, no “assistant:” turn, no trained dialogue after action SFT.

Probed 2026-09-04 on the **VLA** weights (not `RynnVLA-001-7B-Base`, not stock Meta Chameleon). Leftover BPE is **garbage**. The decoder look (trained world prompt → next-frame PNG) did not become usable; further harness work was declined. Spec + token map stay in [`11_chameleon_talk_harness.md`](11_chameleon_talk_harness.md) so you do not re-derive them. Do **not** reopen it as a next task.

Do not confuse a caption from the *base* Chameleon with this policy talking.

## What “API-era” means

Said about **JARVIS-1’s planner**, not STEVE-1.

JARVIS-1’s S2 is a *planner LLM you call*, not a released VLM. The [paper](https://arxiv.org/abs/2311.05997) runs **GPT-4 / ChatGPT via the OpenAI API**. Vision is MineCLIP similarity → canned Minecraft sentences stuffed into the GPT prompt (plus templated inventory). Ablations include LLaMA2-70B and a Minecraft-finetuned LLaMA2-13B; those are “bring your own 13B/70B,” not a Hub VLA.

The [GitHub](https://github.com/CraftJarvis/JARVIS-1) never shipped the multimodal descriptor / retrieval. You get STEVE-1 plus a prompt stack. Same 2023 pattern as Voyager / DEPS: pay an API (or host a big Llama) for English plans, separate controller for keys.

## Seen, not scored

Closed brain, API-only player, or a benchmark that *uses* APIs. Links so you can re-read; do not put them on the scorecard.

| Thing | Why it came up | Why it fails the filter | Links |
|---|---|---|---|
| **SIMA 2** | Best *companion*: Gemini, embodied QA, **asks clarifiers**, action chunks, commercial 3D / MineDojo / Genie-3 | No weights. You will not hack Google for a checkpoint. | [arXiv:2512.04797](https://arxiv.org/abs/2512.04797), SIMA 1 [arXiv:2404.10179](https://arxiv.org/abs/2404.10179) |
| **Tencent GIGA** | Dual FPS: VLM planner + LSTM/RL executor; can refuse a bad order (Peacekeeper Elite / The Finals) | Closed; gamescom talk, not a Hub card | [Inven writeup](https://www.invenglobal.com/articles/25084/tencent-unveils-shooter-ai-agent-that-rejects-player-orders) |
| **Voyager** | Lifelong Minecraft, GPT-4 writes JS skills | GPT-4 API | [GitHub](https://github.com/MineDojo/Voyager), [arXiv:2305.16291](https://arxiv.org/abs/2305.16291) |
| **JARVIS-1** | Real `true_hierarchical` Minecraft (MLM → language goals → STEVE-1) | Planner is API-era; multimodal pieces unreleased | [GitHub](https://github.com/CraftJarvis/JARVIS-1), [arXiv:2311.05997](https://arxiv.org/abs/2311.05997), [page](https://craftjarvis-jarvis1.github.io/) |
| **DEPS** | Describe / explain / plan / select in Minecraft | LLM via API | [arXiv:2302.01560](https://arxiv.org/abs/2302.01560) |
| **Cradle** | Screen + kbd/mouse on RDR2, Stardew, etc. Code is open | Brain is GPT-4o. **Pauses** real-time games while it thinks | [BAAI-Agents/Cradle](https://github.com/BAAI-Agents/Cradle), [page](https://baai-agents.github.io/Cradle/), [arXiv:2403.03186](https://arxiv.org/abs/2403.03186) |
| **GameSense** | VLM “don’t pause” vs Cradle; evaluated in the Doom / action-game setting | Framework + API VLMs, not a pullable player | [arXiv:2503.21263](https://arxiv.org/abs/2503.21263) |
| **VideoGameBench** | Doom / Doom II / Quake-class titles + other 90s games; Lite **pauses** for CoT | Eval harness; you bring Gemini / GPT-4o / Claude keys | [vgbench.com](https://vgbench.com/), [GitHub](https://github.com/alexzhang13/videogamebench), [arXiv:2505.18134](https://arxiv.org/abs/2505.18134) |
| **MineDreamer** | VLM dreams a future frame, STEVE-1 acts | Planner typically not a self-contained open VLA | cited from JARVIS-VLA related work (Zhou et al. 2024) |

There is still **no** open-weight, chatty, true-async Doom (or generic FPS) player. The intersection of SIMA-2-chatty × Helix-dual × weights × 3D is empty. Minecraft via MineStudio is the only open 3D env with downloadable players.

## Sibling smoke (closed)

Success was supposed to be “it answered in English *or* it moved.” All four product loops failed the English-while-acting bar. Folders deleted.

| Order | What | Success |
|---|---|---|
| S | JARVIS-VLA screenshot VQA | **Rejected 2026-09-03.** `action_tokens` only. |
| B | MolmoAct2 Think-LIBERO + Molmo2-ER Ask | **Rejected 2026-09-03.** Ask talks (other net). Think mute. |
| C | WorldVLA / RynnVLA-002 | **Rejected 2026-09-04.** Mouth garbage; dream not usable. |
| A | InternVLA-N1 DualVLN | **Rejected 2026-09-04.** `llm_output` = `→→→→`. Never next. |
| — | EO-1 / ChatVLA / WALL-OSS / ECoT | **Next window.** Same weights must talk and act. [`09_next_session.md`](09_next_session.md). |
| K | Gemma 4 12B + STEVE-1 dummy handoff | Unlocked; not this window. |

## Pull log

### jarvis-vla (2026-09-03)

- **Box:** 1× RTX 5090, `demo_sandboxes/jarvis_vqa`.
- **Prompt:** official SFT / `VLLM_AGENT` layout — `{question}\nobservation: \n` then image. Qwen2-VL chat template on `CraftJarvis/JarvisVLA-Qwen2-VL-7B`.
- **Frames:** official `CraftJarvis/minecraft-vla-sft` **valid** split (not the 106 GB train set).
- **Mouth:** `action_tokens`. Reply is only `<|reserved_special_token_*|>`. No English, no other leftover tokens, no useful feedback. First decode (`skip_special_tokens=True`) looked like garbage because it stripped the action stream.
- **Decision:** skip `demo_sandboxes/jarvis_minestudio`. Same weights; will not talk. Minecraft-with-a-mouth is smoke K (Gemma 4 12B + STEVE-1) when you want it.
- **Do not** treat OmniJARVIS or JARVIS-1 as the same result. Those are other animals.

### molmoact2 (2026-09-03)

- **Box:** 1× RTX 5090. Think-LIBERO and Molmo2-ER **cannot** sit in VRAM together; ran as two kernel sessions.
- **Ask (`allenai/Molmo2-ER`):** leftover / intended mouth works. Separate VLM. Answered the table question in English. Not the policy.
- **Think (`allenai/MolmoAct2-Think-LIBERO`):** official `predict_action` on the card’s libero_10 / ep0 / t0 cameras + EEF. Returned a 10×7 continuous action chunk (and depth bins). Internal “think” is `<depth_start>` … depth codes … `<depth_end>`, then the flow expert — not a `<think>` chat span.
- **Inject (`think_inject.ipynb`):** spliced “if an instruction is unclear, ask a follow-up before committing; keep the arm still until you are certain” into the official `The task is to {task}` slot (`normalize_language=False`). **Did not** get follow-ups or a still arm. Policy still committed actions. Prompt-inject will not grow a mouth on this SFT.
- **Finetune:** plausible on **Molmo2-ER (or Gemma 4 12B) as a gate**, then call Think only on a clean task. Low confidence that further SFT on `predict_action` will make Think interview you; that head is trained to emit depth then move.
- **Decision:** Path R still stands as an arm policy. Sibling “talk while acting” is not this checkpoint. Crop closed.

### rynn-worldvla (2026-09-04)

- **Box:** 1× RTX 5090 (32 GB), `demo_sandboxes/rynn_worldvla`, transformers 4.43.0.
- **Load:** `VLA_model_256/libero_goal` is `ChameleonXLLMXForConditionalGeneration_ck_action_head` (per its `config.json`), **not** the base xllmx class. Harness reads the shards + Meta `vqgan.ckpt` directly and verified **593/593 Parameters elementwise** against the files (`load verified … tensors 593`). Saved names match module names; no translator needed. `vqgan.ckpt` has two extras (`custom_layer.*`) with no HF slot — dropped, same as official convert.
- **Act:** official ItemProcessor railroad (`What action…?<|state|><|image|><|image|>`, zeros(8) state for the GIF frame) + `generate_dis_ma` → five clean `10004…15004` chunks ending `8710`; smooth monotone dim-0 trajectory. Deterministic across boxes. The policy acts.
- **Mouth:** banned-id greedy (only BPE ≥16384 allowed) → ` Use only commonality` + `sound` + `speaking`×30 (ids `54812, 17017` looping). **leftover_english = garbage.** Prompt-echo + degenerate cycle, not English. First run said `usable` — false positive in the old ≥3-words verdict; fixed to require distinct words and no short cycle.
- **Dream:** vendor eval helper carries the *older WorldVLA* prompt (“Generate the image based on the current image and the action.”) — off-distribution for 002 cards, produced malformed blocks. The 002 cards were trained on “Generate the next image based on the provided sequence of historical images and corresponding actions.” + `<|image|><|image|><|action|>`. With that prompt, generation can be on-distribution (one run: 2017/2088 image-range tokens, one canonical 1060-token 512² block). Official `decode_image` still dies on anything but a perfect `8197` + 2 grid toks + 32×33 (newline `8803` every 33rd) + `8196` span. Ablation Rung 2: `push_left` junk short spans; `push_right` hit `max_new_tokens=3000` with fragmented `8197…8196` pairs; `grip_close` 1028 (no newlines) + 1059 (`KeyError 8803`). Harness recoveries (skip junk spans, flat 1024-body, pad-one-short, stream-stitch) did not produce a usable action-conditioned next-frame look. Owner: do **not** fine-tune the harness further.
- **Decision:** **not a usable option.** Mouth dead like JARVIS / Molmo-Think. Decoder/dream look closed. Do not reopen. Act-on-railroad is real and not enough. Crop closed. Next window is EO-1 / ChatVLA / WALL-OSS / ECoT — not InternVLA-N1.

### internvla-n1 DualVLN (2026-09-04)

- **Box:** 2× RTX 5090, `demo_sandboxes/internvla_n1` (deleted).
- **Load:** DualVLN shards on `cuda:0`. S1 module weights verified elementwise vs safetensors (7/7 probes). Warmup was one step on a **black dummy** frame (throwaway).
- **Walk loop:** official `InternVLAN1AsyncAgent.step` on their sample RGB stream (“Turn around and walk out of this office…”).
- **Mouth:** S2 `llm_output` on the logged step was **`→→→→`** (arrow tokens). `pixel_goal` was `None`. That is not English intermediate goals and not a SIMA-2 clarifier.
- **Ask cell:** `system2_ask` on `InternVLA-N1-System2` / `cuda:1` is a **separate** Qwen that cannot act. Same class of mistake as Molmo2-ER. Disembodied planner — ignore.
- **Decision:** **rejected.** Not a usable option for the ask. Sandbox deleted. **Never the next box.** Do not reopen DualVLN, System-2 chat, Habitat, or “maybe the arrows mean something.”
