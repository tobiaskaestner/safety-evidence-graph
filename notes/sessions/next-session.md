# Next session — pick up here

Rolling handoff for the Phase-B iteration-0 build. Overwrite it at the end of a
session; it describes **one** state, not a history. Last written **2026-08-06**,
end of session `6a5cb5f0-d771-4892-9d48-10c6e0988e98`.

Read this, then the root `CLAUDE.md`, then `research/CLAUDE.md`, then the brief
for whichever role you are working as.

## Where the code stands

`affirmatrix` branch `tool` at **817e2af**. Working tree clean. **146 tests
pass, ruff clean, all four documents build.**

Iteration-0 backlog **B0–B9 are done** (`doc/manual/explanation/architecture/iteration-0-backlog.rst`):

| Landed | Module | Backlog |
|---|---|---|
| canonical byte encoding, SHA-256 | `_hashing.py` | B1 |
| node hash, two-sided edge hash, flat-sealed design root | `commitment/` | B2–B4 |
| record vocabulary, record-source protocol | `records/` | B5 |
| built-in graph type | `taxonomy/` | B6 |
| assembly, refusals, refines-acyclicity gate | `graph/` | B7–B8 |
| would-be store + loader | `sources/store.py`, `tests/fixtures/would_be_store/` | B9 |

Everything else in `src/affirmatrix/` is a docstring-only stub —
`affirmation/`, `case/`, `cli/`, `config/`, `drift/`, `gates/`, `proof/`,
`satisfaction/`, `sources/{content,outcomes,reqs}.py`, `identity.py`,
`diagnostics.py`. The docstrings are binding design; read the stub before
implementing it.

## Start here: B10

**Persist nodes, edges, events, proofs; validate on write** — affirmation store,
SEG-SYS-007. Two sequencing facts from the backlog's own *Sequencing* section:

- **B10 → B11 → B13.** Drift detection compares the *recorded* stream from the
  affirmation store against the *current* stream from a producer, so read-back
  (B11) must exist before suspicion can be derived (B13).
- **An operator affirms between B14 and B15.** A faithfully bootstrapped store
  starts every edge pending, and a pending edge blocks a package, so the gate
  has nothing to show until a bulk affirmation has happened at a checkpoint.

B9's loader is the *current*-side producer B13 will compare against, and it is
deliberately retired later by record production — do not build on it as if it
were permanent.

**Where B10's output goes:** `affirmatrix/case/`, a worktree of the orphan
`case` branch (ADR-0009). It is at `acc8ebf` and **empty** — the lineage is
initialised, no store files yet. `/case/` is gitignored on `tool`, so store
files can never show up as changes to the code branch. Commits there are store
acts: **human-enacted only, no co-author trailers.** Stage 1 of ADR-0009 is in
force — the tool writes files and knows nothing of git.

Unlike the would-be store, the affirmation store **is** schema-validated: it
holds hashes and references, never content.

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
| `affirmatrix` (`tool`) | 817e2af | **ahead 4, behind 1** of `origin/tool` |
| `research` | ffd5e9d | ahead 1 of `origin/research` |
| `affirmatrix/case` | acc8ebf | empty, awaiting B10 |
| `tutorials` | b0b4dc2 | **needs rebase**, see below |

Two snags to hand to the human rather than fix:

1. **`tool` has diverged, not merely advanced.** Local `554b5e8` and remote
   `4f46c4a` carry the same commit message — the remote holds a version that
   was rewritten locally. That is the "behind 1". It needs resolving at push
   time.
2. **`tutorials` is no longer a fast-forward.** `b0b4dc2` branched off
   `56fe007`, and `tool` has since gained `9e57e79` and `817e2af`, so
   `b0b4dc2` is not an ancestor of `tool`. Per the root `CLAUDE.md` it wants
   rebase-then-fast-forward while no role agent is mid-edit, then the worktree
   is removed.

The four-stream conformance-fixture branches (`reqs impl results graph`) remain
in the bare repo, unmounted, nothing exercising them. Remount with
`git worktree add <dir> <branch>` when integration tests need the topology.

## What this session did

Resumed session `8442f2d0…`, which a host OOM killed. B9 survived uncommitted
on disk, which was lucky: it meant the fixture could land already correct
instead of being committed wrong and patched after, so **no content hash in the
store has ever moved.**

Then the marker correction the human spotted while reading the fixture's
test-specification docstrings. **DEC-032** (`development/notes/decision_log.md`),
refining DEC-003's Python binding:

- `:verifies: SEG-SREQ-nnn` — the **relation**, matching the `Verifies` edge,
  which runs TestSpecification → Requirement.
- `:test-id: SEG-TS-nnn` — the **identity**, the specification a test realizes.
- `:implements: SEG-SREQ-nnn` unchanged, still a single field.

DEC-003 had already given `:verifies:` a requirement as its target; the SWE and
TE briefs had drifted to `:verifies: SEG-TS-nnn` and the fixture inherited the
drift. So DEC-032 restores DEC-003's target and adds the field DEC-003 lacked:
it fixed test identity as a manual `SEG-TS-nnn` "independent of name and
location" but never said how an extractor *learns* it from the code. Tests need
two fields precisely because their identity is not derivable; implementations
need one because the dotted path supplies it.

Commits: `9e57e79` (convention — extractor docstring, ADR-0006), `817e2af`
(B9 — loader, fixture, 29 tests) on `tool`; `ffd5e9d` (DEC-032, index
cross-links, both briefs, `research/CLAUDE.md`) on `research`.

`test_every_realization_marks_the_requirement_its_specification_verifies` in
`tests/unit/test_store_loader.py` holds the nine fixture markers to
`edges/coverage.toml`. It is mutation-checked: restoring the old
`:verifies: SEG-TS-004` fails it. The nine targets were *derived* from
`coverage.toml`, not hand-copied.

## Open, and not this session's to close

- **DEC-032 consequence 4** is deferred: the content extractor must read
  `:test-id:` as TestSpecification identity. Lands with the extractor, past
  iteration 0.
- **`pyproject.toml` has no owner** in any brief — flagged in ADR-0006's
  consequences, still undecided.
- **`SEG-TS-nnn` in the fixture is fixture-local.** The identifiers do not
  correspond to entries in a test specification document, because that document
  does not exist yet. When it does, either the two agree or record production
  has already retired the fixture.
- **Test-specification identity for the real suite** — ADR-0006 gives
  `tests/specification/` to the TE and says those tests carry both markers, but
  no such test exists yet. The verification suite is unstarted.

## Rules that catch people out

From the root `CLAUDE.md` — the full set is there, these are the ones that bite:

- **One editor at a time.** At most one role agent in a file-editing phase;
  everyone else is report-only until the editing pass is committed. Path
  ownership prevents edit conflicts, not working-tree collisions. Sequence:
  ratify → one agent applies → verify → commit → next agent.
- **Self-contained history.** Commit messages and code comments in
  `affirmatrix/` must tell their story from that repository alone — no role
  acronyms, no `DEC-nnn`/`AC-nnn` (those live here, in the research
  workspace), no conversational shorthand. In-repo anchors (`ADR-000N`,
  `SEG-SYS`/`SREQ`/`TS` IDs) are fine. This is why DEC-032 is cited in *this*
  file and in the decision log, but nowhere in `affirmatrix`.
- **Affirmation and proof generation are the human's alone.** Agents never
  affirm a pending or suspect edge.
- **Checkpoint discipline.** One step, then ⏸ and wait.
- **Don't invent design.** Derive from the binding docs and the stub
  docstrings; ask when unclear. Gaps become requirements, not ad-hoc code.
