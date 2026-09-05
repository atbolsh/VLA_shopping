# EO-1 — interleaved text + action

**Run only on a rented RTX 5090 or RTX 5000 box. Do not execute `setup.sh` on the notes machine.**

Same 3B must print English **and** an action. Official HF path: `processor.generate(model, batch)` → `output.text` + `output.action`. Do **not** load a second VLM.

- Box: 1× RTX 5090 or RTX 5000.
- Weights: [`IPEC-COMMUNITY/EO-1-3B`](https://huggingface.co/IPEC-COMMUNITY/EO-1-3B) (~4B listed, ~6.5 GB).
- Code: https://github.com/EO-Robotics/EO1
- Paper: https://arxiv.org/abs/2508.21112
- Frames: official `demo_data/example1.jpg` + `example2.png` — **on-distribution** for their reasoning demo (not LIBERO).
- Not interruptible: one decoder, interleaved text + flow, no async S1.
- Planner size is **3B** (below the 12B bar). This window tests the mouth-while-acting claim, not Path N.

```bash
cd demo_sandboxes/eo1
bash setup.sh
# kernel: eo1
```

Open `demo.ipynb`. Raw text first, then the action array.
