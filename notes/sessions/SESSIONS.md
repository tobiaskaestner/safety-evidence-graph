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

## Conventions

- **Status**: `active` (current work) · `paused` (will return) · `archived` (done/reference) · `stub` (abandoned early).
- When a thread produces durable conclusions, create `notes/sessions/<topic>.md` and link it in the last column.
- Session transcripts live at `~/.claude/projects/-wrk-z-ws-safety-safety-evidence-graph/<id>.jsonl`.
