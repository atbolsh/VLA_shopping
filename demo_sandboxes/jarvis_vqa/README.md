# JARVIS-VLA — leftover Qwen mouth

**Run only on a rented 5090 box. Do not execute `setup.sh` on the notes machine.**

Sibling first smoke from [`notes/09_next_session.md`](../../notes/09_next_session.md): does a Minecraft screenshot still get an English answer after action SFT?

- Box: 1× RTX 5090, CUDA 12.8 template.
- Disk: ~16 GB for `CraftJarvis/JarvisVLA-Qwen2-VL-7B`.
- No MineStudio, no JDK, no vLLM. That is [`../jarvis_minestudio`](../jarvis_minestudio/README.md).

## Official sources

- Weights: https://huggingface.co/CraftJarvis/JarvisVLA-Qwen2-VL-7B
- Frames: https://huggingface.co/datasets/CraftJarvis/minecraft-vla-sft (`valid` only; `download_screenshots.py`)
- Chat path: Qwen2-VL `apply_chat_template` + `qwen_vl_utils.process_vision_info` on **these** weights (Qwen’s snippet, not a Gemma wrapper).
- Pins recorded in [`requirements.txt`](requirements.txt). Torch/transformers rungs live in [`setup.sh`](setup.sh).

## On the box

```bash
# repo-root .env already has export HF_TOKEN=...
cd demo_sandboxes/jarvis_vqa
bash setup.sh
# Jupyter: pick kernel "jarvis-vqa"
```

If `setup.sh` already finished, pull frames now (official `minecraft-vla-sft` **valid** split only):

```bash
source .venv/bin/activate
python download_screenshots.py
```

Open `demo.ipynb`. Pick a frame from the **screenshot** dropdown. Ask “what are you looking at?”

Success: leftover English **or** a logged “SFT ate the mouth” (`empty` / `garbage`). Write the verdict back to [`notes/10_sibling_list.md`](../../notes/10_sibling_list.md) after you have run it.

Rung written to `.rung` (gitignored) so you know which torch/transformers pair landed.
