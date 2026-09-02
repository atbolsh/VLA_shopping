# Scorecard

Scores are 1–5. Rubric lives in `../AGENTS.md`. Totals are an unweighted sum (max 35) so a specialist can still win its column even if it loses the total.

**Do not treat the total as "buy this."** InternVLA-N1 wins navigation+dual+reasoning. MolmoAct2 / GR00T / π0.5 win "I want a robot on the desk this month." OpenHelix wins "I want to swap my Gemma in as S2."

The `pull` column is shopping rank. **Next window is a look order**, not this table: RynnVLA-001/002 + WorldVLA → MolmoAct2 → InternVLA-N1 → small sandboxes. [`09_next_session.md`](09_next_session.md).

| id | name | params | dual class | dual | reason | size | env | robot | night | open | total | pull |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| internvla-n1 | InternVLA-N1 | ~8B S2 | true_async | 5 | 4 | 5 | 5 | 2 | 3 | 5 | 29 | 1 |
| gemma4-diy | Gemma 4 12B + stolen S1 | 12B + small | kit | 5* | 5 | 4 | 4 | 3 | 4 | 5 | 30* | 2 |
| molmoact2 | MolmoAct2-Think | ~5B (HF) | near_expert | 3 | 4 | 5 | 4 | 5 | 2 | 5 | 28 | 3 |
| groot-n17 | GR00T N1.7 | 3B | near_expert | 3 | 2 | 5 | 5 | 4 | 5 | 4 | 28 | 4 |
| navila | NaVILA | 8B + loco | true_hierarchical | 5 | 3 | 5 | 5 | 3 | 2 | 5 | 28 | 5 |
| fis-vla | FiS-VLA | 7B | true_embedded | 5 | 2 | 5 | 4 | 2 | 2 | 5 | 25 | 6 |
| openhelix | OpenHelix | 7B + 3DDA | true_async | 5 | 2 | 5 | 4 | 1 | 2 | 5 | 24 | 7 |
| pi05 | π0.5 + RTC | 3.6B | near_expert | 3 | 2 | 5 | 5 | 5 | 2 | 4 | 26 | 8 |
| robodual | RoboDual | 7B + DiT | true_async | 5 | 2 | 5 | 4 | 1 | 2 | 5 | 24 | 9 |
| onetwovla | OneTwoVLA | ~3.3B | behavioral_switch | 4 | 3 | 5 | 2 | 2 | 4 | 3 | 23 | 10 |
| magma-8b | Magma-8B | 8B | single | 1 | 3 | 5 | 4 | 2 | 2 | 4 | 21 | 11 |
| helix-closed | Helix | 7B+80M | true_async | 5 | 3 | 5 | 1 | 1 | 1 | 1 | 17 | — |

`gemma4-diy` totals assume you actually wire S1. Starred dual=5 is *potential*, not shipped. Full Network / Action / World / Paper blocks: [`06_option_specs.md`](06_option_specs.md).

## Three shopping paths

### Path N — navigation first

**InternVLA-N1** in InternNav (Habitat + Isaac). True dual, Qwen2.5-VL-7B System 2, hosted Gradio eval, 3k-scene dataset. Closest off-the-shelf analog to "look at a room, plan, twitch toward the goal."

Backup: **NaVILA** if you want a Unitree Go2 and language macros (`forward 75cm`) rather than a learned nav diffusion policy.

### Path K — keep the brain you already like

**Gemma 4 12B as System 2**, OpenHelix / LCB / InternVLA-N1-S1 as System 1. This is the only way to keep criterion 3 without hoping a 2024 7B VLM grew new reasoning. OpenHelix is the cleanest open recipe (frozen LLaVA, trained `<ACT>` token + projector + 3DDA). FiS-VLA is the research-prettier variant (S1 *is* the last blocks) but harder to re-backbone.

### Path R — cheap robot + overnight dreams

1. **MolmoAct2-SO100_101** if the question is "which 2026 open VLA is actually finetuned on the SO-101 ($121.94 DIY follower BOM), with a Think mode."
2. **GR00T N1.7 + DreamGen / Cosmos** if the question is "which stack already manufactures night-time training data from a handful of daytime demos."
3. **π0.5 in LeRobot** if you want the most-walked path (LIBERO eval one-liner, RTC, SO-101). Accept weak PaliGemma reasoning.

## Explicit non-picks (so later-us does not re-litigate)

| Model | Why it is not a primary card |
|---|---|
| SmolVLA (~450M) | Perfect for bringing up an SO-101. Useless as the planner. Use it as a hardware smoke test only. |
| NORA / NORA-1.5 (3B, Qwen2.5-VL) | Modern VLM, still the e4B size class, no dual loop. |
| OpenVLA 7B | The backbone RoboDual sits on. Pull it as a *dependency*, not as the product. |
| LCB, HiRT, DP-VLA | Historically important; OpenHelix and RoboDual supersede them as starting points. |
| InternVLA-A1 / Vesta | Strong 2026 Qwen3-VL planners; less turnkey "download and play" than InternVLA-N1. Revisit if N1's nav action space is too narrow. |
| Gemini Robotics / π0.5 paper hierarchy | Closed or unreleased pieces. Architecture references only. |
| Anything 27B+ "because Gemma 27B is smart" | Violates criterion 1 with no dual-system payoff. Use it as a night-time critic at most. |
