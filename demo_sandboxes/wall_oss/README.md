# WALL-OSS — Uni-CoT claim, `wall-oss-flow` weights

**Run only on a rented RTX 5090 or RTX 5000 box. Do not execute `setup.sh` on the notes machine.**

Paper (arXiv:2509.11766) says one net does instruction → CoT / subtask → continuous action. Official `scripts/fake_inference.py` and `generate_flow_action` are **action-first**. This notebook runs the official action path **and** a text generate on the **same** `wall-oss-flow` weights. Do not swap in a chat Qwen.

- Box: 1× RTX 5090 or RTX 5000.
- Weights: [`x-square-robot/wall-oss-flow`](https://huggingface.co/x-square-robot/wall-oss-flow)
- Newer deploy ckpt (not default): [`wall-oss-0.5`](https://huggingface.co/x-square-robot/wall-oss-0.5)
- Code: https://github.com/X-Square-Robot/wall-x
- Planner: Qwen2.5-VL-**3B** + MoT (below the 12B bar).
- Frames: EO-1 stills as face/wrist — **not** on-distribution. Official `fake_inference` is random tensors; LIBERO is later.
- Not interruptible: Uni-CoT can skip/interleave text in one net, not a separate S1.

`pip install -e vendor/wall-x` builds CUDA ops. If that fails, the harness still tries `sys.path` import.

```bash
cd demo_sandboxes/wall_oss
bash setup.sh
# kernel: wall-oss
```
