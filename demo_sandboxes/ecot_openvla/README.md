# ECoT-OpenVLA — TASK / PLAN / SUBTASK / MOVE then action

**Run only on a rented RTX 5090 or RTX 5000 box. Do not execute `setup.sh` on the notes machine.**

Official Colab path: `predict_action(..., unnorm_key="bridge_orig")` returns `(action, generated_ids)`. Decode the ids. Prompt ends `ASSISTANT: TASK:`. Llama-2-7B (`below_reject` on the shopping rubric). This window tests whether the English chain is still there.

- Box: 1× RTX 5090 or RTX 5000.
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

If this venv already exists and the notebook raises `ImportError: ... timm`, do **not** re-run setup. In the ecot-openvla venv:

```bash
python -m pip install timm
```

Restart the **ecot-openvla** kernel.

- `demo.ipynb` — official still (`test_obs.png`) + `predict_action`.
- **`play.ipynb`** — interactive WidowX / SimplerEnv (Bridge). Same weights: English chain **and** a 7-DoF action, then the env steps. Needs `bash setup_simpler.sh` once.
