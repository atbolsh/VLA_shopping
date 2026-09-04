# RynnVLA-002 / WorldVLA — act, dream, leftover BPE

**Run only on a rented 5090 box. Do not execute `setup.sh` on the notes machine.**

Official loops emit action tokens and/or next-frame tokens, **not** chat. This folder stays in Lumina/xllmx. Do not load these weights as a vanilla HF causal LM. A caption from Meta Chameleon or `RynnVLA-001-7B-Base` does **not** count.

- Box: 1× RTX 5090, CUDA 12.8.
- Disk: ~16–25 GB (one LIBERO-goal VLA ckpt + one world-model ckpt + Chameleon tokenizer).
- Frozen stack: keep `transformers==4.43.0`. Torch starts at **2.7.0+cu128** (oldest sm_120 near their 2.2), then 2.8.0. Do not jump to Molmo’s 2.11 here.

## Two stages

```bash
bash setup.sh              # base: xllmx + weights; dream + talk on sample frames
bash setup.sh --with-libero  # optional: mujoco / robosuite / LIBERO closed loop
```

Do **not** `pip install -r` the official WorldVLA `requirements.txt` (it pulls cu121 `nvidia-*`).

## Official sources

- Code: https://github.com/alibaba-damo-academy/WorldVLA
- Weights: https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-002
- Tokenizer: WorldVLA `chameleon/tokenizer` (`text_tokenizer.json`)
- Act scripts: `rynnvla-002/evals_libero/`
- Dream script: `rynnvla-002/exps_libero_world_model/eval_world_model_goal.sh`
- Talk spec: [`notes/11_chameleon_talk_harness.md`](../../notes/11_chameleon_talk_harness.md)

Token map (WorldVLA `text_tokenizer.json`):

| Ids | What |
|---|---|
| 0–3 | `<s>` `<pad>` `</s>` `<unk>` |
| 4–8195 | `IMGIMG*` VQ codebook |
| 8196–16383 | reserved / 256 action bins |
| 16384–65535 | BPE mouth |

Talk bans 4–16383. Verdict: `usable` / `garbage` / `empty`.

## On the box

```bash
cd demo_sandboxes/rynn_worldvla
bash setup.sh
# kernel: rynn-worldvla
```

Open `demo.ipynb`. Three turns on the same VLA weights: **Act**, **Dream**, **Talk**.

Frames come from `screenshot/` (first frame of the official WorldVLA LIBERO GIFs), not the orange/blue placeholders. If that folder is empty after an older setup:

```bash
source .venv/bin/activate
python download_frames.py
```

The Chameleon tokenizer is `text_tokenizer.json` loaded with `LlamaTokenizerFast(tokenizer_file=...)` — it is **not** an HF `from_pretrained` folder.
