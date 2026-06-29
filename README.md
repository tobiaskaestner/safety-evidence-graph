# `b-impl/` — branch `impl` (repo **B**, implementation + test specs)

Part of the SEG Phase-B workspace (DEC-002): one bare repo, four long-lived
branches checked out as worktrees that **never merge** into each other. This is
an **orphan branch** — disjoint history from the others by design, giving it an
independent SHA (`repoBSha` in the EvidenceManifest).

- **Repo key:** `repoB` (in `seg.yaml`)
- **Write-owners:** Software Engineer (`src/seg/`) and Test Engineer (`tests/`),
  worked **sequentially** — never two agents at once in this worktree.
- **Holds:** `src/seg/` (the `seg` tool), `tests/`, `doc/design/`,
  `doc/testspec/`.

The development-binding decision-log slice (DEC-001…006) is to live here under
the one-home model — promotion pending (see workspace setup notes).
