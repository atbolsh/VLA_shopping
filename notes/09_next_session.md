# Next session (English while acting)

Decided 2026-09-04 after the first crop failed. Do **not** start this in the window that wrote the note. **Next time: start with EO-1**, then ChatVLA → WALL-OSS → ECoT. One sandbox at a time.

**InternVLA-N1 is not the next box. Never again.** DualVLN is rejected. Do not reopen it, do not “just try System-2 chat,” do not rent 2×5090 for it.

The first crop (JARVIS-VLA, MolmoAct2-Think, RynnVLA-002 / WorldVLA, InternVLA-N1 DualVLN) is **closed**. Those sandboxes were deleted. Logs stay below and in [`10_sibling_list.md`](10_sibling_list.md).

## What you are actually testing

SIMA 2 sets **intermediate goals in plain English while it acts**. That is the bar.

Success is: the **same policy weights** print a readable English plan / subtask / “I will now …” **and** an action, on one forward path. Fail is: action tokens only, arrows, depth bins, a second VLM that cannot move, or a leftover mouth that is garbage.

**Do not** pull disembodied planner brains (RoboBrain, Pelican-VL, InternVLA-N1-System2, Molmo2-ER). Those talk. They do not act. That was the last crop’s mistake.

These four are **below** the Gemma 4 12B reasoning bar (3B, 2B, ~3B+MoT, Llama-2-7B). That is stated up front. This window is not Path N and it is not a 12-card rewrite. It is “does any open VLA actually talk while it moves?”

**None of them are interruptible.** No true-async dual, no high-rate S1 that keeps seeing fresh pixels, no trained “something unexpected happened — stop and re-plan.” EO-1 interleaves text and flow in one generate. ChatVLA re-queries every *N* steps. WALL-OSS’s Uni-CoT paper can skip or interleave CoT, still one net. ECoT runs the full TASK/PLAN/SUBTASK/MOVE chain, then one action. OneTwoVLA is the surprise-flip paper; it has no weights. Fine for this window.

**On-distribution stills (this smoke):** EO-1 uses their official `demo_data` frames (reasoning demo, not LIBERO). ECoT uses official Bridge `test_obs.png` + `unnorm_key=bridge_orig`. ChatVLA and WALL-OSS have no public observation PNGs / no installable training env in-folder — those two are stand-in stills and said so. Closed-loop LIBERO/SimplerEnv waits until a mouth works.

## Closed crop (do not reopen)

| Model | Date | What happened | Next? |
|---|---|---|---|
| JARVIS-VLA 7B | 2026-09-03 | Official railroad = `action_tokens` only. No English. | Never. |
| MolmoAct2-Think-LIBERO | 2026-09-03 | Depth bins + action chunk. Caution inject ignored. Molmo2-ER talks because it is a **different** net. | Never as a mouth. |
| RynnVLA-002 / WorldVLA | 2026-09-04 | Act railroad works. Leftover BPE **garbage**. Dream/decoder not usable. | Never. |
| InternVLA-N1 DualVLN | 2026-09-04 | Official `step` S2 `llm_output` was **`→→→→`** (arrow tokens), not English goals. `pixel_goal` None on the logged step. `system2_ask` is a separate Qwen that cannot act. | **Never.** |

## Look, then one sandbox (this order)

### 1. EO-1

Closest official claim: one decoder, interleaved vision-text-action, `processor.generate` returns **text and actions**.

| What | URL |
|---|---|
| Weights | https://huggingface.co/IPEC-COMMUNITY/EO-1-3B |
| Code | https://github.com/EO-Robotics/EO1 (moving to [SHAILAB-IPEC/EO1](https://github.com/SHAILAB-IPEC/EO1)) |
| Paper | https://arxiv.org/abs/2508.21112 |
| Sandbox | [`../demo_sandboxes/eo1`](../demo_sandboxes/eo1/README.md) |

3B Qwen2.5-VL. Official HF snippet: `output = processor.generate(model, batch)` → `output.text` + `output.action`. Also `select_action` (act only) and `model.generate` (reason only). Use the **unified** generate. Sample frames: their `demo_data/example1.jpg` / `example2.png`.

Ask on the box: did the **same** 3B emit a readable English intermediate goal **and** an action vector?

### 2. ChatVLA (v1 weights)

MoE so robot SFT does not wipe VQA. ChatVLA-2 (math / open-world paper) has **no public robot weights**. You pull ChatVLA-1.

| What | URL |
|---|---|
| Weights | https://huggingface.co/zzymeow/ChatVLA |
| Code | https://github.com/midea-ai/ChatVLA_public (same as [tutujingyugang1/ChatVLA_public](https://github.com/tutujingyugang1/ChatVLA_public)) |
| Paper (v1) | https://arxiv.org/abs/2502.14420 |
| Paper (v2, no robot ckpt) | https://arxiv.org/abs/2505.21906 |
| Sandbox | [`../demo_sandboxes/chatvla`](../demo_sandboxes/chatvla/README.md) |

Qwen2-VL-2B + control expert. Official robot loop: `policy.evaluate(**batch)` in their `evaluate/evaluate_robot.py` (`eval_in_vqa` is a flag on **these** weights, not a second card). Need their `preprocessor_config.json` / `chat_template.json` from Qwen2-VL-2B-Instruct if the Hub dump is incomplete.

Ask on the box: does `evaluate` print English in `outputs`, or only an action chunk? VQA on the **same** checkpoint is a second cell, not a substitute for talk-while-acting.

### 3. WALL-OSS

Paper claim is Uni-CoT: instruction → reasoning / subtask → continuous action in one net.

| What | URL |
|---|---|
| Weights (CoT paper) | https://huggingface.co/x-square-robot/wall-oss-flow |
| Newer deploy ckpt | https://huggingface.co/x-square-robot/wall-oss-0.5 |
| Code | https://github.com/X-Square-Robot/wall-x |
| Paper | https://arxiv.org/abs/2509.11766 |
| Sandbox | [`../demo_sandboxes/wall_oss`](../demo_sandboxes/wall_oss/README.md) |

Qwen2.5-VL-3B + MoT ~4B. Official scripts (`scripts/fake_inference.py`, `generate_flow_action`) are **action-first**. The sandbox must also try text / CoT on the **same** `wall-oss-flow` weights. If the official railroad is mute, log that. Do not swap in a chat Qwen.

### 4. ECoT-OpenVLA

Oldest honest “English then act” open VLA. Fixed chain: TASK / PLAN / SUBTASK / MOVE, then action tokens.

| What | URL |
|---|---|
| Weights | https://huggingface.co/Embodied-CoT/ecot-openvla-7b-bridge |
| Code / Colab | https://github.com/MichalZawalski/embodied-CoT |
| Paper | https://arxiv.org/abs/2407.08693 |
| Sandbox | [`../demo_sandboxes/ecot_openvla`](../demo_sandboxes/ecot_openvla/README.md) |

Llama-2-7B (`below_reject` on the shopping rubric). Official prompt ends `ASSISTANT: TASK:`. `predict_action(..., unnorm_key="bridge_orig")` returns `(action, generated_ids)`. Decode the ids. Frame: their `test_obs.png`.

Ask on the box: do TASK / PLAN / SUBTASK come out as real English, or did this dump collapse to action tokens too?

## Then: small sandboxes (one at a time)

Success is “readable English intermediate goal **and** an action from the same weights.” Not a new scorecard.

| Order | Sandbox | Disk (rough) | Success |
|---|---|---|---|
| 1 | [`eo1`](../demo_sandboxes/eo1/README.md) | ~8 GB | `processor.generate` text is English (not empty / not tokens) **and** an action array. |
| 2 | [`chatvla`](../demo_sandboxes/chatvla/README.md) | ~6 GB | Official `evaluate` `outputs` contain English **or** log that v1 is mute-while-acting. |
| 3 | [`wall_oss`](../demo_sandboxes/wall_oss/README.md) | ~8 GB | CoT / subtask English on `wall-oss-flow`, not only `predict_action`. |
| 4 | [`ecot_openvla`](../demo_sandboxes/ecot_openvla/README.md) | ~14 GB | TASK/PLAN/SUBTASK English + Bridge action. |

**1× RTX 5090** for each. Do **not** install Habitat, Isaac, or an SO-101. Do **not** run `setup.sh` on the notes machine.

OneTwoVLA is the paper you wanted (reason ↔ act in one net). **No policy weights.** Do not build a fifth sandbox for it.

Gemma 4 12B + STEVE-1 remains Path K if this crop is also mute. That is not this window.
