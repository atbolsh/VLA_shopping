# MolmoAct2-Think + Molmo2-ER

**Run only on a rented 5090 box. Do not execute `setup.sh` on the notes machine.**

Two **official** surfaces, not one blended chat:

1. **Act / think** — [`allenai/MolmoAct2-Think-LIBERO`](https://huggingface.co/allenai/MolmoAct2-Think-LIBERO) `predict_action(..., enable_depth_reasoning=True, enable_adaptive_depth=True, depth_cache=...)`. Prompt style is theirs (`The task is to … first predict the depth map …`). Reply pane: 10×10 depth grid + which cells refreshed + continuous action.
2. **Ask** — [`allenai/Molmo2-ER`](https://huggingface.co/allenai/Molmo2-ER) with the Molmo2 `apply_chat_template` from [allenai/molmo2](https://github.com/allenai/molmo2). Same observation image, **separate** model load.

Do not stuff Gemma-style system prompts into `predict_action`.

- Box: 1× RTX 5090. Official 5090 pin: **torch 2.11.0 + torchvision 0.26.0 cu128**, `transformers` 4.57.x, Python 3.11–3.12.
- Disk: ~20 GB Think-LIBERO + ~16 GB Molmo2-ER.

Optional closed loop is a **separate** `.venv-lerobot` (`lerobot==0.5.1` fights transformers 4.57). Python ≥3.12 only:

```bash
bash setup.sh --with-lerobot
```

## On the box

```bash
cd demo_sandboxes/molmoact2
bash setup.sh
# kernel: molmoact2
```

`setup.sh` clones with `GIT_LFS_SKIP_SMUDGE=1`. A few LeRobot test PNGs in that repo 404 on LFS; we do not need them. If a previous clone left `vendor/molmoact2` half-checked-out, just re-run `setup.sh`.

Open `demo.ipynb`. Frames come from the Think-LIBERO card (`screenshot/sample_*_rgb.png`), not the orange/blue placeholders.

If `setup.sh` already finished:

```bash
source .venv/bin/activate
python download_frames.py
```

Then **restart the `molmoact2` kernel** so it picks up `src/think_act.py` (processor list→dict shim + `AutoModelForImageTextToText`).
