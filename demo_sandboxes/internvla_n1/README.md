# InternVLA-N1 — official inference-only notebook

**Run only on a rented 2×5090 box. Do not execute `setup.sh` on the notes machine.**

The hosted Gradio ([InternRobotics/InternNav-Eval-Demo](https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo)) is **down** as of 2026-09-03 (401; thin UI over a remote backend). Do not use `pc4work/InternNav-Eval-Demo`. This folder wraps InternNav’s own [`scripts/notebooks/inference_only_demo.ipynb`](https://github.com/InternRobotics/InternNav/blob/main/scripts/notebooks/inference_only_demo.ipynb): `InternVLAN1AsyncAgent.step(rgb, depth, pose, instruction, intrinsic=...)`. No Habitat / Isaac in v1.

- Box: **2× RTX 5090**, CUDA 12.8.
- GPU split (hardcoded): DualVLN agent on `cuda:0`, System-2 Qwen chat on `cuda:1`.
- Disk: ~16 GB DualVLN + ~16 GB System2 + DepthAnything-Small + their sample tarball.
- Frozen library pins: `transformers==4.51.0`, `diffusers==0.31.0`, `accelerate==1.10.1`. Torch starts at **2.7.0+cu128** (nearest sm_120 to their 2.6+cu124), then 2.8.0. Do not use Molmo’s 2.11 / 4.57 here. Do **not** install Python 3.9 or their `flash_attn ... cp39 ... torch2.6` wheel.

## Official sources

- Code: https://github.com/InternRobotics/InternNav
- DualVLN: https://huggingface.co/InternRobotics/InternVLA-N1-DualVLN
- System 2: https://huggingface.co/InternRobotics/InternVLA-N1-System2
- DepthAnything (their notebook): https://huggingface.co/depth-anything/Depth-Anything-V2-Metric-Hypersim-Small
- Sample RGB stream: `assets/realworld_sample_data.tar.gz` inside the InternNav clone

## On the box

```bash
cd demo_sandboxes/internvla_n1
bash setup.sh
# kernel: internvla-n1
```

Open `demo.ipynb`. Type an English house instruction; step the official agent on their sample frames.

- **Walk loop** (`DualVlnPlay.step`): mute toward you. Reply pane is S2 `llm_output` (mid-level English) + a pixel-goal, only every `plan_step_gap`. It will not ask a clarifier.
- **Ask** (`System2Ask` on `cuda:1`): Qwen2.5-VL chat on the System-2 card. Same *kind* of leftover mouth as Molmo2-ER, not the navigator.

Habitat `scripts/eval/eval.py` stays a later job.
