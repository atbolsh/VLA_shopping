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

After the demo, `dream_ablations.ipynb` is the five-rung ladder (recon floor, action counterfactuals, rollout ×3, unified-card dream, one fair on-railroad mouth shot). Decoder-first: the mouth is already logged `garbage`; rung 5 is the only mouth rung and the last one.

Frames come from `screenshot/` (first frame of the official WorldVLA LIBERO GIFs), not the orange/blue placeholders. If that folder is empty after an older setup:

```bash
source .venv/bin/activate
python download_frames.py
```

## Official load (do not skip)

`VLA_model_256/libero_goal` `config.json` is `ChameleonXLLMXForConditionalGeneration_ck_action_head`, not the base xllmx class. Official discrete eval (`evals_libero/eval_libero_goal_his_2_third_view_wrist_w_state_5_256_abiw_discrete.sh`) does:

```python
from model import ChameleonXLLMXForConditionalGeneration_ck_action_head
model = ChameleonXLLMXForConditionalGeneration_ck_action_head.from_pretrained(
    ckpt, torch_dtype=torch.bfloat16, mask_image_logits=False,
    action_dim=7, time_horizon=5, device_map="cpu",
)
# then ItemProcessor(target_size=256) + model.generate_dis_ma
```

WorldVLA `requirements.txt` pins **transformers==4.43.0** (same as `setup.sh`). The published VLA `config.json` lists `transformers_version: 4.48.0`; that is the saver, not the pin. Keep 4.43.0.

Load is **not** `from_pretrained`. The harness reads every safetensors key, merges Meta `vqgan.ckpt` onto `model.vqmodel.*` (encoder/quantizer only; HF has no decoder; `custom_layer.*` extras are dropped, same as official convert), `load_state_dict(..., assign=True)`, then compares each live tensor to the file. A skipped shard key or a still-random Parameter is a hard error. Wait for `load verified … tensors N`.

Saved names match the module names exactly — verified 593/593 Parameters elementwise on 2026-09-04. No re-save or key translator is needed. The two historical gaps were: wrong class (base xllmx instead of `_ck_action_head`) and `model.vqmodel.*` absent from the shards (filled from `vqgan.ckpt`).

**Dream prompt:** the 002 world-model cards were trained on `Generate the next image based on the provided sequence of historical images and corresponding actions.<|image|><|image|><|action|>` (`data/dataset.py`, `world_model_bi_views_conv_generation.py`). The vendor helper `get_action_Chameleon_dis_awm_g_video_wrist` carries the older WorldVLA-era prompt and produced malformed image blocks on this card; the harness builds the trained conversation itself.

The Chameleon tokenizer is `text_tokenizer.json`. Talk still loads it with `LlamaTokenizerFast(tokenizer_file=...)`. Act/dream use the official Lumina-mGPT-7B-768 tokenizer files (setup downloads those jsons only) plus `vqgan.yaml` / `vqgan.ckpt`.
