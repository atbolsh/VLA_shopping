# ECoT-OpenVLA — TASK / PLAN / SUBTASK / MOVE then action

**Run only on a rented 5090 box. Do not execute `setup.sh` on the notes machine.**

Official Colab path: `predict_action(..., unnorm_key="bridge_orig")` returns `(action, generated_ids)`. Decode the ids. Prompt ends `ASSISTANT: TASK:`. Llama-2-7B (`below_reject` on the shopping rubric). This window tests whether the English chain is still there.

- Box: 1× RTX 5090.
- Weights: [`Embodied-CoT/ecot-openvla-7b-bridge`](https://huggingface.co/Embodied-CoT/ecot-openvla-7b-bridge) (~16 GB).
- Code: https://github.com/MichalZawalski/embodied-CoT
- Paper: https://arxiv.org/abs/2407.08693
- Frame: official `test_obs.png` — **on-distribution** Bridge (`unnorm_key="bridge_orig"`).
- Not interruptible: full TASK/PLAN/SUBTASK/MOVE, then one action.

```bash
cd demo_sandboxes/ecot_openvla
bash setup.sh
# kernel: ecot-openvla
```
