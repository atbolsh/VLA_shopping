# Test plan

**Build-out is EO-1 + LIBERO** ([`09_next_session.md`](09_next_session.md), repo `README.md`). The 2026-09-03/04 crop is **rejected**. InternVLA-N1 is **never** the next box. Do not start ChatVLA / WALL-OSS / ECoT / Bridge VM.

The rest of this file is later pull-day smokes, after a sandbox you still like.

## Closed crop (do not rerun)

1. **JARVIS-VLA** — **rejected 2026-09-03.** Mouth dead (`action_tokens`). [`10_sibling_list.md`](10_sibling_list.md#pull-log).
2. **RynnVLA-001 / 002 + WorldVLA** — **rejected 2026-09-04.** Mouth garbage; dream not usable.
3. **MolmoAct2-Think** — **rejected 2026-09-03.** Think is a mute policy. Molmo2-ER is a different net.
4. **InternVLA-N1 DualVLN** — **rejected 2026-09-04.** S2 `llm_output` was `→→→→`. Do not reopen.

## Sandboxes (this window)

| Order | Install | Success looks like |
|---|---|---|
| 1 | EO-1 (`demo_sandboxes/eo1`) | Same 3B: English text **and** an action. |
| 2 | ChatVLA-1 (`demo_sandboxes/chatvla`) | Official `evaluate` prints English in `outputs`, or log mute. |
| 3 | WALL-OSS (`demo_sandboxes/wall_oss`) | CoT / subtask English on `wall-oss-flow`, not only flow actions. |
| 4 | ECoT-OpenVLA (`demo_sandboxes/ecot_openvla`) | TASK/PLAN/SUBTASK English + Bridge action. |

Habitat / Isaac / SO-101 wait. Disembodied planners are out.

## Smoke 0 — reasoning only (no robot)

Same prompts you already use on Gemma 4 12B / e4B: multi-step plans, "what do you do if the gold disappears," a short Python sketch, a spatial "turn until X" description.

| Checkpoint | Expect |
|---|---|
| InternVLA-N1 System 2 (Qwen2.5-VL-7B ft) | Near 12B. If it fails this, Path N is only a controller. |
| Molmo2-ER / MolmoAct2 text+image | Strong spatial, maybe weaker coding. |
| Cosmos-Reason2-2B | e4B-class risk. If it fails, GR00T is a body without a brain. |
| OpenHelix's LLaVA-7B | Should fail the bar. Confirms Path K. |
| Magma-8B | Middle. Useful if you want one net that also clicks UIs. |

Log the verdicts back into each card's `reasoning_vs_gemma4_12b` field.

## Older path installs (after a sandbox you still like)

| Path | Install | Success looks like |
|---|---|---|
| N | InternNav Habitat eval **or** the HF space | Same as sandbox A, but local. |
| K | CALVIN eval of OpenHelix *or* a dummy S1 that repeats `[CLOCK]` until a guard | S2 called once per maneuver, not per tick. |
| R | `lerobot-eval` on `lerobot/pi05_libero` **or** MolmoAct2-Think-LIBERO | Same as sandbox B. Then, and only then, plug an SO-101. |

## Deep dives (pick one)

- **N deep:** InternVLA-N1 DualVLN on a held-out Habitat scene; measure S2 Hz vs S1 Hz; see whether S2 stays silent while S1 walks.
- **K deep:** Freeze Gemma 4 12B, train only an `<ACT>` projector + a 3-class or 3DDA head on collapsed gold-game macros (sibling Options 1+2+5).
- **R deep:** 10 daytime SO-101 pick-and-place demos → Cosmos-Predict2.5 / RynnVLA-style dreams overnight → GR00T or MolmoAct2 morning finetune. This is the self-teaching thesis.

## Record in the card after each pull

```text
pulled: YYYY-MM-DD
gpu:
vram_gb:
reasoning_smoke: above | near | below_ok | below_reject
env_smoke: pass | fail | not_tried
notes:
```

Append that block under `## Pull log` at the bottom of the card. Do not invent a second tracking file.
