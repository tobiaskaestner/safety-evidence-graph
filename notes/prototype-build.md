# Prototype build (graph-construction + SPDX v3.1 exchange)

- **Session:** `d0826f3d-dc7b-4058-9c86-4edeb47bc598` (2026-06-25)
- **Status:** archived

## Goal
Build the throwaway SEG Phase A de-risking prototype from the agent brief
(`.claude/plans/prototype_agent_brief.md`): exercise the three core graph
workflows (consistency check, proof generation, suspect detection) end-to-end
against a hand-written "would-be" store and surface unknowns before the real
tool is built. Work proceeded as a 7-step collaborative plan with a human
review pause at each checkpoint.

## What was built
- `prototype/` scaffold: `README.md` + stub modules (Step 1).
- `prototype/store.json` / `store-small.json` — hand-crafted store: 2 system
  reqs, 5 leaf reqs, 5 impls, 6 test specs, 6 outcomes, 1 waiver; covers a
  fully-satisfied subtree (SYS-REQ-001), FAIL+valid-waiver (REQ-004/WAV-001),
  and a stale-SHA failure (REQ-005/RUN-001-TS-006) that propagates to
  SYS-REQ-002 (Step 2).
- `hashing.py` (raw-byte SHA-256, nodeHash/merkleHash/edgeHash derivation),
  `graph_model.py` (Node/Edge/Graph/LinkState dataclasses), `loader.py`
  (three-pass build: nodes → edges → Merkle), `test_structural.py`
  (15 structural/determinism/schema checks) (Step 3).
- Widened the requirement IRI regex in all 7 schemas from `REQ-[0-9]+` to
  `[A-Z][A-Z0-9-]*-[0-9]+` so `SYS-REQ-xxx` and multi-tier IDs validate; the
  old "known schema gap" tests were removed.
- `cli.py` — `dump` (with `--nodes/--edges/--hashes/--dot`), `consistency`,
  `proof <regex...>`, `suspect`, plus later `generate-store` and a global
  `--store-file` flag.
- `satisfaction.py` + `workflows.consistency()` — DEC-001 recursive
  leaf/non-leaf coverage with structural-gap, suspect-link, and stale-outcome
  reporting (Step 4).
- `workflows.generate_proof(scope)` — proof over a regex-resolved requirement
  scope with the DEC-002 partial-vs-total signal, merkleRoot, and nodeManifest
  (Step 5).
- `dot_render.py` — shared state-aware DOT renderer used by `dump`/`consistency`/
  `proof` `--dot`: satisfaction/outcome/link-state colours, scope dimming,
  `rankdir=RL`, and `peripheries=2` double-border on mutated nodes.
- `suspect.py` + `workflows.detect_suspect()` — apply in-memory node patches,
  classify strong edges (directlyOutdated / doublyOutdated / transitivelySuspect
  via BFS), report link-state and satisfaction deltas (Step 6).
- `store_generator.py` + `generate-store` command — produces consistent graphs
  at configurable "up-to" sizes (medium ~40 reqs, large ~486, extra-large
  ~26.8K reqs / ~110K nodes, gitignored). Includes multi-impl (~15%) and
  cross-req test-spec (~5%) scenarios.
- Hand-crafted `store-deep.json` (3-tier SYS→MID→leaf) and
  `store-deep-mid-coverage.json` (non-leaf MID reqs with direct coverage, to
  exercise DEC-001 enforce-if-present).
- `prototypes/graph-construction/NOTES.md` — the Step 7 surfaced-unknowns
  write-up.

> Note: this transcript covers only the graph-construction prototype (Steps
> 1–7). The `prototypes/spdx-v3.1-exchange/` artifacts (`README.md`, `GAPS.md`,
> the SPDX FuSa round-trip pipeline) exist in the repo but do NOT appear in
> this session's transcript — they were produced in separate work. SPDX
> findings below are summarized from those artifacts, not from this thread.

## Key decisions
- **Widen requirement IRI regex** to `[A-Z][A-Z0-9-]*-[0-9]+` — accommodates
  `SYS-REQ`/`MID-REQ`/multi-tier IDs via regex backtracking; cheaper than a
  schema extension.
- **Strong edges initialised ACTIVE** (not PENDING) — the hand-crafted store
  represents a pre-affirmed state, so consistency output is meaningful.
- **Majority-SHA heuristic for staleness** — `Counter(repoBShas).most_common`
  picks the "current" SHA since the prototype has no live repo.
- **Scope passed as regex list, resolved in the CLI layer** — `fullmatch`
  against `store_id`, dedup, warn on no-match; `generate_proof` takes IRIs.
- **Shared `dot_render.py` (Idea 3)** — one renderer for static and
  state-overlay views so `dump`/`consistency`/`proof` stay consistent.
- **`fail_waived` rendered red, not orange** — a FAIL is a FAIL; the waiver is
  already shown by the WAV node + Excuses edge.
- **`rankdir=RL`** — top-level requirements (DAG sinks) on the left, evidence
  on the right, matching proof-reading direction.
- **`peripheries=2` on mutated nodes** — makes the change origin visible so the
  directlyOutdated → transitivelySuspect chain is traceable.
- **XL store gitignored, generate-on-demand** — 34 MB / ~2 h load is impractical
  to commit.

## Conclusions / outcomes
- All three workflows run end-to-end and produce human-validated output.
- DEC-001 exercised both directions: fully-satisfied subtree (SYS-REQ-001) and
  leaf failure cascading to a non-leaf (REQ-005 stale → SYS-REQ-002); waiver
  path and enforce-if-present (via store-deep-mid-coverage) both confirmed.
- DEC-002 partial-vs-total signal flips correctly: partial scope → `ready` +
  `uncoveredTopLevel`; total scope → `isTotalScope=true`, `blocked` by the
  stale outcome.
- Suspect propagation correct: direct/double-outdated classification + BFS
  transitive suspicion; transitivelySuspect stops at top-level reqs (no
  outgoing strong edges). Edge-hash binds both endpoints, so any node content
  change invalidates all incident strong edges (including the outgoing Refines).
- 15/15 structural tests pass; emitted records validate against the schemas;
  hashing deterministic.
- State-aware DOT export proved the standout feature for understanding proof
  state — recommended as first-class output, not an afterthought.
- Generator confirms cross-req test specs and multi-impl reqs work without
  special-casing.

## Open questions / gaps / next steps
From `graph-construction/NOTES.md` and the conversation:
- **Performance cliff:** recursive `_fill_merkle` recomputes the whole graph on
  every load — fine to ~2K nodes (0.24 s) but ~110K nodes took ~2 h. Real tool
  must persist Merkle hashes and update only the affected subtree incrementally.
- **Majority-SHA is a hack** — production must receive the current repo-B SHA
  explicitly.
- **Waiver expiry not checked** — WAV-001 has an `expiry`; prototype treats all
  waivers as valid.
- **`broken` link state never exercised** — needs a node-deletion scenario and
  resolution UX.
- **PENDING→ACTIVE affirmation path never exercised** — no ReviewEvent /
  affirmation-backlog workflow; multi-person separation of duties (DEC-004)
  open.
- **DEC-003 landmines for real extractors:** don't hash
  `ast.get_docstring(clean=True)` (breaks raw-byte guarantee — use
  `get_source_segment`); comments invisible to `ast` so markers must live in
  docstrings; tree-sitter as a future unified locator.
- **Partial-scope proof safety** — make it impossible to misread a partial
  "ready" proof as a system-level claim (warn when `isTotalScope=false`).

From `spdx-v3.1-exchange/GAPS.md` (separate work, listed for completeness):
- G3 (LOAD-BEARING): SEG residual condition lossily mapped to a free-text SPDX
  `Assumption` + a `comment` hint — motivates "machine-checkable assumptions".
- G9 (LOAD-BEARING): re-published undischarged inherited assumption yields
  UNSATISFIED, contradicting DEC-015 conditional-proof intent — no
  discharge-by-re-publish rule exists; sharpest composability finding.
- Others: no published FuSa JSON-LD context (inline-embedded), pyshacl must run
  `inference="none"`, refines direction flips on the wire, roll-up verdict
  intentionally not exported, global commitment idealized, evidence layer
  omitted, G-subtree collapsed to guarantee root on import.

## Pointers
- `/wrk/z/ws-safety/safety-evidence-graph/.claude/plans/prototype_agent_brief.md` — the 7-step brief.
- `/wrk/z/ws-safety/safety-evidence-graph/prototypes/graph-construction/NOTES.md` — surfaced unknowns (Step 7).
- `/wrk/z/ws-safety/safety-evidence-graph/prototypes/graph-construction/README.md` — what each module does + how to run.
- `/wrk/z/ws-safety/safety-evidence-graph/prototypes/spdx-v3.1-exchange/README.md` and `.../GAPS.md` — SPDX round-trip (separate work).
- `.claude/plans/seg_decision_log.md` (DEC-001…DEC-004) and `seg_python_realization.md` — referenced design docs.
