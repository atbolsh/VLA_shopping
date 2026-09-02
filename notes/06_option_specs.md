# Option specs (parseable)

Survey date: 2026-09-02. Every option uses the same four headings.

**Network** — exact checkpoints, with links.  
**Action** — do you have to **finetune just to get started** in some public env you can install? Installing software, requesting a gated HF card, or merging safetensors is **not** training. Adapting later to a *new* env (including your gold game, or a physical arm in your room) is a separate row.  
**World** — exact env and/or robot, links, price. Software is $0 unless noted.  
**Paper** — canonical paper + local PDF.

"$120 / arm" is explained first, then the twelve options in pull order.

---

## What "$120 / arm" meant

It is the **official bill-of-materials for one SO-101 follower arm**, if you 3D-print the plastic yourself and buy the servos/board/PSU. Not a finished robot in a box, and not a leader+follower teleop pair.

| What you buy | Official number | Source |
|---|---|---|
| One **follower** arm, DIY parts only (6× STS3215, board, PSU, clamps, screwdriver). You print the frame. | **$121.94 US** / **€124.30** | [SO-ARM100 BOM, "Parts for One Follower Arm"](https://github.com/TheRobotStudio/SO-ARM100) |
| Leader + follower pair, DIY parts (classic LeRobot teleop). You print both frames. | **$229.88 US** / **€226.30** | [same BOM, "Parts For Two Arms"](https://github.com/TheRobotStudio/SO-ARM100) |
| Vendor kit (printed parts / assembled / camera included) | ~$200–$740 depending on package | [WowRobo](https://shop.wowrobo.com/products/so-arm101-diy-kit-assembled-version-1), [Hiwonder](https://www.hiwonder.com/products/lerobot-so-101), [Seeed](https://www.seeedstudio.com/SO-ARM100-Low-Cost-AI-Arm-Kit.html), [vendor list](https://github.com/TheRobotStudio/SO-ARM100#kits) |

Assembly docs: [Hugging Face SO-101](https://huggingface.co/docs/lerobot/en/so101). Software: [LeRobot](https://github.com/huggingface/lerobot).

I used "$120 / arm" as shorthand for that **$121.94 follower BOM**. A usable teleop cell is closer to **$230 DIY** or **$200–$400+** as a kit. I should have written the BOM number.

---

## 1. InternVLA-N1

### Network

| Piece | What | Link |
|---|---|---|
| System 2 (slow) | Finetuned **Qwen2.5-VL-7B** (~8B on HF) for pixel-goal / VLN reasoning | [InternRobotics/InternVLA-N1-System2](https://huggingface.co/InternRobotics/InternVLA-N1-System2) |
| System 1 (fast), current | **DualVLN** — RGB nav controller, jointly trained, recommended | [InternRobotics/InternVLA-N1-DualVLN](https://huggingface.co/InternRobotics/InternVLA-N1-DualVLN) |
| System 1 (fast), alt | **NavDP\*** — RGB-D nav controller | [InternRobotics/InternVLA-N1-w-NavDP](https://huggingface.co/InternRobotics/InternVLA-N1-w-NavDP) |
| Code | InternNav (Habitat + Isaac) | [InternRobotics/InternNav](https://github.com/InternRobotics/InternNav) |

### Action

| | |
|---|---|
| **Finetune just to get started?** | **No.** DualVLN + System 2 are already trained. |
| **First env you can install** | [InternNav](https://github.com/InternRobotics/InternNav) on Habitat VLN-CE. Hosted taste: [Gradio](https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo). |
| **Later (new env / your game / an arm)** | Yes — nav action space, not `CLOCK`, not SO-101. |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env (start here) | InternNav on **Habitat** VLN-CE | [InternNav](https://github.com/InternRobotics/InternNav), [Habitat](https://aihabitat.org/), [VLN-CE](https://github.com/jacobkrantz/VLN-CE) | $0. GPU + disk for scene datasets. |
| Env (heavier) | Isaac Sim / InternUtopia | [Isaac Sim](https://developer.nvidia.com/isaac-sim) | $0 software; NVIDIA GPU required. |
| Data | InternData-N1 (~3k scenes, 830k VLN) | [InternRobotics/InternData-N1](https://huggingface.co/datasets/InternRobotics/InternData-N1) | $0 download. |
| Robot | None required. Real-world VLN exists in their stack; no cheap-arm finetune. | — | — |

### Paper

- Tech report (not arXiv): [InternVLA_N1.pdf](https://internrobotics.github.io/internvla-n1.github.io/static/pdfs/InternVLA_N1.pdf)
- Local: `papers/pdfs/internvla_n1_techreport.pdf`

---

## 2. Gemma 4 12B + stolen System 1 (kit)

### Network

| Piece | What | Link |
|---|---|---|
| System 2 (slow) | **Your** Gemma 4 12B (already being finetuned) | whatever checkpoint you already have |
| System 1 option A | OpenHelix **3D Diffuser Actor** + `<ACT>` projector | [OpenHelix/openhelix](https://huggingface.co/OpenHelix/openhelix), [code](https://github.com/OpenHelix-robot/OpenHelix) |
| System 1 option B | InternVLA-N1 **DualVLN** (nav only) | [InternVLA-N1-DualVLN](https://huggingface.co/InternRobotics/InternVLA-N1-DualVLN) |
| System 1 option C | A tiny policy you train (3-class CNN / flow head) for `CLOCK` / `ANTICLOCK` / `FORWARD` | not published — you write it |
| Recipe papers | OpenHelix + LCB (`<ACT>` token) | below |

### Action

| | |
|---|---|
| **Finetune just to get started?** | **Yes.** There is no released “Gemma 4 12B + S1” policy. This kit does not play in any env until you train the bridge. |
| **First env you can install** | None for *this* pairing. To watch a dual system without training, use option 7 (OpenHelix on CALVIN) or option 1 (InternVLA-N1 on Habitat). |
| **Later (new env / your game / an arm)** | That *is* the work: freeze Gemma, train `<ACT>` + projector (OpenHelix §1.5), or train a CLOCK head. |

This option does not exist until you train the bridge. That is the point.

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env | Your gold game, or CALVIN if you keep 3DDA, or Habitat if you keep DualVLN | [CALVIN](http://calvin.cs.uni-freiburg.de/), [InternNav](https://github.com/InternRobotics/InternNav) | $0 |
| Robot | Whatever S1 already speaks. No vendor Gemma-on-SO-101 ckpt. | [SO-101](https://huggingface.co/docs/lerobot/en/so101) if you later train a LeRobot head | $0 until you buy an arm |

### Paper

- OpenHelix: [arXiv:2505.03912](https://arxiv.org/abs/2505.03912) — local `papers/pdfs/2505.03912_openhelix.pdf`
- LCB (the `<ACT>` idea): [arXiv:2405.04798](https://arxiv.org/abs/2405.04798) — local `papers/pdfs/2405.04798_lcb.pdf`
- Sibling design: `../stateful_realtime_thinking/notes/02_design_options.md` (Option 5)

---

## 3. MolmoAct2 / MolmoAct2-Think

### Network

| Piece | What | Link |
|---|---|---|
| Whole VLA (base) | **Molmo2-ER** + flow-matching action expert. HF lists the SO-100/101 card at **5B**. | [allenai/MolmoAct2](https://huggingface.co/allenai/MolmoAct2) |
| Think variant | Same, plus adaptive 10×10 depth tokens (slow reason / skip unchanged cells) | [allenai/MolmoAct2-Think-LIBERO](https://huggingface.co/allenai/MolmoAct2-Think-LIBERO) |
| SO-10x finetune | Absolute joint-pose, community SO-100/101 data | [allenai/MolmoAct2-SO100_101](https://huggingface.co/allenai/MolmoAct2-SO100_101) |
| Other finetunes | DROID Franka; bimanual YAM | [MolmoAct2-DROID](https://huggingface.co/allenai/MolmoAct2-DROID), [MolmoAct2-BimanualYAM](https://huggingface.co/allenai/MolmoAct2-BimanualYAM) |
| Code | Training + servers | [allenai/molmoact2](https://github.com/allenai/molmoact2) |

There is not a separately downloadable "S1-only" net. The action expert is grafted onto the VLM via per-layer KV. Think mode is the slow/fast *in time*.

### Action

| | |
|---|---|
| **Finetune just to get started?** | **No.** [MolmoAct2-Think-LIBERO](https://huggingface.co/allenai/MolmoAct2-Think-LIBERO) is already trained. |
| **First env you can install** | [LIBERO](https://libero-project.github.io/) (Franka tabletop). |
| **Later (new env / your game / an arm)** | Your own SO-101 table: expect a light finetune even with [MolmoAct2-SO100_101](https://huggingface.co/allenai/MolmoAct2-SO100_101). A new game: yes. |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env | **LIBERO** (Franka tabletop, language tasks) | [libero-project.github.io](https://libero-project.github.io/), [Lifelong-Robot-Learning/LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO) | $0 |
| Robot | **SO-100 / SO-101** (official finetune) | [SO-101 docs](https://huggingface.co/docs/lerobot/en/so101), [BOM](https://github.com/TheRobotStudio/SO-ARM100) | **$121.94 DIY follower**; **$229.88 DIY leader+follower**; kits ~$200–$740 |
| Robot (lab) | DROID Franka, bimanual YAM | HF cards above | lab money; use sim instead |

### Paper

- MolmoAct2: [arXiv:2605.02881](https://arxiv.org/abs/2605.02881) — local `papers/pdfs/2605.02881_molmoact2.pdf`
- Predecessor MolmoAct 7B: [arXiv:2508.07917](https://arxiv.org/abs/2508.07917) — local `papers/pdfs/2508.07917_molmoact.pdf`
- Blog: [allenai.org/blog/molmoact2](https://allenai.org/blog/molmoact2)

---

## 4. Isaac GR00T N1.7

### Network

| Piece | What | Link |
|---|---|---|
| VLM backbone (slow-ish) | **Cosmos-Reason2-2B** (Qwen3-VL lineage), **gated** | [nvidia/Cosmos-Reason2-2B](https://huggingface.co/nvidia/Cosmos-Reason2-2B) |
| Full VLA | 2B VLM + ~1B flow-matching action transformer = **3B** | [nvidia/GR00T-N1.7-3B](https://huggingface.co/nvidia/GR00T-N1.7-3B) |
| LIBERO finetune | Franka / `LIBERO_PANDA` | [nvidia/GR00T-N1.7-LIBERO](https://huggingface.co/nvidia/GR00T-N1.7-LIBERO) |
| Code | Isaac-GR00T (N1.7 is current GA) | [NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) |
| Night factory | Cosmos-Predict2.5 + DreamGen (separate nets, used offline) | [DreamGen](https://research.nvidia.com/labs/gear/dreamgen/), [cookbook](https://nvidia-cosmos.github.io/cosmos-cookbook/recipes/end2end/gr00t-dreams/post-training.html) |

OpenHelix would **not** call this a true dual system (the action head typically shares the VLM's observation). NVIDIA still describes the family as dual-system.

### Action

| | |
|---|---|
| **Finetune just to get started?** | **No.** Download [GR00T-N1.7-LIBERO](https://huggingface.co/nvidia/GR00T-N1.7-LIBERO) (gated [Cosmos-Reason2-2B](https://huggingface.co/nvidia/Cosmos-Reason2-2B) first). That is access, not training. |
| **First env you can install** | [LIBERO](https://libero-project.github.io/). Also official scripts for RoboCasa and SimplerEnv. |
| **Later (new env / your game / an arm)** | SO-100 example is a *finetune recipe*. Dreams = train a world model overnight, then finetune GR00T. A new game: yes. |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env | LIBERO | [libero-project.github.io](https://libero-project.github.io/) | $0 |
| Env | RoboCasa (procedural kitchens) | [robocasa.ai](https://robocasa.ai/) | $0 |
| Env | SimplerEnv (Google Robot / WidowX) | [simpler-env/SimplerEnv](https://github.com/simpler-env/SimplerEnv) | $0 |
| Env | Isaac Lab / Lab-Arena | [isaac-sim/IsaacLab](https://github.com/isaac-sim/IsaacLab) | $0; NVIDIA GPU |
| Robot | SO-100 example in the repo | [Isaac-GR00T examples/SO100](https://github.com/NVIDIA/Isaac-GR00T) | **$121.94+** as above |
| Robot | DROID, Unitree G1, etc. (pretrain tags) | HF collection | G1 is thousands of dollars; do not buy to shop |

### Paper

- GR00T N1 (architecture; N1.7 is a later release): [arXiv:2503.14734](https://arxiv.org/abs/2503.14734) — local `papers/pdfs/2503.14734_groot_n1.pdf`
- DreamGen project: [research.nvidia.com/labs/gear/dreamgen](https://research.nvidia.com/labs/gear/dreamgen/)

---

## 5. NaVILA

### Network

| Piece | What | Link |
|---|---|---|
| System 2 (slow) | **VILA / Llama-3-8B**, 8-frame video, emits mid-level English (`moving forward 75cm`) | [a8cheng/navila-llama3-8b-8f](https://huggingface.co/a8cheng/navila-llama3-8b-8f) |
| S2 pretrain start | SigLIP + Llama-3-8B VILA pretrain | [a8cheng/navila-siglip-llama3-8b-v1.5-pretrain](https://huggingface.co/a8cheng/navila-siglip-llama3-8b-v1.5-pretrain) |
| System 1 (fast) | Vision **locomotion RL** policy (Isaac Lab → real Go2 / H1) | weights via [NaVILA repo](https://github.com/AnjieCheng/NaVILA) / [HF collection](https://huggingface.co/collections/a8cheng/navila-legged-robot-vision-language-action-model-for-naviga-67cfc82b83017babdcefd4ad) |
| Code | Training + Habitat eval | [AnjieCheng/NaVILA](https://github.com/AnjieCheng/NaVILA) |
| Isaac bench | VLN-CE-Isaac | [yang-zj1026/NaVILA-Bench](https://github.com/yang-zj1026/NaVILA-Bench) |

### Action

| | |
|---|---|
| **Finetune just to get started?** | **No.** VLM + locomotion policy are released. |
| **First env you can install** | Habitat [VLN-CE](https://github.com/jacobkrantz/VLN-CE) (easiest). Second: [NaVILA-Bench](https://github.com/yang-zj1026/NaVILA-Bench) on Isaac Lab. |
| **Later (new env / your game / an arm)** | Real Go2: their policy is meant to transfer; still expect sim-to-real pain. A new game: yes for the twitch half; S2 macros stay reusable. |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env | Habitat VLN-CE | [VLN-CE](https://github.com/jacobkrantz/VLN-CE), [Habitat](https://aihabitat.org/) | $0 |
| Env | VLN-CE-Isaac / NaVILA-Bench | [NaVILA-Bench](https://github.com/yang-zj1026/NaVILA-Bench) | $0; Isaac Sim |
| Robot | **Unitree Go2** (quadruped) | [unitree.com/go2](https://www.unitree.com/go2), [shop.unitree.com](https://shop.unitree.com) | **From $1,600** (Air, freight extra). Pro ~$2,800 list. EDU is quote-only (~$11k+). US reseller often higher. |
| Robot | Unitree H1 (humanoid) | Unitree H1 shop | **Not cheap.** Do not buy to shop. |

### Paper

- [arXiv:2412.04453](https://arxiv.org/abs/2412.04453) — local `papers/pdfs/2412.04453_navila.pdf`
- Project / videos: [navila-bot.github.io](https://navila-bot.github.io/)

---

## 6. FiS-VLA (Fast-in-Slow)

### Network

| Piece | What | Link |
|---|---|---|
| One 7B net | **Llama-2-7B** VLM. Last blocks *are* System 1; full net is System 2. Extra high-rate RGB / state / point cloud into S1. | [haosad/fisvla](https://huggingface.co/haosad/fisvla) |
| Code | HybridVLA-lineage training + RLBench test | [CHEN-H01/Fast-in-Slow](https://github.com/CHEN-H01/Fast-in-Slow) |

There is no second downloadable specialist. S1 is inside the 7B.

### Action

| | |
|---|---|
| **Finetune just to get started?** | **No.** [haosad/fisvla](https://huggingface.co/haosad/fisvla) is a released pretrained ckpt; `test_rlbench.sh` is the eval. |
| **First env you can install** | [RLBench](https://github.com/stepjam/RLBench) (CoppeliaSim — painful install, but public). |
| **Later (new env / your game / an arm)** | Re-backbone onto Gemma: yes (research). A new game: yes. |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env | **RLBench** (CoppeliaSim) | [stepjam/RLBench](https://github.com/stepjam/RLBench) | $0 |
| Robot | Real arm in the paper (not SO-101) | project page | lab arm; use RLBench |

### Paper

- [arXiv:2506.01953](https://arxiv.org/abs/2506.01953) — local `papers/pdfs/2506.01953_fis_vla.pdf`
- Videos: [fast-in-slow.github.io](https://fast-in-slow.github.io/)

---

## 7. OpenHelix

### Network

| Piece | What | Link |
|---|---|---|
| System 2 | **LLaVA-1.5-7B**, frozen; one learned `<ACT>` token | inside [OpenHelix/openhelix](https://huggingface.co/OpenHelix/openhelix) (`prompt_tuning_aux/llava_ckpt_safetensors` → merge to `pytorch_model.bin`) |
| System 1 | **3D Diffuser Actor** (`policy.pth`), RGB + proprio + point cloud | same HF repo |
| Code | MIT, CALVIN scripts | [OpenHelix-robot/OpenHelix](https://github.com/OpenHelix-robot/OpenHelix) |

### Action

| | |
|---|---|
| **Finetune just to get started?** | **No.** Merge the released safetensors and run their CALVIN eval. Fiddly, not training. |
| **First env you can install** | [CALVIN](http://calvin.cs.uni-freiburg.de/) ABC-D. |
| **Later (new env / your game / an arm)** | Gemma as S2: train the `<ACT>` projector (Path K), not 3DDA from scratch. A new game: yes (7-D gripper ≠ `CLOCK`). |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env | **CALVIN** ABC-D (Franka tabletop, long-horizon language) | [calvin.cs.uni-freiburg.de](http://calvin.cs.uni-freiburg.de/), [mees/calvin](https://github.com/mees/calvin) | $0 |
| Robot | Simulated Franka in CALVIN | same | $0. No SO-101 ckpt. |

### Paper

- [arXiv:2505.03912](https://arxiv.org/abs/2505.03912) — local `papers/pdfs/2505.03912_openhelix.pdf`
- Project: [openhelix-robot.github.io](https://openhelix-robot.github.io/)

---

## 8. π0.5 + Real-Time Chunking

### Network

| Piece | What | Link |
|---|---|---|
| Base VLA | **PaliGemma ~3B** + ~300M flow-matching expert ≈ **3.6B** | [lerobot/pi05_base](https://huggingface.co/lerobot/pi05_base) or openpi `gs://openpi-assets/checkpoints/pi05_base` |
| LIBERO finetune | same architecture | [lerobot/pi05_libero](https://huggingface.co/lerobot/pi05_libero) (and OpenPI `pi05_libero`) |
| Code | openpi + LeRobot | [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi), [huggingface/lerobot](https://github.com/huggingface/lerobot) |
| Fast loop | **Not a second net.** 50-step action chunks; **RTC** overlaps the next chunk with execution | LeRobot `--inference.type=rtc` |

The paper's high-level subtask head is **not** in the open checkpoints. Do not expect a planner that narrates subtasks.

### Action

| | |
|---|---|
| **Finetune just to get started?** | **No.** [lerobot/pi05_libero](https://huggingface.co/lerobot/pi05_libero) is already trained. |
| **First env you can install** | [LIBERO](https://libero-project.github.io/) via `lerobot-eval --env.type=libero`. |
| **Later (new env / your game / an arm)** | Your SO-101 table: **finetune**. A new game: yes. Paper hierarchy is not in the open weights. |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env | LIBERO | [libero-project.github.io](https://libero-project.github.io/), LeRobot `env.type=libero` | $0 |
| Robot | SO-100 / SO-101 via LeRobot | [SO-101 docs](https://huggingface.co/docs/lerobot/en/so101) | **$121.94 / $229.88 DIY** as above |
| Robot | ALOHA (public π0 towel ckpts, not π0.5) | openpi README | ALOHA is thousands of dollars; ignore for shopping |

### Paper

- π0.5: [arXiv:2504.16054](https://arxiv.org/abs/2504.16054) — local `papers/pdfs/2504.16054_pi05.pdf`
- π0 (the architecture π0.5 sits on): [arXiv:2410.24164](https://arxiv.org/abs/2410.24164) — local `papers/pdfs/2410.24164_pi0.pdf`
- RTC: [arXiv:2506.07339](https://arxiv.org/abs/2506.07339) — local `papers/pdfs/2506.07339_real_time_chunking.pdf`
- Blog: [physicalintelligence.company/blog/pi05](https://www.physicalintelligence.company/blog/pi05)

---

## 9. RoboDual

### Network

| Piece | What | Link |
|---|---|---|
| System 2 | **OpenVLA-7B** generalist (Llama-2-7B + SigLIP), LoRA'd, emits coarse actions + lang latents | [qwbu/RoboDual-OpenVLA-Generalist](https://huggingface.co/qwbu/RoboDual-OpenVLA-Generalist) (needs a local [OpenVLA-7B](https://huggingface.co/openvla/openvla-7b) path in their scripts) |
| System 1 | **DiT** specialist (RGB+depth+tactile+proprio) | [qwbu/RoboDual-Specialist](https://huggingface.co/qwbu/RoboDual-Specialist) |
| Code | [OpenDriveLab/RoboDual](https://github.com/OpenDriveLab/RoboDual) | |

### Action

| | |
|---|---|
| **Finetune just to get started?** | **No.** Both HF cards are released. |
| **First env you can install** | [CALVIN](http://calvin.cs.uni-freiburg.de/). |
| **Later (new env / your game / an arm)** | New tabletop: they train S1 from scratch. A new game: yes. |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env | CALVIN ABC-D | [calvin.cs.uni-freiburg.de](http://calvin.cs.uni-freiburg.de/) | $0 |
| Robot | Paper real-robot; no SO-101 | project page | lab; use CALVIN |

### Paper

- [arXiv:2410.08001](https://arxiv.org/abs/2410.08001) — local `papers/pdfs/2410.08001_robodual.pdf`
- Project: [opendrivelab.github.io/RoboDual](https://opendrivelab.github.io/RoboDual/)

---

## 10. OneTwoVLA

### Network

| Piece | What | Link |
|---|---|---|
| Instantiation | **π0** (PaliGemma 3B + flow expert). One net, two *modes* (reason text vs act). | Built on π0; see [openpi](https://github.com/Physical-Intelligence/openpi) |
| Code + UMI client | Official impl | [Fanqi-Lin/OneTwoVLA](https://github.com/Fanqi-Lin/OneTwoVLA), [UMI client](https://github.com/Fanqi-Lin/OneTwoVLA-UMI-Client) |
| Data | Robot + synthetic embodied-reasoning VL | [Richard-Nai/onetwovla-dataset](https://huggingface.co/datasets/Richard-Nai/onetwovla-dataset) |
| Policy weights | **Not a clear one-click HF VLA card** at survey time | Confirm on the GitHub README before promising a download |

### Action

| | |
|---|---|
| **Finetune just to get started?** | **Yes.** Code + datasets are public; there is no one-click policy card. Their README is `train_scripts/train_*.sh`, then a UMI hardware client — not a sim eval. |
| **First env you can install** | **None advertised.** You can watch [one-two-vla.github.io](https://one-two-vla.github.io/). The useful no-train steal is the VL synthesizer, not a playable agent. |
| **Later (new env / your game / an arm)** | Train from π0 on their cocktail / grounding data, or on yours. |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env | Authors' real kitchen (UMI). **No** public Habitat/LIBERO loop advertised. | [one-two-vla.github.io](https://one-two-vla.github.io/) | $0 to watch videos |
| Robot | UMI / their arms | UMI client repo | lab hardware |

### Paper

- [arXiv:2505.11917](https://arxiv.org/abs/2505.11917) — local `papers/pdfs/2505.11917_onetwovla.pdf`

---

## 11. Magma-8B

### Network

| Piece | What | Link |
|---|---|---|
| Single net | **Llama-3-8B-Instruct** + Magma vision, SoM/ToM pretraining. No System 1. | [microsoft/Magma-8B](https://huggingface.co/microsoft/Magma-8B) |
| Code | [microsoft/Magma](https://github.com/microsoft/Magma) | |

### Action

| | |
|---|---|
| **Finetune just to get started?** | **No** for their published sim/UI evals. Download [Magma-8B](https://huggingface.co/microsoft/Magma-8B) and run the repo eval. There is no S1. |
| **First env you can install** | [SimplerEnv](https://github.com/simpler-env/SimplerEnv) and [LIBERO](https://libero-project.github.io/). Also UI / Mind2Web-style. |
| **Later (new env / your game / an arm)** | Real WidowX in the paper is few-shot finetune. Adding twitch is Path K. |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Env | SimplerEnv | [simpler-env/SimplerEnv](https://github.com/simpler-env/SimplerEnv) | $0 |
| Env | LIBERO | [libero-project.github.io](https://libero-project.github.io/) | $0 |
| Robot | WidowX few-shot in the paper | — | lab; use SimplerEnv |

### Paper

- [arXiv:2502.13130](https://arxiv.org/abs/2502.13130) — local `papers/pdfs/2502.13130_magma.pdf`
- Project: [microsoft.github.io/Magma](https://microsoft.github.io/Magma/)

---

## 12. Helix (Figure) — closed reference

### Network

| Piece | What | Link |
|---|---|---|
| System 2 | Undisclosed **7B** VLM, 7–9 Hz, emits a latent | **No weights** |
| System 1 | **80M** visuomotor transformer, 200 Hz, **own camera stream** | **No weights** |

### Action

| | |
|---|---|
| **Finetune just to get started?** | **Cannot.** No weights. |
| **First env you can install** | None. |
| **Later (new env / your game / an arm)** | Watch [the video](https://www.figure.ai/news/helix). |

### World

| Kind | Exact thing | Link | Price |
|---|---|---|---|
| Robot | Figure humanoid | [figure.ai/news/helix](https://www.figure.ai/news/helix) | Not for sale as a kit |

### Paper

- None. Blog only: [figure.ai/news/helix](https://www.figure.ai/news/helix)

---

## Quick strip: finetune just to get started?

“No” means: released weights + an env you can install, and the policy is already trained for that env. Setup (conda, gated HF, merge shards) is not finetuning. Moving to a *different* env later is always more work — that is no longer “getting started.”

| # | Option | Finetune just to start? | First installable env |
|---|---|---|---|
| 1 | InternVLA-N1 | **No** | [InternNav](https://github.com/InternRobotics/InternNav) + Habitat; [Gradio](https://huggingface.co/spaces/InternRobotics/InternNav-Eval-Demo) |
| 2 | Gemma + stolen S1 | **Yes** — no such checkpoint exists | None until you train. Watch #7 or #1 instead. |
| 3 | MolmoAct2 | **No** | [LIBERO](https://libero-project.github.io/) via Think-LIBERO |
| 4 | GR00T N1.7 | **No** | LIBERO (also RoboCasa / SimplerEnv scripts) |
| 5 | NaVILA | **No** | Habitat [VLN-CE](https://github.com/jacobkrantz/VLN-CE); then Isaac [NaVILA-Bench](https://github.com/yang-zj1026/NaVILA-Bench) |
| 6 | FiS-VLA | **No** | [RLBench](https://github.com/stepjam/RLBench) (CoppeliaSim) |
| 7 | OpenHelix | **No** | [CALVIN](http://calvin.cs.uni-freiburg.de/) |
| 8 | π0.5 | **No** | LIBERO via `lerobot-eval` |
| 9 | RoboDual | **No** | CALVIN |
| 10 | OneTwoVLA | **Yes** — train scripts, no policy card, no public sim loop | Videos only |
| 11 | Magma-8B | **No** | [SimplerEnv](https://github.com/simpler-env/SimplerEnv), LIBERO (no S1) |
| 12 | Helix | **Cannot** | None |
