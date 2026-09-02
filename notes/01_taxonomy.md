# What counts as quick-twitch / slow-plan

Mapped onto `../stateful_realtime_thinking/notes/01_literature_survey.md` thread A, plus OpenHelix's 2025 taxonomy ([arXiv:2505.03912](https://arxiv.org/abs/2505.03912)).

## The test OpenHelix actually uses

A **true dual system** is not "VLM plus some action head." System 1 must take **real-time perception** (RGB, sometimes depth / point cloud / proprio) on every fast tick. If S1 only consumes an S2 latent or a frozen action chunk, the fast loop is open-loop between S2 calls. That is useful (sibling Options 1 and 6) but it is not "hold the button and watch."

| Class in this repo | Sibling analog | S2 does | S1 does | S1 sees fresh pixels? |
|---|---|---|---|---|
| `true_async` | Helix / OpenHelix / RoboDual / LCB | 2–10 Hz plan or latent | 20–200 Hz actions | yes |
| `true_embedded` | FiS-VLA | full VLM, low-rate frames | last VLM blocks + extras | yes (high-rate extras) |
| `true_hierarchical` | NaVILA / InternVLA-N1 | language mid-level ("forward 75 cm") | locomotion / nav policy | yes |
| `near_expert` | π0 / GR00T N1.7 / MolmoAct2 | VLM features | flow / diffusion expert | usually **same** observation as S2 |
| `behavioral_switch` | OneTwoVLA | CoT when the net decides to | action expert otherwise | same net |
| `single` | OpenVLA / Magma / NORA | one AR pass | — | n/a |
| `kit` | sibling Option 5 DIY | your Gemma 4 12B | someone else's S1 | if you wire it that way |

NVIDIA still describes GR00T as dual-system in blogs. OpenHelix explicitly **excludes** π0 and GR00T N1 from the true-dual table for the perception reason above. This repo scores GR00T / π0 / MolmoAct2 high on *engineering maturity* and lower on *dual purity*.

## Handoff media (from the sibling survey)

| Handoff | Who uses it here |
|---|---|
| Latent / `<ACT>` token | OpenHelix, LCB |
| Coarse action + language | RoboDual |
| Shared last blocks | FiS-VLA |
| Language mid-level skills | NaVILA, InternVLA-N1 |
| KV cache into an action expert | MolmoAct2 |
| Action chunks + RTC overlap | π0.5 |
| "Dream" videos → inverse dynamics | GR00T-Dreams (overnight, not the control loop) |

## Why 7B-class dual papers will disappoint on reasoning

The 2024–mid-2025 dual-system literature standardized on **LLaVA-1.5-7B**, **InstructBLIP-7B**, or **OpenVLA / Llama-2-7B**. Those cores are older and weaker than Gemma 4 12B, and in the same band as the Gemma 4 e4B you already rejected for planning.

The 2025–2026 wave that has a chance on criterion 3:

- **Qwen2.5-VL-7B** — InternVLA-N1 System 2.
- **Llama-3-8B** — NaVILA, Magma.
- **Molmo2-ER** — MolmoAct2 (embodied-reasoning specialist; paper claims it beats GPT-5 / Gemini Robotics ER-1.5 on *embodied* benches, not general coding).
- **Qwen3-VL-8B** — Vesta / InternVLA-A1 lineage (planner, less of a turnkey VLA than InternVLA-N1).
- **Keep Gemma 4 12B** and only steal an S1 (`gemma4-diy`).

## Size excuses (criterion 1)

Nothing on the shortlist needs to be >20B. The useful excuses go the *other* way:

- **Do not shrink S2 below ~7–8B** if you want Gemma-12B-like planning. 2B–3B VLMs (Cosmos-Reason2-2B, PaliGemma-3B, Qwen2.5-VL-3B, SmolLM2) are the e4B failure mode.
- A **2B–14B world model used only at night** (Cosmos-Predict2.5) is a valid extra, not a replacement for the daytime planner.
- LoRA / prompt-tuning of S2 plus a frozen or lightly-tuned S1 is the cheap training mechanism (OpenHelix, RoboDual, LCB).
