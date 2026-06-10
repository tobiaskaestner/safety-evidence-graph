# CLAUDE.md — SEG (Safety Evidence Graph)

Shared context for **every** agent in this repository. Your specific role, scope,
and the worktree you work in are defined in **your brief** (you were pointed to it
on launch). This file is the common baseline: read it, then your brief, then the
binding docs. Keep this file lean — detail lives in the docs it points to.

## What this is

SEG (the **SEG Toolbox**) binds safety requirements, tests, and code into a
hash-anchored graph and generates an integrity proof over it. Long-term goal:
**self-hosting** — SEG generates an integrity proof of itself.

Two phases:
- **Phase A — prototype** (`prototype/`, throwaway, all inputs mocked): de-risks
  the graph workflows. Does not use the worktree topology below.
- **Phase B — implementation**: the real `seg` tool, built test-first across the
  worktrees below.

## Workspace (Phase B)

One repo, four long-lived branches as worktrees; they never merge into each other:

| Worktree | Branch | Holds |
|---|---|---|
| `reqs/`    | A | `doc/requirements/` (sphinx-needs) — Requirement nodes |
| `impl/`    | B | `src/seg/`, `tests/`, `doc/design/`, `doc/testspec/` |
| `results/` | C | raw pytest artifacts, `doc/testreport/` |
| `graph/`   | G | `nodes/ edges/ events/ proofs/ config/ schema/`, `context.jsonld` |

`seg.yaml` sits at the workspace root (untracked) and points `repoA…repoG` at the
worktrees. `impl/` is co-owned by the Software and Test Engineers (SWE: `src/seg/`;
TE: `tests/`), worked **sequentially** — never two agents at once in one worktree.

## Binding documents (`.claude/plans/`) — cite by ID

- **The SEG design summary** (`knowledge_graph_design_summary_v4.x.md`) — design of
  record (concept + C-oriented reference).
- **`seg_decision_log.md`** — locked decisions DEC-001…008; the authoritative *why*.
- **`seg_architecture_constraints.md`** — engine structural constraints AC-001…014.
- **`seg_python_realization.md`** — the Python / single-repo binding.

## Skills (`.claude/skills/`)

Follow the relevant skill: **python-pattern** (all engine/extractor code),
**seg-requirements-authoring** (requirements).

## Cardinal rules (everyone, always)

1. **Don't invent design.** If intent is unclear, ask. Derive from the binding
   docs; never freelance design.
2. **Stay in scope.** Scope is the agreed iteration backlog — nothing more. If
   asked for something outside it, push back or flag it before proceeding.
3. **Gaps become requirements, not code.** Hit a gap, ambiguity, or loophole →
   write a note to the RE. Requirements lead code; don't patch it ad hoc.
4. **Affirmation is the FSM's alone.** Agents **never** affirm pending/suspect
   edges. The FSM (the human) operates affirmation and proof generation.
5. **Stay in your worktree.** Write only within the branch your brief owns.
6. **Checkpoint discipline.** Work your brief's action plan one step at a time;
   stop at each ⏸ and wait for the human.

## Invariants worth knowing (detail in the docs)

- The graph stores **only hashes**, never content — content lives in the versioned
  source repos and is fetched transiently when needed.
- Content hashes are over **raw source byte spans**; the parser only *locates*
  spans, never feeds the hash (DEC-003 / AC-004).
- The engine **builds** proof-generation and affirmation but never **operates** them
  as authority — the FSM does (AC-006).
- Isolate the variable parts behind seams: taxonomy, satisfaction, input adapters,
  and interfaces (AC-001/002/003/014) — so the meta-model and future interfaces
  plug in rather than force a rewrite.
- IDs: `SEG-SYS-nnn` (system), `SEG-SREQ-nnn` (software), `SEG-TS-nnn` (test spec).
  Markers are docstring fields `:implements:` / `:verifies:` (no runtime behaviour).

## Getting started

Open your brief, then the binding docs. If unsure which worktree you're in, match
your working directory to the table above.
