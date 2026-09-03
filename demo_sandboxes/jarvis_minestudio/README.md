# JARVIS-VLA — MineStudio play loop

**Run only on a rented 5090 box. Do not execute `setup.sh` on the notes machine.**

Official play path from [CraftJarvis/JarvisVLA](https://github.com/CraftJarvis/JarvisVLA): JDK 8, MineStudio, `vllm serve`, then `VLLM_AGENT.forward`. This is the risky install (display + Java). Talk here is **only** whatever their action prompt returns — not a second chat template. Mouth smoke is [`../jarvis_vqa`](../jarvis_vqa/README.md).

- Box: 1× RTX 5090, CUDA 12.8.
- Disk: ~16 GB weights (same card as VQA) plus MineStudio assets.
- Headless: Xvfb first; else `MINESTUDIO_GPU_RENDER=1` + VirtualGL.

## Official sources

- Code: https://github.com/CraftJarvis/JarvisVLA
- Env: https://github.com/CraftJarvis/MineStudio
- Weights: `CraftJarvis/JarvisVLA-Qwen2-VL-7B`
- Agent: `jarvisvla.evaluate.agent_wrapper.VLLM_AGENT`
- Serve: `vllm serve ... --port 8000`
- Sampling they recommend if it sticks: temperature 0.7, top_p 0.99, top_k -1, history_num 2–4

**vLLM is the torch anchor in this folder.** Installing torch first just gets replaced. If no vLLM wheel works, setup writes `.rung` with `vllm=degraded-hf-generate` and the notebook uses a one-step HF path.

## On the box

```bash
cd demo_sandboxes/jarvis_minestudio
bash setup.sh
# in another terminal, after setup:
source .venv/bin/activate
bash serve.sh          # skip if .rung says degraded
# Jupyter kernel: jarvis-minestudio
```

Open `demo.ipynb`. Type a Minecraft instruction (`kill a sheep`, `mine a tree`). The notebook shows the live (or last) frame and the decoded buttons/camera tokens.

Smoke the simulator first if the notebook env cell fails:

```bash
# Xvfb path
python -m minestudio.simulator.entry
# or GPU render
MINESTUDIO_GPU_RENDER=1 python -m minestudio.simulator.entry
```
