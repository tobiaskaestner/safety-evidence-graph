# `results/` — branch `c-results` (repo **C**, test outcomes)

Part of the SEG Phase-B workspace (DEC-002): one bare repo, four long-lived
branches checked out as worktrees that **never merge** into each other. This is
an **orphan branch** — disjoint history from the others by design, giving it an
independent SHA (`repoCSha` in the EvidenceManifest).

- **Repo key:** `repoC` (in `seg.yaml`)
- **Write-owner:** the outcome-extraction step (run by the FSM at checkpoints;
  no CI per DEC-002).
- **Holds:** raw pytest result artifacts — the input to the test-outcome
  extractor.

Kept off branch B so a requirement or code edit doesn't churn results.
