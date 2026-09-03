# Goal (note only): leftover English from the Chameleon VLA

**Not a Cursor official goal.** Parked here so the next window can pick it up. Do not start code in the window that only wrote this. Do not download weights from here.

This is look #2 on [`09_next_session.md`](09_next_session.md). You like the vision decoder. Official WorldVLA / RynnVLA loops emit action tokens and/or next-frame tokens. The question is whether the **same VLA checkpoint** still has a leftover BPE mouth if you refuse to let it speak image or action ids.

A draft Python harness was started and **deleted**. Write code later, not now.

## What you are proving (later)

Same **VLA** weights, two queries:

1. **Talk.** Ban image + reserved/action ids. Whatever comes out of BPE (`>= 16384`) is leftover Chameleon English, or SFT ate it.
2. **Dream.** Official world-model prompt (action + frame → next frame). That is why this family is in the four-look list. A dead mouth does not demote the decoder.

A caption from Meta Chameleon or `RynnVLA-001-7B-Base` does **not** count. Those already talk; they are not the policy.

## Token map (measured on WorldVLA `text_tokenizer.json`)

| Ids | What |
|---|---|
| 0–3 | `<s>` `<pad>` `</s>` `<unk>` |
| 4–8195 | `IMGIMG*` VQ codebook (8192) |
| 8196–16383 | reserved / sentinels — WorldVLA parks the 256 action bins here |
| 16384–65535 | BPE text (the mouth) |

Official VLA prompts ask for `<|action|>` / `<|image|>`. Talk means: allow only BPE + `</s>` / `<s>`.

WorldVLA cards are Lumina/xllmx, not a vanilla HF causal LM. When you do write a harness, clone [WorldVLA](https://github.com/alibaba-damo-academy/WorldVLA) and stay in that env. Dream PNG: `rynnvla-002/exps_libero_world_model/eval_world_model_goal.sh` on the **same** ckpt.

## Verdict (when you actually run it)

Write it back into [`10_sibling_list.md`](10_sibling_list.md) and sandbox C in [`09_next_session.md`](09_next_session.md).

| leftover_english | Meaning |
|---|---|
| `usable` | ≥3 real English words after stripping `IMGIMG*` / angle-bracket specials |
| `garbage` | Tokens decoded, not a sentence |
| `empty` | Mouth is gone |
| `unverified` | Never loaded — not a miss yet |
