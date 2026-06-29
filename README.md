# `reqs/` — branch `a-reqs` (repo **A**, requirements)

Part of the SEG Phase-B workspace (DEC-002): one bare repo, four long-lived
branches checked out as worktrees that **never merge** into each other. This is
an **orphan branch** — disjoint history from the others by design, giving it an
independent SHA (`repoASha` in the EvidenceManifest).

- **Repo key:** `repoA` (in `seg.yaml`)
- **Write-owner:** Requirements Engineer (RE)
- **Holds:** `doc/requirements/` — sphinx-needs Requirement nodes
  (IDs `SEG-SYS-nnn` system, `SEG-SREQ-nnn` software).

Requirements lead code: edits here trigger re-affirmation, not a test re-run.
