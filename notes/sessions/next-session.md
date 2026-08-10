# Next session — pick up here

Rolling handoff for the Phase-B iteration-0 build. Overwrite it at the end of a
session; it describes **one** state, not a history. Last written **2026-08-10**,
end of session `479dabc0-9d72-4866-ba1c-8fbed01cfc32`.

Read this, then the root `CLAUDE.md`, then `research/CLAUDE.md`, then the brief
for whichever role you are working as.

## Where the code stands

`affirmatrix` branch `tool` at **ba34c5c**. Working tree clean. **210 tests
pass, ruff clean, all four documents build.**

Iteration-0 backlog **B0–B10 are done** (`doc/manual/explanation/architecture/iteration-0-backlog.rst`):

| Landed | Module | Backlog |
|---|---|---|
| canonical byte encoding, SHA-256 | `_hashing.py` | B1 |
| node hash, two-sided edge hash, flat-sealed design root | `commitment/` | B2–B4 |
| record vocabulary, record-source protocol, hex conversion | `records/` | B5 |
| built-in graph type | `taxonomy/` | B6 |
| assembly, refusals, refines-acyclicity gate | `graph/` | B7–B8 |
| would-be store + loader | `sources/store.py`, `tests/fixtures/would_be_store/` | B9 |
| affirmation store **write face**, schemas, context, IRI minting | `case/`, `identity.py` | B10 |

The project now has its **first runtime dependencies**: `jsonschema` +
`referencing` (schema validation on write, SEG-SREQ-019). Installed with
`uv pip install --python .venv` — the repo carries no `uv.lock`, deliberately
not introduced in passing.

Still docstring-only stubs: `affirmation/`, `cli/`, `config/`, `drift/`,
`gates/`, `proof/`, `satisfaction/`, `sources/{content,outcomes,reqs}.py`,
`diagnostics.py`. The docstrings are binding design; read the stub before
implementing it.

## Start here: B11

**Read-back as a record source** — the affirmation store's read face,
SEG-SYS-007, and the pass that verifies SEG-SREQ-020 (records read back as
written). The read face conforms to the `records.RecordSource` protocol with
role **recorded** (ADR-0004): persisted edge records re-enter the engine
carrying their stored edge hash and link state, so drift detection (B13) can
compare them against a *current* stream. Sequencing: **B10 → B11 → B13**, and
an operator affirms between B14 and B15.

What B11 inherits from B10, already decided and built:

- Per-kind JSON-LD collection documents (`{"@context": "../context.jsonld",
  "@graph": [...]}`), entries sorted by `id`, absolute IRIs minted by
  `identity`, digests as bare lowercase hex (`records.digest_from_hex` exists
  and is tested).
- The case validates against **its own** `{root}/schema/` copy; the packaged
  copy only seeds an empty root and never overwrites.
- A review event's source revisions live under `seg:fromRevision` /
  `seg:toRevision` — distinct from the identifier-valued `seg:from`/`seg:to`
  terms; a suite invariant test enforces that identifier-valued terms only
  ever hold IRIs.
- `AffirmationStore` is the write face in `case/__init__.py`; the read face
  joins it there (the stub docstring already binds both).

## Verify with these exact commands

Always cap memory on pytest. A runaway test OOMed the machine once, and it took
a session with it — the cap turns that into a killed process.

```console
$ cd affirmatrix
$ (ulimit -v 1048576; timeout 300 .venv/bin/python -m pytest -q) && .venv/bin/ruff check .
$ .venv/bin/python -m doc build          # serve: … -m doc serve -p 8881
```

## Git state — read before touching a branch

**Never push.** Pushing is the human's job; do not ask.

| Worktree | At | Note |
|---|---|---|
| `affirmatrix` (`tool`) | ba34c5c | **ahead 5, behind 1** of `origin/tool` |
| `research` | (this commit) | ahead of `origin/research` |
| `affirmatrix/case` | acc8ebf | still empty — B10 tests use tmp roots only; the real case waits for an FSM-operated bootstrap |
| `tutorials` | b0b4dc2 | **needs rebase**, see below |

Two snags to hand to the human rather than fix (unchanged since 2026-08-06):

1. **`tool` has diverged, not merely advanced.** Local `554b5e8` and remote
   `4f46c4a` carry the same commit message — the remote holds a version that
   was rewritten locally. Resolve at push time.
2. **`tutorials` is no longer a fast-forward.** `b0b4dc2` branched off
   `56fe007`; `tool` has since moved. Rebase-then-fast-forward while no role
   agent is mid-edit, then remove the worktree.

The four-stream conformance-fixture branches (`reqs impl results graph`) remain
in the bare repo, unmounted.

## What this session did

B10, coordinator-driven: work order drafted and FSM-ratified
(`development/notes/b10_swe_work_order.md` — three rulings: schemas live in
`case/schema/` seeded from package data; per-kind collection documents are the
atomicity unit; `context.jsonld` ships with the store, the config files do
not). An SWE subagent ran report → ratify → apply; the FSM's code review
caught one defect (revision strings under identifier-valued JSON-LD terms),
fixed as `seg:fromRevision`/`seg:toRevision` before commit. Landed as
`ba34c5c` on `tool`: `case/` write face (five modules), 14 draft-2020-12
schemas + shared context as package data, `identity` IRI minting, `records`
hex conversion, 64 new tests, architecture note
(`affirmation-store-write-face.rst`).

Five requirement gaps surfaced and parked per cardinal rule 3 —
**`development/notes/re_notes_from_b10.md`** is the RE's next work-order
input. Notable: G15 (per-content-hash source location in `NodeRecord`)
carries an FSM ruling already; G9 (a current stream handed to `write_edges`
would silently reset every affirmation) is the sharpest.

## Open, and not this session's to close

- **The RE notes above** — G3 (ReviewEvent role), G6 (identifier-base /
  `config.json` vs `affirmatrix.yaml`), G8 (snapshotId colons vs Windows),
  G9 (bulk-reset guard), G15 (source location per content hash, ruled).
- **`pyproject.toml` ownership** — now live, not theoretical: B10 edited it
  under one-time FSM authorization.
- **DEC-032 consequence 4** deferred: the content extractor reads `:test-id:`;
  lands with the extractor, past iteration 0.
- **`SEG-TS-nnn` in the fixture is fixture-local**; the real test-specification
  document and the TE's verification suite (`tests/specification/`) remain
  unstarted.

## Rules that catch people out

From the root `CLAUDE.md` — the full set is there, these are the ones that bite:

- **One editor at a time.** At most one role agent in a file-editing phase;
  everyone else is report-only until the editing pass is committed.
- **Self-contained history.** Commit messages and code comments in
  `affirmatrix/` must tell their story from that repository alone — no role
  acronyms, no `DEC-nnn`/`AC-nnn`/`G-nn` (those live here, in the research
  workspace). In-repo anchors (`ADR-000N`, `SEG-SYS`/`SREQ`/`TS` IDs) are fine.
- **Affirmation and proof generation are the human's alone.** Agents never
  affirm a pending or suspect edge.
- **Checkpoint discipline.** One step, then ⏸ and wait.
- **Don't invent design.** Derive from the binding docs and the stub
  docstrings; ask when unclear. Gaps become requirements, not ad-hoc code.
- **Never write to `affirmatrix/case/`** from code or tests — store files
  reach it only through an FSM-operated run; commits there are store acts,
  human-enacted, no co-author trailers.
