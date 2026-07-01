# Schema test-drive

- **Session:** `a880b53a-ba65-4bfc-b865-b32e7f5583d4` (2026-06-08)
- **Status:** archived

## Goal
Test-drive the evidence-graph JSON schemas by hand-synthesizing realistic instance data for every node/edge/event/proof type, validating it against the schemas, then loading it into rdflib and running the planned SPARQL traceability queries — surfacing schema issues along the way.

## What happened
- Read all schemas in `prototypes/graph-construction/schemas/`. Noted `edge-excuses.json` was missing the `.schema.json` suffix (mismatching its `$id`); renamed it to `edge-excuses.schema.json`.
- Installed tooling and set up workspace; the `jsonschema` CLI is deprecated, so used the Python API for validation instead.
- Synthesized instance data incrementally: 5 node types (requirements, implementations, test specifications, test outcomes, waivers), 6 edge files, the review event, and 4 proof documents (design consistency proof, execution coverage record, coverage report, evidence manifest) under one `snapshotId`.
- Added pytests under a `tests/` folder — one test per file sharing a `validate_all` helper, plus an `$id`-keyed schema registry so `$ref`s to `edge-base.schema.json` resolve. Reached 16/16 on validation (Step 1).
- Created `context.jsonld` (the JSON-LD files had no `@context`), loaded everything into rdflib (144 triples), and wrote the SPARQL queries. Reached 22/22 with all 5 graph queries passing (Step 2). Switched to `Dataset` and added a `pytest.ini` to silence rdflib's JSON-LD deprecation warning.
- Walked the user through JSON-LD -> RDF triples -> SPARQL mechanics (user was new to JSON-LD).
- Ran a structured pass (Step 3) with an automated schema-checking script to collect issues.
- Master session reviewed the findings and returned `plans/schema-corrections.md`; implemented those corrections (9 of 10 items; one already done) and re-verified 22/22.

## Key decisions
- Drop hand-authored hash fields (`seg:merkleHash`, `seg:nodeHash`, `edgeHash`) from authored nodes — they are computed by the proof generator, not authored, and are not `required`.
- Use `unevaluatedProperties: false` instead of `additionalProperties: false` on edge schemas — in draft 2020-12 `additionalProperties` is blind to properties pulled in via `allOf` + `$ref`.
- Build a schema registry keyed by `$id` for validation, and inject `context.jsonld` at load time — needed for `$ref` resolution and for rdflib to interpret prefixes.
- Keep Q1 split into two SPARQL queries rather than a UNION — clearer, since the legs traverse different edge types.

## Conclusions / outcomes
- Full test-drive passed: schema validation + graph loading + all SPARQL queries green (22/22). The implements -> REQ-001 and verifies -> TS-017 -> PASS traceability chain is traversable.
- One real schema bug found and fixed (F1): `additionalProperties` -> `unevaluatedProperties` across edge schemas.
- Structured pass found 5 further issues (O1-O5); the master session's `schema-corrections.md` follow-up was implemented, including tightening the design-consistency-proof id pattern, adding `seg:sourceRepo`/`seg:sourcePath` to waivers, typing `seg:expiry` as `xsd:date`, and creating a reserved `edge-calls.schema.json`.

## Open questions / next steps
- O3 (flagged as the main open design question): is a `ReviewEvent` a node (with a hash, in the Merkle tree) or a metadata record (git provenance suffices)? Carried back to the high-level session.
- Bootstrapping question the plan flagged as the next high-level topic (not pursued in this session).

## Pointers
- Schemas: `/wrk/z/ws-safety/safety-evidence-graph/prototypes/graph-construction/schemas/`
  - `edge-base.schema.json`, `edge-*.schema.json` (the `unevaluatedProperties` / `$ref` pattern)
  - `context.jsonld` (JSON-LD context, `xsd:`/`seg:expiry` typing)
  - `waiver.schema.json`, `review_event.schema.json` (O2/O3), `design_consistency_proof.schema.json` (O1), `edge-calls.schema.json` (O4)
- Follow-up plan: `plans/schema-corrections.md` (master session's corrections)
- Note: the original `plans/schema-testdrive` plan is no longer present in `/home/tobi/.claude/plans/`.
