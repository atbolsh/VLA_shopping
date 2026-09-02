# Test plan (for the later pull day)

Do not download everything. Three smokes, then one deep install.

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

## Smoke 1 — hosted / local demo, no training

1. Open [InternNav-Eval-Demo](https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo) and [InternVLA-N1 homepage](https://internrobotics.github.io/internvla-n1.github.io/).
2. Watch [FiS](https://fast-in-slow.github.io/), [OpenHelix](https://openhelix-robot.github.io/), [NaVILA](https://navila-bot.github.io/), [OneTwoVLA](https://one-two-vla.github.io/), [Helix](https://www.figure.ai/news/helix), [DreamGen](https://research.nvidia.com/labs/gear/dreamgen/).
3. Optional browser toy (not a candidate, architecture only): [Gemini ER + MuJoCo WASM](https://avikde.github.io/vla-pipeline/).

## Smoke 2 — one installable env each path

| Path | Install | Success looks like |
|---|---|---|
| N | InternNav Habitat eval **or** the HF space | Agent follows a language instruction in a house for >30 s without a human clicking actions. |
| K | CALVIN eval of OpenHelix *or* a dummy S1 that repeats `[CLOCK]` until a guard | S2 called once per maneuver, not per tick. |
| R | `lerobot-eval` on `lerobot/pi05_libero` **or** MolmoAct2-Think-LIBERO | Cube/object task completes. Then, and only then, plug an SO-101. |

## Deep dives (pick one)

- **N deep:** InternVLA-N1 DualVLN on a held-out Habitat scene; measure S2 Hz vs S1 Hz; see whether S2 stays silent while S1 walks.
- **K deep:** Freeze Gemma 4 12B, train only an `<ACT>` projector + a 3-class or 3DDA head on collapsed gold-game macros (sibling Options 1+2+5).
- **R deep:** 10 daytime SO-101 pick-and-place demos → Cosmos-Predict2.5 dreams overnight → GR00T or MolmoAct2 morning finetune. This is the self-teaching thesis.

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
