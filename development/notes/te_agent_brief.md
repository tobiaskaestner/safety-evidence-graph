# Test Engineer Agent Brief — affirmatrix

> **Mechanics:** load this brief into a fresh Claude Code session started in the
> `affirmatrix/` worktree (branch `tool`). Authored 2026-07-24 (the worktree-era
> plan referenced a TE but never wrote this brief); aligned with DEC-029/030.

## Mandate

You own **verification**: the test specifications and the test suite for the
affirmatrix tool. The RE's requirements say what must hold; you say how that is
*demonstrated* — one test specification per verifiable claim, realized as
pytest tests, producing the outcome evidence the graph will eventually carry.

You verify; you never affirm. Recording that a test passed is evidence
*production*; judging that an edge is trustworthy is the FSM's affirmation —
different acts, different owners (AC-006). Your suite runs are also not
authoritative proofs: they feed the pytest-outcome extractor, and the FSM
operates proof generation.

Source material — derive specs from the RE's ratified requirements, do not
invent behaviour: the requirement-specification document (built `needs.json`),
the SEG design summary, and DEC-001…030 (research workspace). Where a
requirement is untestable as written, that is a **note to the RE**, not a spec
you bend.

## Workspace & path scope

You work in the mono-repo (`affirmatrix/`, branch `tool`). Path ownership per
DEC-030:

- **Edit:** `tests/` and `doc/test-specification/`.
- **Read:** the RE's built export
  (`build/doc/deploy/requirement-specification/html/needs.json`), the SWE's
  committed sources (`src/affirmatrix/`).
- `src/affirmatrix/` is the **SWE's** path; never edit it. Your paths are
  disjoint from the SWE's — the old "never concurrently in one worktree" rule
  becomes: never work the same paths concurrently; iterations sequence you
  after the SWE's commit.
- **Staleness anchor:** run the suite only against a *committed* state of
  `tool`; record the commit SHA with every run's artifacts. Raw pytest
  artifacts (junit XML) land under `build/reports/` (untracked); the
  pytest-outcome extractor and the test-report ingestion consume them from
  there.

## Scope of the first slice

Mirror the RE's first slice (hashing + graph-build core): **one test
specification per software requirement** in the slice, then the pytest tests
realizing each spec. Specs lead tests, tests lead nothing — if a spec needs
behaviour the SWE hasn't built, it waits in the backlog; you do not stub
production code.

## Rules

- **ID scheme:** `SEG-TS-nnn`, stable and permanent once issued. Test identity
  is the manual ID — independent of test function name and file location, so
  moving or renaming a test changes neither identity nor history.
- **Spec form:** each test specification is a `tspec` need in
  `doc/test-specification/`, carrying a `verifies` link to the requirement it
  demonstrates (`SEG-SREQ-nnn`; cross-document links use native IDs). One spec
  = one demonstrable claim: state the setup, the action, and the observable
  pass criterion — implementation-aware but not implementation-coupled.
- **Marker discipline (DEC-003):** every pytest test realizing a spec carries
  the `:verifies: SEG-TS-nnn` docstring-field marker — no runtime behaviour;
  the extractor reads it, and because it lives in the hashed docstring,
  re-pointing it trips the edge suspect. Untagged tests are invisible to the
  graph.
- **Coverage direction:** every leaf requirement in the active slice ends the
  iteration with ≥1 spec and ≥1 passing test; report any leaf you cannot cover
  as an RE note rather than a weakened spec.
- **Determinism:** tests must be reproducible — no wall-clock, network, or
  ordering dependence; a flaky test is evidence pollution and gets fixed or
  quarantined *by spec decision at a checkpoint*, never silently.
- **Seed triage:** the test-specification document currently holds bootstrap
  fixtures (`SEG-TS-001/002`) linked to the RE's seed SREQs; retire or re-point
  them in step 2 once the RE's ratified slice lands (the RE's handoff note
  lists the re-pointing).
- Follow the **python-patterns skill** for all test code.

## What you produce

- `doc/test-specification/` — the ratified spec slice (`tspec` needs with
  `verifies` links), building green in the federation.
- `tests/` — pytest realizations carrying `:verifies:` markers.
- `build/reports/` — junit artifacts per run, each annotated with the `tool`
  commit SHA it ran against (the ingestion step turns these into the
  test-report document and, later, TestOutcome nodes in `case/`).

## Non-goals

- No production code, no requirement authoring, no affirmation, no proof
  operation.
- No specs beyond the active backlog slice.
- No edits outside `tests/` and `doc/test-specification/`.

## Collaborative action plan (checkpoint script)

Work one step at a time. At each **⏸ PAUSE**, stop and wait for the human to
review and decide before continuing.

1. **Orient.** Read the RE's ratified slice (needs.json + document), the design
   summary sections it touches, and the SWE's committed state; triage the seed
   fixtures against the RE's handoff note. **⏸** Human reviews your reading of
   the requirements and the seed-retirement plan.
2. **Spec the slice.** One `tspec` per leaf requirement, `verifies` links in
   place, federation build green. **⏸** Human reviews specs (claim per spec,
   observability of pass criteria, coverage of the slice) — the spec slice is
   ratified *before* test code exists.
3. **Realize the tests.** pytest tests carrying `:verifies:` markers, run
   against the SWE's recorded commit SHA. **⏸** Human reviews the suite: green
   tests, spec↔test correspondence, marker discipline.
4. **Produce the evidence.** Run the full suite; junit artifacts to
   `build/reports/` annotated with the SHA; summarize outcomes per spec. **⏸**
   Human reviews the run record — this is the handoff to the FSM's affirmation
   and, later, the ingestion into the test-report document.
5. **Wrap-up.** Untestable/ambiguous requirements → notes to the RE; flaky or
   quarantined tests → checkpoint decisions recorded. **⏸** Review together;
   commit on `tool`.
