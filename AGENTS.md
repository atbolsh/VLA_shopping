# Agent notes for this repo

This is a shopping notebook for **Vision-Language-Action** models (standard name: VLA; the owner calls them LVA). Address the owner as **you** in human-facing notes. It is meant to be updated as models are pulled and tested.

The parseable human source of truth for Network / Action / World / Paper is `notes/06_option_specs.md`. Card bodies must keep a four-bullet Spec block that matches that file.

## Read first

1. `notes/00_brief.md` — constraints, mapped onto `../stateful_realtime_thinking`.
2. `candidates/index.yaml` — machine-readable shortlist.
3. `candidates/*.md` — one card per model. YAML frontmatter must match `schema/candidate.schema.json`.
4. `notes/02_scorecard.md` — why the scores are what they are.
5. `notes/09_next_session.md` — next window, four looks: JARVIS-VLA → Chameleon/Rynn/WorldVLA (decoder + harness-talk goal) → MolmoAct2 → InternVLA-N1, then sandboxes. Do not start that in a window that only wrote the note.
6. `notes/10_sibling_list.md` — sibling (talk + 3D game) scorecard. Hard filter: policy weights. Not a twelfth shopping card.
7. `notes/08_community_gems.md` — HF community sweep. Do not promote Hub training dumps to cards.
8. `papers/README.md` — what was pulled and why.

## How to add or revise a candidate

1. Copy an existing card in `candidates/`.
2. Fill every required frontmatter field. Scores are 1–5 integers; justify them in the body, not only in the YAML.
3. Add a one-line entry to `candidates/index.yaml`.
4. Add the paper to `papers/README.md` and drop the PDF in `papers/pdfs/` as `<arxiv-id>_<shortname>.pdf` when an arXiv id exists.
5. If the scorecard ranking changes, update `notes/02_scorecard.md` and the canvas data in the managed canvases directory (do not invent a second source of scores).

## Score meanings (do not drift)

| Score | dual | reasoning | size_fit | env_play | cheap_robot | overnight | openness |
|---|---|---|---|---|---|---|---|
| 5 | True dual; S1 sees fresh pixels asynchronously | At or above Gemma 4 12B | Comfortably <10B, 7B-class S2 | Installable 3D env with a documented play loop | Official SO-100/101 (or cheaper) checkpoint | Documented dream/world-model data loop | Open weights, code, data |
| 3 | Near-dual (action expert / chunks) or hierarchical language macros | Usable planner; may lose to 12B | <20B with a clear excuse | Sim exists but is painful | Mid-cost platform (Go2, Franka in lab) | Large public dataset, not a self-loop | Weights open, some gates |
| 1 | Single-system AR VLA | Below the rejected Gemma 4 e4B bar | >>20B or unknown giant | No public env | No robot story | No synthetic-data story | Closed |

`reasoning_vs_gemma4_12b` is the only field allowed to be a qualitative enum (`above` / `near` / `below_ok` / `below_reject` / `unknown`). Llama-2-7B and LLaVA-1.5-7B default to `below_reject` unless a paper shows otherwise.

## Dual-class vocabulary (from OpenHelix + sibling notes)

- `true_async` — S2 slow; S1 fast **and** S1 gets real-time perception, not only an S2 latent.
- `true_embedded` — S1 is the last blocks of the same VLM, still with high-rate extras (FiS).
- `true_hierarchical` — S2 emits temporally-extended language/mid-level commands; a separate high-rate controller executes (NaVILA).
- `near_expert` — VLM + flow/diffusion action expert on shared observations (π0, GR00T N1.7, MolmoAct2). OpenHelix would not call this a true dual system.
- `behavioral_switch` — one net that sometimes reasons and sometimes acts (OneTwoVLA).
- `single` — one forward pass, one action (or action tokens).
- `kit` — recipe to attach an S1 to a stronger S2 the user already has.
- `closed_reference` — architecture ceiling, no weights.

## Do not

- Treat Helix, Gemini Robotics, or π0.5's *paper* hierarchy as pullable.
- Recommend SmolVLA / 2B-class VLMs as the reasoning core. The user already rejected Gemma 4 e4B.
- Invent interactive demos. If there is no hosted playground, say so and point at the local eval.
- Promote a LeRobot auto-upload (`tylergp/molmoact2-*`, unnamed `*so101*` LoRAs) to a candidate card. Those are training dumps. The community sweep lives in `notes/08_community_gems.md`.
