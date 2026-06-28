# Prototype Agent Brief — SEG Phase A

## Mandate

The Safety Evidence Graph (SEG) binds safety requirements, tests, and code into
a hash-anchored graph and generates an integrity proof over it. **This is a
throwaway de-risking prototype.** Its job is to play through the core graph
workflows and **surface unknowns** before the real tool is built — not to be
reused, packaged, or made production-clean.

Reference docs (read first): `seg_decision_log.md` (DEC-001…DEC-004),
`seg_python_realization.md`, the schemas in `schema/`. Where a question isn't
answered here, ask — do not invent design.

## Hard non-goals

- **No real extractors.** Work only from the hand-written "would-be" store
  (below). Do not parse Python/C source, doxygen, or pytest output.
- **No four-branch topology / worktrees.** Plain single-branch repo.
- **No packaging.** Plain modules invoked from the command line; no
  `pyproject.toml`, no install step.
- **No auto-pilot workflow validation.** Do not write a test suite that asserts
  the three workflows are "correct" and self-passes. Workflow correctness is
  judged by the human in the action plan. (Mechanical unit checks are fine —
  see Build scope.)

## Build scope

Layout:
```
prototype/
  README.md            # restate the throwaway mandate + how to run
  store.json           # the would-be store (the only input)
  loader.py            # store -> hashes -> schema-valid node/edge records
  graph_model.py       # in-memory nodes, edges, link-states
  hashing.py           # raw-byte hashing of `to_hash` values; derive nodeHash/merkleHash
  satisfaction.py      # leaf/non-leaf recursive coverage (DEC-001)
  suspect.py           # suspect propagation over strong edges
  workflows.py         # consistency(), generate_proof(scope), detect_suspect()
  cli.py               # invoke the three workflows from the command line
  schema/              # COPY of the real schemas, for validating emitted records
```

The would-be store — a JSON list of items in this shape (graph stores only the
computed hashes, so the store carries pre-hash **content** + **references**;
the store itself is **not** schema-validated):

```json
{ "id": "REQ-001", "type": "Requirement", "name": "REQ-001",
  "to_hash": { "nodeHash": "<requirement text>" }, "refines": ["SYS-REQ-001"] }

{ "id": "IMPL-x", "type": "Implementation", "name": "x",
  "to_hash": { "apiHash": "<signature+docstring>", "bodyHash": "<body>" },
  "implements": ["REQ-001"] }

{ "id": "TS-017", "type": "TestSpecification", "name": "TS-017",
  "to_hash": { "specHash": "<intent>", "implHash": "<test body>" },
  "verifies": ["REQ-001"] }

{ "id": "RUN-44/TS-017", "type": "TestOutcome", "name": "RUN-44/TS-017",
  "runId": "RUN-44", "outcome": "PASS", "repoBSha": "<40 hex>",
  "specId": "TS-017", "implId": "IMPL-x",
  "to_hash": { "nodeHash": "<outcome record>" } }

{ "id": "WAV-001", "type": "Waiver", "name": "WAV-001",
  "excuses": "RUN-44/TS-099", "approver": "<id>", "expiry": "YYYY-MM-DD",
  "reason": "<text>", "to_hash": { "nodeHash": "<waiver record>" } }
```

Loader behaviour: hash each `to_hash` value over raw bytes; derive `nodeHash`
(for Implementation/TestSpecification) and `merkleHash` from the sub-hashes;
emit schema-valid node + edge records that carry **only hashes and references,
never content**; build edges from the reference fields (`refines`, `implements`,
`verifies`, `specId`→confirms, `implId`→witnesses, `excuses`).

Three workflows, as plain callable functions (no self-asserting tests):
1. **consistency()** — build the graph, report structural gaps, link states,
   and requirement satisfaction by the DEC-001 leaf/non-leaf recursive rule.
2. **generate_proof(scope)** — produce a proof over a requirement scope,
   including the **partial-vs-total top-level scope signal** (DEC-002): does the
   scope cover all top-level requirements in the graph, or a subset?
3. **detect_suspect()** — given a mutation to the store, recompute and report
   which edges changed link-state and how suspicion propagates.

Permitted mechanical unit checks (pytest, optional, structural only): emitted
records validate against `schema/`; hashing is deterministic. **Not** workflow
correctness.

## Collaborative action plan (checkpoint script)

Work through these **one at a time**. At each **⏸ PAUSE**, stop and wait for the
human to inspect and decide before continuing. The human drives all mutations.

1. **Scaffold** the layout + README. **⏸** Human reviews layout.
2. **Write `store.json`**: 2–3 system requirements, each refined into 2–3
   software requirements; 1–2 test specs per software requirement;
   implementations 1:1 with software requirements; one run of outcomes. Include
   at least one fully-satisfied subtree. **⏸** Human reviews the dataset, may
   adjust it.
3. **Loader + hashing**: emit the graph; run the structural unit checks. **⏸**
   Human inspects the emitted nodes/edges/hashes and the schema-validation
   result.
4. **Workflow 1 — consistency()**: run it against the graph. **⏸** Human
   inspects the gaps / link-states / satisfaction output and judges it.
5. **Workflow 2 — generate_proof(scope)**: human names a scope; agent generates
   the proof + scope signal. **⏸** Human inspects and judges, including the
   partial-vs-total signal on a deliberately partial scope.
6. **Workflow 3 — detect_suspect()**: **human picks a node and a mutation**
   (e.g. edit a software-requirement body, or a test body); agent applies it to
   the store and recomputes. **⏸** Human judges what went suspect and how it
   propagated. Repeat for a couple of human-chosen mutations, including one that
   makes a leaf fail so the human can see transitive satisfaction fail at the
   parent with the gap reported at the leaf (DEC-001, both directions).
7. **Wrap-up**: agent collects surprises / surfaced unknowns into a short
   `NOTES.md` for the real implementation. **⏸** Review together.
