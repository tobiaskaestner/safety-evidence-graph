# SEG — Safety Evidence Graph

SEG binds safety **requirements, tests, and code** into a hash-anchored graph and
generates an **integrity proof** over it; the long-term goal is **self-hosting** (SEG
proves itself). A second pillar composes **safety cases across a supply chain**: a case
is a vector of per-component assume-guarantee contracts under a flat-openable
commitment, projected to an SPDX 3.x FunctionalSafety (FuSa) JSON-LD BOM and
re-imported downstream — where each consumer **recomputes** the verdict rather than
trusting one carried in the BOM.

## Maturity pipeline

Work flows through four stages, each gaining commitment and losing generality
(`notes/seg_pipeline_model.md`):

**`funnel/` → `research/` → `prototype/` → `development/`**

| Folder | What lives there |
|---|---|
| [`funnel/`](funnel/) | Raw idea exploration (intentionally empty at this stage). |
| [`research/`](research/) | General-grounds conclusions + self-contained, throwaway prototypes (SPDX FuSa round-trip, clingo/SHACL demos, the DSL) and design notes. |
| [`prototype/`](prototype/) | The SEG prototype — quick-feedback additions, not yet true software engineering. |
| [`development/`](development/) | Phase B: the real `seg` tool, built test-first across four worktrees; design-of-record. |
| [`notes/`](notes/) | Cross-cutting record: glossary, decision-log index, pipeline model, session history. |

## Start here

- **Agents:** read [`CLAUDE.md`](CLAUDE.md) first — it is the shared baseline (workspace,
  binding documents, cardinal rules), then your brief.
- **Decisions of record:** [`notes/decision_log_index.md`](notes/decision_log_index.md)
  (DEC-001…028) indexes the core-engine and composability decision-log slices.
- **Design of record:** [`development/design/knowledge_graph_design_summary.md`](development/design/knowledge_graph_design_summary.md)
  and the constraints in [`development/design/seg_architecture_constraints.md`](development/design/seg_architecture_constraints.md).
- **Requirements-authoring skill:** [`skills/SKILL.md`](skills/SKILL.md).
