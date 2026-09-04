# Goal (closed): leftover English from the Chameleon VLA

**Closed 2026-09-04. Do not pick this up next.** RynnVLA-002 / WorldVLA is **not a usable option**. Token map below is kept so you do not re-derive it.

Look #2 on [`09_next_session.md`](09_next_session.md). Official loops emit action tokens and/or next-frame tokens. The question was whether the **same VLA checkpoint** still has a leftover BPE mouth if you refuse to let it speak image or action ids.

## What was proved

Same **VLA** weights, two queries (ran 2026-09-04 in `demo_sandboxes/rynn_worldvla`):

1. **Talk.** Ban image + reserved/action ids. BPE (`>= 16384`) leftover was **garbage** (SFT ate the mouth).
2. **Dream.** Trained world-model prompt (action + frames → next frames). Generation was messy; decode was not usable. A dead mouth did **not** leave a keeper decoder.

A caption from Meta Chameleon or `RynnVLA-001-7B-Base` does **not** count. Those already talk; they are not the policy.

## Token map (measured on WorldVLA `text_tokenizer.json`)

| Ids | What |
|---|---|
| 0–3 | `<s>` `<pad>` `</s>` `<unk>` |
| 4–8195 | `IMGIMG*` VQ codebook (8192) |
| 8196–16383 | reserved / sentinels — WorldVLA parks the 256 action bins here |
| 16384–65535 | BPE text (the mouth) |

Official VLA prompts ask for `<|action|>` / `<|image|>`. Talk means: allow only BPE + `</s>` / `<s>`.

WorldVLA cards are Lumina/xllmx, not a vanilla HF causal LM. The `rynn_worldvla` sandbox was **deleted** with the rest of the first crop. Official dream script (upstream only): `rynnvla-002/exps_libero_world_model/eval_world_model_goal.sh`.

## Verdict (2026-09-04)

Logged in [`10_sibling_list.md`](10_sibling_list.md#rynn-worldvla-2026-09-04) and sandbox C in [`09_next_session.md`](09_next_session.md).

| leftover_english | Meaning | This run |
|---|---|---|
| `usable` | ≥3 distinct real English words, no short cycle | — |
| `garbage` | Tokens decoded, not a sentence | **this** — prompt echo (` Use only commonality`) then `speaking`×∞ |
| `empty` | Mouth is gone | — |
| `unverified` | Never loaded — not a miss yet | — |

Dream/decoder: not usable. Official `decode_image` needs a perfect 1060-token 512² span; generations were junk short `8197…8196` pairs, 1028 (no newlines), 1059 (`KeyError 8803`), or `max_new_tokens` fragments. Recoveries did not yield a usable next-frame look. Owner declined more harness work.

**Do not** treat a caption from Meta Chameleon or `RynnVLA-001-7B-Base` as this policy talking. Crop closed. Next window is EO-1 / ChatVLA / WALL-OSS / ECoT — not InternVLA-N1.
