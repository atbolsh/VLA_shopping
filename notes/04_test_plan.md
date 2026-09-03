# Test plan

**Next window starts at [`09_next_session.md`](09_next_session.md).** Look first (JARVIS-VLA → Chameleon/Rynn/WorldVLA → MolmoAct2 → InternVLA-N1), then one small sandbox at a time. Do not download the twelve-card zoo.

The rest of this file is the later pull-day smokes, after those looks.

## Look order (next session)

1. **JARVIS-VLA** — **done 2026-09-03.** Mouth dead (`action_tokens`). Skip MineStudio. [`10_sibling_list.md`](10_sibling_list.md#pull-log).
2. **RynnVLA-001 / 002 + WorldVLA** — videos, HF GIFs, GitHub. Vision decoder / next-frame path. Then hack a harness for leftover English.
3. **MolmoAct2** — **done 2026-09-03.** Ask talks; Think-LIBERO inject failed. [`10_sibling_list.md`](10_sibling_list.md#pull-log).
4. **InternVLA-N1** — next: 2×5090 sandbox (`internvla_n1`). Gradio still 401. Expect mute `step` + readable S2 `llm_output`; chat is `system2_ask`.

Links live in [`09_next_session.md`](09_next_session.md) and [`05_demos.md`](05_demos.md).

## Sandboxes (after the looks)

| Order | Install | Success looks like |
|---|---|---|
| S | JARVIS-VLA screenshot VQA (`jarvis_vqa`). MineStudio skipped. | **Done 2026-09-03:** `action_tokens` only. |
| A | InternNav Gradio (already in look 4) | Agent follows a language instruction in a house for >30 s without a human clicking actions. |
| B | MolmoAct2 Think-LIBERO + Molmo2-ER Ask | **Done 2026-09-03:** Ask English; Think action chunk; inject did not gate. |
| C | WorldVLA or RynnVLA-002 LIBERO from their GitHub | One LIBERO suite, one action-conditioned next-frame sample, one leftover-English harness attempt. |

Habitat / Isaac / SO-101 wait until A/B/C have a winner.

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
