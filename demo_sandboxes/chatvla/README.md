# ChatVLA-1 — official evaluate on the robot weights

**Run only on a rented 5090 box. Do not execute `setup.sh` on the notes machine.**

ChatVLA-**2** has no public robot checkpoint. This folder is ChatVLA-1 (`zzymeow/ChatVLA`) only.

Official robot loop: vendor `evaluate/evaluate_robot.py` → `policy.evaluate(**batch)`. `eval_in_vqa` is a flag on **these** weights, not a second card. Do not load stock Qwen as a substitute mouth.

- Box: 1× RTX 5090.
- Weights: https://huggingface.co/zzymeow/ChatVLA
- Code: https://github.com/midea-ai/ChatVLA_public
- Backbone: Qwen2-VL-**2B** (below the 12B bar).
- Cameras: official script wants top + two wrists. We reuse one EO-1 still three times and say so — **not** on-distribution (no public ALOHA env / observation PNG).
- Not interruptible: re-query every *N* steps. No surprise trigger.

```bash
cd demo_sandboxes/chatvla
bash setup.sh
# kernel: chatvla
```
