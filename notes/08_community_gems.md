# Community sweep (HF + lesser-known siblings)

Survey date: 2026-09-02. This is **not** a second shortlist. The twelve cards and three paths stay put. This note answers: *are there hidden gems on Hugging Face — community finetunes, odd attachments, same class as MolmoAct2 / InternVLA, outside the main papers?*

Short answer: **no secret 7B true-dual that beats InternVLA-N1 or MolmoAct2-Think.** The Hub is full of LeRobot auto-uploads that inherit the official architecture and add no eval. The interesting finds are a different family: **VLA + vision / world decoder**, plus one missed official InternVLA sibling (M1) and a Lego kit (StarVLA / VLAct) you can steal pieces from.

## Method

Hugging Face `api/models` search (sorted by downloads) for MolmoAct, InternVLA, OpenVLA, WorldVLA, RynnVLA, SpatialVLA, UniVLA, StarVLA, VLAct, Dream-VLA, MemoryVLA, Qwen-VLA, ABot, StreamVLN, X-VLA, WALL-OSS, Evo1, VLA-JEPA, LingBot-VA, ServoVLA, Cosmos Policy, so101, plus paper/GitHub follow-ups. Downloads are a weak quality signal; LeRobot `push_to_hub` dumps inflate them.

## What is *not* a gem

These look like "community MolmoAct2 / InternVLA" in search and are not.

| Repo | Why it showed up | What it actually is |
|---|---|---|
| `tylergp/molmoact2-libero-ft-10mm-*` | 1k–5k downloads | Auto LeRobot cards. Template still says `policy.type=act`. Intermediate LIBERO training steps, no eval writeup. |
| `jstm/molmoact2_single_arm` / `_bimanual` | Named MolmoAct2 | Real Colosseum-sim finetune (~10k steps, 1539 episodes). **No evaluation posted.** Same architecture as official. |
| `hbseong/internvla_pick_and_place_so101` | Named internvla + SO-101 | **0.9B** weights. Not InternVLA-N1/A1/M1. Generic LeRobot dump. |
| `mradermacher/*-GGUF` | InternVLA-N1 / M1 / Magma | Quantizations of official cards. Useful later, not a new model. |
| Community OpenVLA-OFT (`Sakits`, `Sylvest`, `VLA-Arena`, `Juelg`, `gen-robot` RL) | High downloads | LIBERO / ManiSkill / arena specialists on **Llama-2-7B**. Same brain you already rejected. `moojink/*-oft-*` is the official OFT paper, not a little guy. |
| SpatialVLA community (`violet-blue`, `vovantuan`, `nikooo6666` xArm) | Finetune spam | 4B PaLiGemma2. Below the e4B bar. |
| `quiet-storm/univla-policy-lerobot-*-wrist-decoder-residual` | "decoder" in the name | Hobby LeRobot UniVLA run. Residual wrist head, not a published world model. |
| `llxs/OneVLA` | Name collision with OneTwoVLA / OneVL | Empty card, 92 downloads. Ignore. |
| Magma-R1 (`batwBMW`, GGUFs) | Magma + community | Android UI control, not a robot VLA. |
| `anikitakis/vla_so101_pick_n_place_full_expert` and most `*so101*vla_jepa*` | Cheap-arm hope | Task specialists. Planner is 2B-class or unnamed. |

**Qwen-VLA** (`Qwen3.5-4B` + 1.15B DiT, manip **and** nav in one prompt-conditioned generalist, 97.9% LIBERO / R2R numbers) looks like the missing official peer. **Weights are not on the Hub.** GitHub issues [#2](https://github.com/QwenLM/Qwen-VLA/issues/2) and [#3](https://github.com/QwenLM/Qwen-VLA/issues/3) are still open as of this sweep. `Qwen-RobotNav` explicitly says there is no weight release. Treat it as a closed_reference until they upload.

**ABot-N1** (AutoNavi): slow Qwen-3.5-4B CoT + pixel goals, fast 2B action expert. Paper scores beat InternVLA-N1 / NaVILA on their tables. **No Hugging Face model repo found.** Path N paper-only peer.

## The vision-decoder family (this is the real find)

You asked for "a version with a vision decoder attached, for some reason." That reason in 2025–2026 papers is: **force the latent to encode physics, or manufacture night-time video, or both.** Four pullable lines do this. None is a Gemma-12B-class planner.

### 1. RynnVLA-001 / 002 — keep this one

The closest thing to "MolmoAct2-class, but the VLM can also draw the next frame."

| | RynnVLA-001 | RynnVLA-002 / WorldVLA |
|---|---|---|
| Org | Alibaba DAMO (RynnBot) | same |
| Backbone | **Chameleon-7B** (discrete image tokens + decoder) | same family; 002 adds a continuous Action Transformer |
| Trick | Stage 1: ego-centric **video generation** on human demos. Stage 2: predict future human trajectories + frames. Stage 3 (you do it): VLA finetune. | Unified action + image generation. 002 adds wrist-cam **generation**, state input, 97.4% LIBERO. |
| HF | [`RynnVLA-001-7B-Base`](https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-001-7B-Base), [`…-Trajectory`](https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-001-7B-Trajectory) | [`WorldVLA`](https://huggingface.co/Alibaba-DAMO-Academy/WorldVLA), [`RynnVLA-002`](https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-002) |
| Code | [RynnVLA-001](https://github.com/alibaba-damo-academy/RynnVLA-001) | [WorldVLA paper](https://arxiv.org/abs/2506.21539), [RynnVLA-002 paper](https://arxiv.org/abs/2511.17502) |
| Dual? | single / generative prior | single AR + optional continuous head |
| Why it matters to you | Overnight loop is *the architecture*, not an add-on. 7B, open (Apache). | Same, plus you can query "what happens if I take this action?" as pixels. |
| Why it is not Path N/K | Chameleon-7B is not Gemma 4 12B. No true async S1. No Habitat VLN product. Community reuploads (`jcenaa/WorldVLA-ActionModel-*`) are action-only slices of the official zoo. |

If Path R's question becomes "I want a policy that can hallucinate tomorrow's pixels from today's actions," start here — not at another MolmoAct2 LoRA.

### 2. InternVLA-A1.5 — official, foresight discarded at serve time

Already on the honorable list as A1/Vesta. The 1.5 revision is the one with the attached decoder:

- Backbone: **Qwen3.5-2B** + 460M unified expert.
- Train-time: learnable foresight tokens condition a **frozen WAN2.2-TI2V-5B** video generator. Video loss over the action-chunk horizon.
- Infer-time: **video branch deleted.** Flow-matching actions only.
- HF: [`InternVLA-A1.5-base`](https://huggingface.co/InternRobotics/InternVLA-A1.5-base), [`-Libero`](https://huggingface.co/InternRobotics/InternVLA-A1.5-Libero), RoboTwin, DOMINO.
- Community: `hxma/internvla_a15_robodojo_60k`, `Jia-Zeng/InternVLA-A1-3B-FineTuned-Place_Markpen`, `zaleni/internvla-a1-*`. Real task finetunes, 2–3B, no dual loop.

Pattern is useful (night WAN, day action-only). Planner is in the e4B reject zone. Do not pull as a brain.

### 3. VLA-JEPA — latent world model, lots of SO-101 hobby weights

LeRobot-native. Qwen3-VL-**2B** + V-JEPA2 predictor (train-time video/latent loss) + DiT action head. Official: [`lerobot/VLA-JEPA-Pretrain`](https://huggingface.co/lerobot/VLA-JEPA-Pretrain), [`…-LIBERO`](https://huggingface.co/lerobot/VLA-JEPA-LIBERO). Community SO-101: `geonmin-kim/VLA-JEPA-3B-SO101-*`, `khoavucao2511/so101_vla_jepa_*`, `coltonhabr/VLA-JEPA-SO101-30`. Paper: [arXiv:2602.10098](https://arxiv.org/abs/2602.10098).

This is the cheap-arm "world model attached" line. Planner too small.

### 4. Cosmos Policy — video model *is* the policy

Not a VLM. NVIDIA post-trains **Cosmos-Predict2-2B** so the same diffusion net emits **actions + future frames + values**. LIBERO 98.5%. Planning checkpoint exists for ALOHA. HF collection: [nvidia/cosmos-policy](https://huggingface.co/collections/nvidia/cosmos-policy). Paper: [arXiv:2601.16163](https://arxiv.org/abs/2601.16163).

Overnight/planning reference, especially next to GR00T + DreamGen. Not a reasoner. 2B.

**OneVL** (Xiaomi, driving): [`xiaomi-research/OneVL_visual_decoder_pt`](https://huggingface.co/xiaomi-research/OneVL_visual_decoder_pt) attaches an Emu3.5 visual decoder at train time and **throws it away at infer**. Same idea as A1.5, wrong domain (NAVSIM / ROADWork), not a robot VLA.

## Missed official sibling: InternVLA-M1

Not community, but it did not make the first twelve because the first pass followed N1 (nav) and A1 (manip + generation).

- Paper: [arXiv:2510.13778](https://arxiv.org/abs/2510.13778)
- HF: [`InternRobotics/InternVLA-M1`](https://huggingface.co/InternRobotics/InternVLA-M1) + LIBERO Spatial/Object/Goal/Long + RT-1/Bridge pretrain
- Dual claim: Qwen2.5-VL-**3B** language head (spatial pretrain) + **86M diffusion** action expert on its **own DINOv2** (21M) + state encoder. Same OpenHelix test as InternVLA-N1 (S1 sees fresh pixels), different job (tabletop). ~4.1B total, ~10 FPS VLM on a 4090.
- Community: `TingtingDu/InternVLA-M1-checkpoint-steps50k` (training dump)

OpenHelix would call this closer to **true** than π0 (S1 has its own encoder). InternVLA-N1 already passes that test on navigation. M1's planner is 3B — same reject as NORA. Use it as a **smaller dual reference** if you steal an S1, not as Path N.

## Other same-class oddballs with weights

| Thing | Size / brain | Dual | Why look | Why not first |
|---|---|---|---|---|
| **Dream-VLA-7B** [`Dream-org/Dream-VLA-7B`](https://huggingface.co/Dream-org/Dream-VLA-7B) | Dream-7B **diffusion LM** + Qwen2ViT | single | Unusual backbone (dLLM, not AR). OXE, HF `predict_action`, Apache. [arXiv:2512.22615](https://arxiv.org/abs/2512.22615) | No twitch loop. Unknown vs Gemma 12B. |
| **StarVLA / VLAct** | Qwen3-VL-**4B** + FAST / OFT / π / GR00T heads | near_expert (GR00T head is the interesting one) | Lego codebase. Continued pretrain on DROID + InternData-A1 + RoboCoin + **MolmoAct**. Many LIBERO / RoboTwin / VLA-Arena finetunes. [`StarVLA/VLAct_Qwen3_Pretrain`](https://huggingface.co/StarVLA/VLAct_Qwen3_Pretrain), [collection](https://huggingface.co/collections/StarVLA/vlact-6a903c2e0c176179da425c96), [code](https://github.com/starVLA/VLAct) | 4B planner. `Qwen3-VL-4B-Instruct-Action` is **tokenizer-only** (2048 action tokens, no extra training). |
| **UniVLA** [`qwbu/univla-7b`](https://huggingface.co/qwbu/univla-7b), [BAAI code](https://github.com/baaivision/UniVLA) | Emu3 tokenizer (vision decode) + world-model pretrain | single + generative prior | Another 7B with a real image tokenizer/decoder. CALVIN / LIBERO / R2R finetunes. | Older than RynnVLA-002; less turnkey. |
| **StreamVLN** [`mengwei0427/StreamVLN_Video_qwen_1_5_…`](https://huggingface.co/mengwei0427/StreamVLN_Video_qwen_1_5_r2r_rxr_envdrop_scalevln) | ~8B LLaVA-Video | slow-fast **KV**, not dual S1 | Path N also-ran with public weights. Sliding-window KV + pruned memory. [arXiv:2507.05240](https://arxiv.org/abs/2507.05240) | No separate pixel-seeing S1. Weaker than InternVLA-N1 on ABot's tables. |
| **Embodied-CoT** [`Embodied-CoT/ecot-openvla-7b-bridge`](https://huggingface.co/Embodied-CoT/ecot-openvla-7b-bridge) | OpenVLA-7B that writes spatial CoT | behavioral_switch | "Think then act" on the old stack. Empty model card. | Llama-2. OpenHelix / OneTwoVLA already cover this idea. |
| **X-VLA** [`2toINF/X-VLA-Pt`](https://huggingface.co/2toINF/X-VLA-Pt), `lerobot/xvla-*` | **0.9B** Florence-2 + soft prompts | single | In LeRobot. Embodiment via soft prompts, including `so101_bimanual`. | Not a reasoner. |
| **WALL-OSS-0.5** [`x-square-robot/wall-oss-0.5`](https://huggingface.co/x-square-robot/wall-oss-0.5) | Qwen2.5-VL-**3B** + MoT action expert ~4B | near_expert | In LeRobot. Community SO-ish finetunes exist. [arXiv:2605.30877](https://arxiv.org/html/2605.30877v2) | 3B VL expert. |
| **Evo-1** `MINT-SJTU/Evo1_*`, `lerobot` docs | InternVL3-**1B** + DiT | near_expert | In LeRobot. LIBERO / MetaWorld / RoboTwin cards. | Tiny. |
| **ServoVLA-SO101** [`ServoVLA/ServoVLA-SO101`](https://huggingface.co/ServoVLA/ServoVLA-SO101) | DINOv3 + Qwen3.5-**0.8B** | single | Honest cheap-arm specialist, documented cameras/chunk. | Not your planner. |
| **LingBot-VA** `lerobot/lingbot_va_*` | ~5B, community SO-101 inits | ? | LeRobot world-model-adjacent policy. | Thin cards; 2B–5B zone. |
| **TRI VLA Foundry** [github](https://github.com/TRI-ML/vla_foundry) | from-scratch + Qwen3-VL families | kit | Training stack, LBM Eval. Not a Hub celebrity. | Framework, not a dual product. |
| CogACT, HybridVLA, TraceVLA, MemoryVLA, SpatialVLA-4B | Llama-2 or 4B | near / single | 2024–25 papers, weights exist | Already-known class, old or small brains. |

## If you want to give a little guy a *real* shot

Next window is **look, not pull**, four entries: JARVIS-VLA, then RynnVLA/WorldVLA (vision decoder + harness-talk goal), then MolmoAct2, then InternVLA-N1, then small sandboxes. Script: [`09_next_session.md`](09_next_session.md). Sibling scorecard: [`10_sibling_list.md`](10_sibling_list.md).

Do not clone a random `*molmoact2*ft*` repo. RynnVLA / WorldVLA is the unofficial line that changes the *robot* design space (vision decoder is first-class). StarVLA/VLAct and InternVLA-M1 stay on this honorable list; they are not in the next look queue.

Everything else on this page is either official-small, official-closed, or a Hub training dump.
