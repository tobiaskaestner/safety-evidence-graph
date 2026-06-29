# `g-graph/` — branch `graph` (repo **G**, graph state)

Part of the SEG Phase-B workspace (DEC-002): one bare repo, four long-lived
branches checked out as worktrees that **never merge** into each other. This is
an **orphan branch** — disjoint history from the others by design, giving it an
independent SHA (`repoGSha` in the EvidenceManifest).

- **Repo key:** `repoG` (in `seg.yaml`)
- **Write-owner:** the FSM (the human) — affirmation and proof generation are
  the FSM's alone; agents never affirm edges.
- **Holds:** `nodes/ edges/ events/ proofs/ config/ schema/`, `context.jsonld`.
  The graph stores **only hashes**, never content (AC-005).

The design's repo-G `sync`/`main` split is collapsed into this single G branch;
link states are refreshed by running the sync/extraction step manually.
