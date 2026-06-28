# `development/` — the real `seg` tool (Phase B)

The final stage of the [maturity pipeline](../notes/seg_pipeline_model.md): design
elements have matured enough to drive a **proper, test-first software-engineering
activity** — the actual `seg` tool.

| Path | What lives there |
|---|---|
| [`design/`](design/) | Design of record: [`knowledge_graph_design_summary.md`](design/knowledge_graph_design_summary.md) (concept + C reference), [`seg_architecture_constraints.md`](design/seg_architecture_constraints.md) (AC-001…016), [`seg_python_realization.md`](design/seg_python_realization.md) (single-repo Python binding), [`seg_cli_reference.md`](design/seg_cli_reference.md). |
| [`notes/`](notes/) | The core-engine decision-log slice and the RE/SWE agent briefs. |

## Workspace topology

Phase B is **one repo, four long-lived branches as worktrees** that never merge into
each other (DEC-002). `seg.yaml` at the workspace root (untracked) points `repoA…repoG`
at them:

| Worktree | Branch | Holds |
|---|---|---|
| `reqs/`    | A | `doc/requirements/` (sphinx-needs) — Requirement nodes |
| `impl/`    | B | `src/seg/`, `tests/`, `doc/design/`, `doc/testspec/` |
| `results/` | C | raw pytest artifacts, `doc/testreport/` |
| `graph/`   | G | `nodes/ edges/ events/ proofs/ config/ schema/`, `context.jsonld` |

These worktrees are separate checkouts and do not appear in this branch's tree.
See [`CLAUDE.md`](../CLAUDE.md) for the full workspace description.
