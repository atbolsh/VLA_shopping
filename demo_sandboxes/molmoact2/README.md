# MolmoAct2-Think + Molmo2-ER

**Run only on a rented 5090 box. Do not execute `setup.sh` on the notes machine.**

Two **official** surfaces, not one blended chat:

1. **Act / think** — [`allenai/MolmoAct2-Think-LIBERO`](https://huggingface.co/allenai/MolmoAct2-Think-LIBERO) `predict_action(..., enable_depth_reasoning=True, enable_adaptive_depth=True, depth_cache=...)`. Prompt style is theirs (`The task is to … first predict the depth map …`). Reply pane: 10×10 depth grid + which cells refreshed + continuous action.
2. **Ask** — [`allenai/Molmo2-ER`](https://huggingface.co/allenai/Molmo2-ER) with the Molmo2 `apply_chat_template` from [allenai/molmo2](https://github.com/allenai/molmo2). Same observation image, **separate** model load.

Do not stuff Gemma-style system prompts into `predict_action`.

**Tried 2026-09-03:** Molmo2-ER Ask answered English. Think-LIBERO `predict_action` returned depth + a 10-step action chunk. Caution-sentence inject (`think_inject.ipynb`) did not get follow-ups or a still arm. Do not re-run inject expecting a mouth. Log: [`notes/10_sibling_list.md`](../../notes/10_sibling_list.md#pull-log).

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

Frames come from the Think-LIBERO card (`screenshot/sample_agentview_rgb.png`, `sample_wrist_rgb.png`), not the orange/blue placeholders.

- **`think_inject.ipynb`** — caution sentence in the official `task=` slot; full `generated_token_ids` decode; `█` over depth/action payload tokens; then depth bins + action vectors. One model (Think-LIBERO). Now also **five drift probes**, none through `predict_action`: 1–3 rebuild the vendor's exact robot prompt with the forced `<depth_output><action_output>` trigger stripped (free continuation; `[START ACTION]` sentinel contract where the harness re-attaches the trigger after the model talks); 4–5 are plain chat `generate` on the Think weights (image, then text-only "hello there"). Each probe prints the **raw decode first**, with space between the before-sentinel and after-sentinel panes; formatted boxed/residue after. Vendor source is cloned to `vendor/molmoact2` (gitignored) as the reference template — the probes call `_build_robot_text` from the model's own runtime module, so prompt shape is never guessed.
- **`demo.ipynb`** — older two-surface notebook (Think + Molmo2-ER). Do not load both on one 5090.

If `setup.sh` already finished:

```bash
source .venv/bin/activate
python download_frames.py
```

Then **restart the `molmoact2` kernel** and open `think_inject.ipynb`.
