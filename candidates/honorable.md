# Honorable mentions (not full cards)

These came up while shopping. They are dependencies, negative controls, or next-year revisits — not first pulls.

| id | params | why it appeared | why it is not a primary |
|---|---|---|---|
| **SmolVLA** | ~450M (SigLIP + SmolLM2-135M + diffusion) | LeRobot default on SO-101; [paper](https://arxiv.org/abs/2506.01844); local playgrounds exist | Planner is smaller than the Gemma e4B you rejected. Use only to verify the arm wires. |
| **NORA / NORA-1.5** | 3B Qwen2.5-VL | Modern VLM, OXE, FAST tokens, [demos](https://declare-lab.github.io/nora), [code](https://github.com/declare-lab/nora) | Right VLM family, wrong size, no dual loop. |
| **OpenVLA 7B** | 7B Llama-2 | [arXiv:2406.09246](https://arxiv.org/abs/2406.09246); backbone of RoboDual | Single-system, old core. Download as a dependency. |
| **LCB** | LLaVA-7B + 3DDA | [arXiv:2405.04798](https://arxiv.org/abs/2405.04798); invented `<ACT>` | OpenHelix is the maintained descendant. |
| **HiRT** | InstructBLIP-7B + RT-1 | [arXiv:2410.05273](https://arxiv.org/abs/2410.05273) | True dual, weaker stack than OpenHelix/RoboDual. |
| **InternVLA-A1 / A1.5 / Vesta** | Qwen3 / Qwen3.5 2–3B + (A1.5) frozen WAN2.2-5B foresight | Official manip sibling; A1.5 attaches a **video decoder at train time** and deletes it at serve | Planner is e4B-class. Community SO/RoboDojo LoRAs (`hxma`, `Jia-Zeng`, `zaleni`) do not fix that. |
| **InternVLA-M1** | Qwen2.5-VL-3B + 86M DiT on its own DINOv2 | Missed official **manip** dual. S1 has its own eyes, same OpenHelix test N1 already passes. LIBERO cards on HF | 3B planner. Compact dual *reference*, not Path N. |
| **RynnVLA-001 / 002 + WorldVLA** | Chameleon-7B + image decoder | Vision-decoder family. | **Rejected 2026-09-04.** Mouth garbage; dream not usable. Sandbox deleted. Do not reopen. |
| **EO-1** | Qwen2.5-VL-**3B** + flow | Official `processor.generate` claims text **and** actions. [HF](https://huggingface.co/IPEC-COMMUNITY/EO-1-3B) | Next crop #1. 3B — below the 12B bar. |
| **ChatVLA-1** | Qwen2-VL-**2B** + MoE | [zzymeow/ChatVLA](https://huggingface.co/zzymeow/ChatVLA). ChatVLA-2 has no robot weights. | Next crop #2. 2B. |
| **ECoT-OpenVLA** | OpenVLA / Llama-2-7B | TASK/PLAN/SUBTASK/MOVE then action. [ecot-openvla-7b-bridge](https://huggingface.co/Embodied-CoT/ecot-openvla-7b-bridge) | Next crop #4. `below_reject` core. |
| **VLA-JEPA** | Qwen3-VL-2B + V-JEPA2 (train) + DiT | LeRobot-native latent world model; many community SO-101 weights | 2B planner. |
| **Cosmos Policy** | Cosmos-Predict2-2B video model emits actions+frames+values | NVIDIA; LIBERO 98.5%; planning ckpt | Not a VLM. Night/planning reference next to DreamGen. |
| **Dream-VLA-7B** | Dream-7B diffusion LM + Qwen2ViT | Odd backbone, OXE, HF-native | Single-system. |
| **StarVLA / VLAct** | Qwen3-VL-4B + OFT / π / GR00T heads | Lego kit; continued pretrain includes MolmoAct | 4B. Tokenizer-only `…-Instruct-Action` is not a trained VLA. |
| **UniVLA (BAAI / qwbu)** | Emu3 tokenizer + world-model pretrain, 7B | Another generative-prior 7B | Older / less turnkey than RynnVLA-002. |
| **StreamVLN** | ~8B LLaVA-Video | Public VLN weights; slow-fast KV | Not true dual. Behind InternVLA-N1. |
| **X-VLA / Evo-1 / ServoVLA** | 0.8B–4B, now in LeRobot | Soft prompts, cheap-arm specialists | Wrong planner size. |
| **WALL-OSS** | Qwen2.5-VL-3B + MoT ~4B | Uni-CoT paper. [`wall-oss-flow`](https://huggingface.co/x-square-robot/wall-oss-flow) | Next crop #3. Official scripts are action-first. 3B planner. |
| **Qwen-VLA / Qwen-RobotNav / ABot-N1** | 4B+DiT or 4B+2B dual nav | Paper-class peers (Qwen-VLA does manip+nav in one net) | **No public weights** as of 2026-09-02. |
| **Gemini Robotics ER** | closed | [browser SPA toy](https://avikde.github.io/vla-pipeline/) | Architecture demo only. |
| **π0.5 paper hierarchy** | n/a | Subtask tokens in the paper | Not in openpi. |
| **GraspVLA** | mid-size | [LIBERO playground](https://github.com/MiYanDoris/GraspVLA-playground) | Grasp specialist, not a general dual planner. |

Community Hub dumps (`tylergp/molmoact2-*`, `jstm/molmoact2_*`, `hbseong/internvla_pick_and_place_so101`, OpenVLA-OFT forks, SpatialVLA LoRAs) are listed and dismissed in [`notes/08_community_gems.md`](../notes/08_community_gems.md). Do not promote them to cards.

## SmolVLA links (hardware bring-up only)

- HF: `lerobot/smolvla_base`
- Paper: https://arxiv.org/abs/2506.01844
- Local browser playground (ROS2/Gazebo, not hosted): https://github.com/rsasaki0109/vla_ros2
