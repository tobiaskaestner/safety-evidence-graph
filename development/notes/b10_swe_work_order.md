# B10 work order — SWE pass

> **Mechanics:** load `re_agent_brief.md`'s sibling `swe_agent_brief.md` into a
> fresh session at the workspace root; this order scopes the pass. The SWE is
> the sole editor for its duration (one editor at a time). Drafted 2026-08-10;
> ratified by the FSM before launch.

## The item

**B10 — Persist nodes, edges, events, proofs; validate on write** — the
affirmation store's write face (SEG-SYS-007), iteration-0 backlog
(`doc/manual/explanation/architecture/iteration-0-backlog.rst`).

Target module: `src/affirmatrix/case/` — currently a docstring-only stub, and
the docstring is binding design. Read it first.

**Out of scope:** the read face (B11) — read-back as a record source lands in
the next pass. Design for it (the docstring already binds the read face to the
record-source protocol), but do not build it. SEG-SREQ-020 (records read back
as written) is therefore verified in B11; the other store requirements are
this pass's.

## Requirements this pass realizes

From `doc/requirement-specification/affirmation-store.rst`:

- **SEG-SREQ-018** — covered content is never persisted
- **SEG-SREQ-019** — only valid records are written (schema-reject, not write)
- **SEG-SREQ-021** — writes stay under the write root
- **SEG-SREQ-022** — records appear only when complete (temp file + rename,
  per ADR-0008)
- **SEG-SREQ-023** — deletion is explicit; a truncated input set must never
  silently prune the case
- **SEG-SREQ-033** — persisted affirmations change only on request

Implementation functions carry `:implements:` markers for the requirement they
realize; unit tests go in `tests/unit/`, test-first.

## Binding design, in reading order

1. `src/affirmatrix/case/__init__.py` — the stub docstring (write policy,
   layering, naming rationale).
2. **ADR-0008** (write policy): all writes land in place in the working
   `case/` by default; `--output-dir` relocates the whole root; the store is
   the **only** writer and owns layout (`nodes/`, `edges/`, `events/`,
   `proofs/{snapshotId}/`), file naming, and schema validation on write;
   per-file atomicity; no implicit deletion; **the tool never runs git**.
3. **ADR-0009**, Stage 1: the tool writes files and knows nothing of git.
   Commits on the `case` lineage are store acts, human-enacted only.
4. **ADR-0007**: record identifiers are case-local and stable (they enter hash
   preimages); **absolute IRIs are minted at serialization time** — the store
   is where that minting happens.
5. **ADR-0004**: layering — the store imports the record vocabulary
   (`affirmatrix.records`: `NodeRecord`, `EdgeRecord`, `ReviewEvent`), never
   the components that compute records.
6. The design summary (research workspace,
   `development/design/knowledge_graph_design_summary.md`) §8: per-kind
   JSON-LD instance documents (`nodes/requirements.jsonld`,
   `edges/refines.jsonld`, `events/review_events.jsonld`), `context.jsonld`,
   draft 2020-12 schemas, absolute-IRI conventions (§8.4).

## Deliverables

1. The write face in `src/affirmatrix/case/`: a store constructed over a write
   root, persisting node records, edge records, and review events; schema
   validation on write; atomic per-file writes; explicit-only removal.
2. For **proofs**: the mechanism only — the `proofs/{snapshotId}/` write path
   through the same validated, atomic, root-confined channel. The four proof
   document types arrive with B16–B17 and their schemas join then (the records
   docstring already anticipates this).
3. JSON Schemas (draft 2020-12) for the three record kinds, carried as
   package data and emitted into the write root's `schema/`, plus
   `context.jsonld` emitted the same way (rulings 1 and 3 below).
4. Unit tests, written first, exercising every SREQ above — including the
   refusal behaviors (invalid record rejected before any byte lands; a write
   root escape attempt refused; interrupted write leaves no readable record).
5. Green gate: memory-capped pytest, ruff, doc build.

**Tests use `tmp_path` write roots, never the real `affirmatrix/case/`
worktree.** The real case stays empty until the FSM operates a bootstrap at a
checkpoint; nothing in the suite may write to it.

## Rulings (FSM, 2026-08-10) — settled before launch

1. **Schemas: `case/schema/` is the authoritative home.** *Coordinator's
   interpretation, to be confirmed at the report checkpoint:* the package
   carries the source copy (package data under `src/affirmatrix/case/`) so a
   fresh clone validates with no case worktree, and the store emits that copy
   into the write root's `schema/` so the case is self-describing — an
   auditor verifies against the copy in the case, never against an installed
   package. Committing the emitted schemas to the lineage is a store act,
   human-enacted.
2. **Per-kind collection documents, confirmed** (`nodes/requirements.jsonld`,
   `edges/refines.jsonld`, `events/review_events.jsonld`, …). Atomicity under
   ADR-0008 therefore means rewriting the whole document to a temp file and
   renaming into place; a record "appears" when its document does.
3. **`context.jsonld` is in B10; the config files are not.** The store emits
   `context.jsonld` alongside the schemas — its own instance documents
   reference it. `config.json` and `config/fsm_authorised_committers.yaml`
   are maintainer-authored inputs, not store writes: the committers list
   joins when verification lands, and how `config.json` reconciles with
   `affirmatrix.yaml` in the mono-repo is a gap to flag as a note to the RE,
   not to solve in this pass.

## Process

- Checkpoint script: orient, report the implementation plan **⏸** → FSM
  ratifies (confirming the interpretation under ruling 1) → tests +
  implementation **⏸** → verify with the exact commands below → commit on
  `tool`.
- Commit message tells its story from the repository alone: in-repo anchors
  (ADR-000N, SEG-SREQ-nnn) fine; no DEC-nnn, no role acronyms.
- **Never push.** Never affirm. Never run git in or against `case/`.

```console
$ cd affirmatrix
$ (ulimit -v 1048576; timeout 300 .venv/bin/python -m pytest -q) && .venv/bin/ruff check .
$ .venv/bin/python -m doc build
```
