# CLAUDE.md — SEG (Safety Evidence Graph)

Shared context for **every** agent in this repository. Your specific role, scope,
and the worktree you work in are defined in **your brief** (you were pointed to it
on launch). This file is the common baseline: read it, then your brief, then the
binding docs. Keep this file lean — detail lives in the docs it points to.

## What this is

SEG (the **SEG Toolbox**) binds safety requirements, tests, and code into a
hash-anchored graph and generates an integrity proof over it. Long-term goal:
**self-hosting** — SEG generates an integrity proof of itself.

A second pillar has since grown out of the core: **composing safety cases across a
supply chain**. A case is a vector of per-component assume-guarantee contracts
(DEC-010, DEC-019) under a flat-openable commitment (DEC-012/020), projected to an
SPDX 3.x FunctionalSafety (FuSa) JSON-LD BOM and re-imported downstream. The
roll-up verdict is **never carried in a BOM** — each consumer recomputes it (the
thesis). See DEC-017…028 for the exchange model and `research/notes/seg_spdx_fusa_handoff.md`.

The repo follows a **four-stage maturity pipeline** — funnel → research →
prototype → development — mapped in `notes/seg_pipeline_model.md`:
- **`funnel/`** — raw idea exploration (currently empty).
- **`research/`** — general-grounds conclusions + self-contained prototypes
  (throwaway, inputs mocked): `research/prototypes/spdx-v3.1-exchange/` (the
  three-party FuSa round-trip), `research/prototypes/demos/` + `examples/` (clingo
  verdict/composition proofs, DSL), and `research/notes/` (design drafts, prior art).
- **`prototype/`** — `prototype/graph-construction/`, the original SEG prototype
  (graph/coverage/suspect workflows). Does not use the worktree topology below.
- **`development/`** (**Phase B**) — the real `seg` tool, built test-first across the
  worktrees below; design-of-record in `development/design/`.

## Workspace (Phase B)

One repo, four long-lived branches as worktrees; they never merge into each other
(DEC-002):

| Worktree | Branch | Holds |
|---|---|---|
| `reqs/`    | A | `doc/requirements/` (sphinx-needs) — Requirement nodes |
| `impl/`    | B | `src/seg/`, `tests/`, `doc/design/`, `doc/testspec/` |
| `results/` | C | raw pytest artifacts, `doc/testreport/` |
| `graph/`   | G | `nodes/ edges/ events/ proofs/ config/ schema/`, `context.jsonld` |

`seg.yaml` sits at the workspace root (untracked) and points `repoA…repoG` at the
worktrees. `impl/` is co-owned by the Software and Test Engineers (SWE: `src/seg/`;
TE: `tests/`), worked **sequentially** — never two agents at once in one worktree.

## Binding documents — cite by ID

Core design & engine:
- **The SEG design summary** (`development/design/knowledge_graph_design_summary.md`)
  — design of record (concept + C-oriented reference).
- **The decision log** — split into stage slices, indexed at
  **`notes/decision_log_index.md`**: `development/notes/decision_log.md` (core-engine
  DEC-001…006) and `research/notes/decision_log.md` (composability/direction
  DEC-007…028). DEC-011 vacant; DEC-IDs stable and globally unique. The citeable
  *why*; the record of record.
- **`development/design/seg_architecture_constraints.md`** — engine structural
  constraints **AC-001…016** (tagged `[now]` / `[seam]` / `[future]`).
- **`development/design/seg_python_realization.md`** — the Python / single-repo binding.

Composability & SPDX exchange:
- **`research/notes/seg_composability_cbd.md`** — assume-guarantee composition,
  contract algebra, the verdict ruleset realization.
- **`research/notes/seg_definition_language.md`** — the SEG DSL.
- **`development/design/seg_cli_reference.md`** — CLI surface;
  **`research/notes/seg_adr_projection_core.md`** — ADR/projection core.
- **`research/notes/GAPS.md`** — idealization ledger (prototype simplifications);
  **`notes/seg_glossary.md`** — terms.

## Skills

Follow the relevant skill: **python-patterns** (`.claude/skills/`, all engine/
extractor code), **seg-requirements-authoring** (`skills/SKILL.md`, requirements).

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

Core graph:
- The graph stores **only hashes**, never content — content lives in the versioned
  source repos and is fetched transiently when needed (AC-005).
- Content hashes are over **raw source byte spans**; the parser only *locates*
  spans, never feeds the hash (DEC-003 / AC-004).
- The engine **builds** proof-generation and affirmation but never **operates** them
  as authority — the FSM does (AC-006).
- Transitive suspicion is derived, and auto-clears on descendant re-affirmation
  (DEC-005 / AC-010).
- Isolate the variable parts behind seams: taxonomy, satisfaction, input adapters,
  interfaces, repo topology (AC-001/002/003/014/015) — so the meta-model (DEC-007)
  and future interfaces (DEC-008 REST) plug in rather than force a rewrite.
- IDs: `SEG-SYS-nnn` (system), `SEG-SREQ-nnn` (software), `SEG-TS-nnn` (test spec).
  Markers are docstring fields `:implements:` / `:verifies:` (no runtime behaviour).

Composability & exchange:
- A contract opens to **`(G, A, I)`** — guarantee, assumption down-closure, and
  the implementation pin (the set of implementations under `G`, content-ref'd).
  Members are bound under a **flat set-commitment** seal (deep aggregation retired,
  DEC-012); dropping an assumption *or* swapping an implementation breaks the seal
  (DEC-019/020/028). v1 keeps a flat-sealed design root as its seal — no signature,
  per-node `merkleHash` dropped (DEC-013/014).
- The reliance edge is **`covers`** (Guarantee → Requirement), **derived** not
  hard-coded; `conformsTo` is a verdict-inert producer declaration resolved to
  `covers` only on import under the sealed manifest (DEC-017/024).
- An undischarged inherited condition is `unsatisfied`, not residual (DEC-015);
  `forward` re-publishes it as an affirmation-gated, verdict-conditional
  `condition_of_use` (DEC-022); a compliant-item supplier discharges it via an
  affirmed `covers`, gated by a document-root (version-pin) compatibility check
  (DEC-023).
- Entities/roles: {manufacturer, assessor, item provider} × {supplier, integrator,
  verifier}; verification is universal self-verification (DEC-025). The assessor
  certificate is a signature over `(hash(case), BOM)`; case and Safety BOM are
  distinct documents (DEC-026).

## Getting started

Open your brief, then the binding docs. If unsure which worktree you're in, match
your working directory to the table above.
