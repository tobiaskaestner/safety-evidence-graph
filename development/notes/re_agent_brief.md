# Requirements Engineer Agent Brief — affirmatrix

> **Mechanics:** load this brief into a fresh Claude Code session started in the
> `affirmatrix/` worktree (branch `tool`). Revised 2026-07-24 for DEC-029 (name)
> and DEC-030 (mono-repo); supersedes the worktree-era brief.

## Mandate

**affirmatrix** is the tool we are building (DEC-029; it manages *safety
evidence graphs* — "SEG" in the design record), and we intend it to eventually
generate an integrity proof **of itself**. Your job: author the **requirements
for the affirmatrix tool**, as sphinx-needs, so the Software Engineer can
implement against them and the Test Engineer can verify them. These
requirements are the contract the rest of the team builds on.

Source material — derive requirements from these, do not invent design:
the SEG design summary (`development/design/knowledge_graph_design_summary.md`
in the research workspace) and `notes/decision_log_index.md` (DEC-001…030; the
commitment layer follows DEC-012/014 — flat-sealed root, no per-node Merkle).
Where intent is unclear, ask.

## Workspace & path scope

You work in the mono-repo (`affirmatrix/`, branch `tool`). **Edit only within
`doc/requirement-specification/`** — that is your path scope (DEC-030 replaced
branch ownership with path ownership). The documentation federation is already
scaffolded: registry (`doc/documents.yaml`), shared typed-needs config
(`doc/needs_config.toml`, `doc/schemas.json`), build via `python -m doc build`.
The shared federation config is common infrastructure — propose changes at
checkpoints, don't unilaterally edit.

Your document builds to
`build/doc/deploy/requirement-specification/html/needs.json` — that file is
what the affirmatrix requirements reader will consume.

**Seed triage.** The document currently contains bootstrap fixtures
(`SEG-SYS-001`, `SEG-SREQ-001/002`) written to verify the federation plumbing —
they are **not ratified requirements**. Author your slice fresh; retire or
replace the seeds as part of it. Coordinate: the test-specification document's
seed needs (`SEG-TS-001/002`) link to the seed SREQs — flag the TE handoff when
you renumber.

## Scope of this first slice

**One system requirement plus 3–4 software requirements that refine it**, on
the **hashing + graph-build core** — the foundational behaviour (compute stable
content hashes over raw byte spans, derive node/edge hashes and the flat-sealed
root, build the graph from nodes and references). This is a deliberately small
**complete subtree**, not the whole tool. Later slices extend it iteration by
iteration.

Do not author requirements for areas beyond this slice yet (proof generation,
gates, suspect detection, extractors, CLI, composition/exchange) — they come in
later iterations.

## Rules

- **ID scheme:** `SEG-SYS-nnn` for system requirements, `SEG-SREQ-nnn` for
  software requirements. IDs are stable and permanent once issued — SWE/TE will
  reference them in `:implements:` / `:verifies:` markers. (The artifact keeps
  the SEG prefix by design — DEC-029.)
- **Decomposition:** the slice is a `refines` tree — software requirements
  refine the system requirement (child → parent). `refines` must be acyclic
  (DEC-001).
- **Leaf rule (DEC-001):** the software requirements are leaves; each must be
  concrete enough to be directly implemented and tested (≥1 implementation and
  ≥1 test will eventually attach). The system requirement is a non-leaf,
  covered transitively by its children — it carries no direct
  implementation/test.
- Keep each requirement **atomic, testable, and implementation-agnostic**
  (state *what*, not *how*). One verifiable claim per software requirement.
- **Reproducible export:** ensure `needs_reproducible_json = True` is set in
  the shared config (propose the change at your first checkpoint — it is not
  yet set) so `needs.json` is stable across builds.
- Follow the **seg-requirements-authoring skill** (research workspace,
  `skills/SKILL.md`) for phrasing conventions.

## Deliverable

- The first ratified slice: 1 `SEG-SYS-nnn` + 3–4 `SEG-SREQ-nnn`, with
  `refines` links, replacing the bootstrap seeds.
- A green `python -m doc build` producing well-formed, reproducible
  `needs.json`.

## Non-goals

- No implementation, no tests, no code markers — requirements only.
- No requirements outside the hashing + graph-build slice.
- No edits outside `doc/requirement-specification/` (shared config by proposal
  only).

## Collaborative action plan (checkpoint script)

Work one step at a time. At each **⏸ PAUSE**, stop and wait for the human to
review and decide before continuing.

1. **Orient.** Read the design summary + DEC-001…030 index; inspect the
   federation and the seed fixtures; propose the `needs_reproducible_json`
   config change and the seed-retirement plan. **⏸** Human reviews the
   orientation and the plan.
2. **Draft the system requirement** (`SEG-SYS-nnn`) for the hashing +
   graph-build core — the single top-level claim this slice establishes. **⏸**
   Human reviews and approves the system requirement *before* it is decomposed.
3. **Decompose** into 3–4 `SEG-SREQ-nnn` software requirements that `refine`
   it, each atomic and testable. **⏸** Human reviews the decomposition
   (coverage, atomicity, IDs) and may adjust.
4. **Build** and confirm `needs.json` is produced, well-formed, and
   reproducible; seeds retired; TE handoff note written (which TS links need
   re-pointing). **⏸** Human reviews the final slice and signs off as the
   contract for SWE/TE.
