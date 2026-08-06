# Research Sessions Index

> This is the hand-curated "sidebar" for this repo — one row per research thread.
> Model: **one Claude Code session per topic**.
>
> **To revisit a thread:** `claude --resume <session-id>` (copy the UUID below).
> **To start a new thread:** run `claude` fresh, then add a row here.
> **Lookback shortcut:** prefer the distilled `notes/sessions/<topic>.md` over replaying the
> full transcript — the transcript is the backup, the note is the summary.
>
> Claude keeps this file updated when we start or wrap a thread.
>
> **This index tracks *conversations*, not tasks.** For the open *research work*
> backlog (what's unfinished, where to read), see `research/notes/seg_open_threads.md`.

| Topic | Session ID | Status | Last active | Distilled note |
|---|---|---|---|---|
| Schema test-drive (graph-construction schemas) | `a880b53a-ba65-4bfc-b865-b32e7f5583d4` | archived | 2026-06-08 | [schema-testdrive.md](schema-testdrive.md) |
| Sphinx-Needs route (route-b) | `31cbd57d-577c-4da6-8cff-a9d5844a8aaf` | archived | 2026-06-08 | _none yet_ |
| Sphinx-Needs plan (short) | `8725dbb3-d5da-4080-870a-36cfe83dd792` | stub (19 lines) | 2026-06-08 | _none yet_ |
| Prototype build — graph-construction (Steps 1–7) | `d0826f3d-dc7b-4058-9c86-4edeb47bc598` | archived (large) | 2026-06-25 | [prototype-build.md](prototype-build.md) |
| Web-session access question (stub) | `1b4ad22f-ee7e-4a3d-a084-c0241712a394` | archived | 2026-07-01 | _none yet_ |
| Workflow setup + git history reconciliation | `179da4bc-fd43-43d5-a5cb-58eb2fce0768` | archived (pushed) | 2026-06-26 | [workflow-and-git-reconciliation.md](workflow-and-git-reconciliation.md) |
| Repo migration to the stage pipeline | `bc875929-9fd2-49c6-8bd3-6362d64ee858` | archived | 2026-06-28 | [migration_to_repo.md](migration_to_repo.md) |
| Phase-B workspace bootstrap (bare repo + worktrees) | `7d9b6125-4e29-4d42-af79-697115564b24` | active | 2026-06-29 | [worktree-workspace-bootstrap.md](worktree-workspace-bootstrap.md) |
| Publication — paper-seed reconciliation, two-paper plan (Prague prio); grew into tool landscape WP-1…WP-6 | `e0e116bc-e0f8-49f5-b4a4-e384a3a1d206` | archived (lost, ended clean at 2ff42a4) | 2026-07-04 | _none yet_ |
| Tool landscape/comparison continuation (WP-4 BASIL + consolidation) | `3e8350d4-079d-4a43-8331-2f9ad88d017c` | active | 2026-07-06 | _none yet_ |
| Affirmatrix graph-builder pass — DFS cycle-check fix (OOM leak), memory-capped pytest convention, commits bc1c014/554b5e8 | `8442f2d0-994d-4033-b624-bf5fd4915767` | archived (lost to host OOM; work survived uncommitted, resumed below) | 2026-08-06 | _none yet_ |
| Would-be store + loader (B9); DEC-032 marker split, commits 9e57e79/817e2af | `6a5cb5f0-d771-4892-9d48-10c6e0988e98` | active | 2026-08-06 | [next-session.md](next-session.md) |

## Conventions

- **Status**: `active` (current work) · `paused` (will return) · `archived` (done/reference) · `stub` (abandoned early).
- When a thread produces durable conclusions, create `notes/sessions/<topic>.md` and link it in the last column.
- **`notes/sessions/next-session.md`** is the rolling Phase-B handoff — where the
  build stands and what to pick up next. It describes one state, not a history:
  overwrite it at the end of a session rather than appending to it.
- Session transcripts live at `~/.claude/projects/-wrk-z-ws-safety-safety-evidence-graph/<id>.jsonl`.
