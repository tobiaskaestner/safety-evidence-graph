# SEG Schema Test-Drive — Issue List

Issues surfaced during Step 1 (validation) and Step 2 (graph traversal).
Status: **fixed** = already corrected in this session; **open** = needs decision.

---

## Fixed during test-drive

### F1 — `additionalProperties` must be `unevaluatedProperties` in all edge schemas
**Schemas:** edge-refines, edge-verifies, edge-implements, edge-confirms, edge-witnesses, edge-excuses  
**Symptom:** `seg:edgeHash` and `seg:linkState` (defined in `strongEdge` via `$ref`) were rejected
as "additional properties" on strong edges. `comment` (from `baseEdge`) would also be rejected
on any edge if present.  
**Root cause:** In JSON Schema draft 2020-12, `additionalProperties: false` only considers
properties declared in the *same schema object's* `properties` keyword. It is blind to `allOf`
subschemas. The `unevaluatedProperties` keyword (new in 2020-12) was designed exactly for this
pattern.  
**Fix applied:** Replaced `additionalProperties: false` with `unevaluatedProperties: false` in
all six edge schemas.

---

## Open issues

### O1 — `design_consistency_proof` id pattern is too loose
**Schema:** design_consistency_proof.schema.json  
**Current pattern:** `^https://[^/]+/[^/]+/proof/.+$`  
**Problem:** Accepts any path under `/proof/`, e.g. `/proof/foo` or `/proof/2024/execution-coverage`.
The other three proof schemas all end with a fixed suffix (`/evidence-manifest`,
`/execution-coverage`, `/coverage-report`), making them self-describing and tamper-evident.  
**Suggested fix:** `^https://[^/]+/[^/]+/proof/[^/]+/design-consistency-proof$`

---

### O2 — `waiver.schema.json` is missing `seg:sourceRepo` and `seg:sourcePath`
**Schema:** waiver.schema.json  
**Problem:** Every other node schema (requirement, implementation, test_specification,
test_outcome) has `seg:sourceRepo` and `seg:sourcePath` as required fields. Waivers are the
only node type that cannot be traced back to a source file and repo, which breaks the
consistency of the "where did this node come from?" provenance model.  
**Note:** Waivers always originate in repo G, so `seg:sourceRepo` would be `"repoG"` (const),
and `seg:sourcePath` would be the path to the waiver file within repo G.  
**Suggested fix:** Add both fields, with `seg:sourceRepo` fixed to `"repoG"`.

---

### O3 — `review_event.schema.json` has no `seg:sourceRepo`, `seg:sourcePath`, or `seg:nodeHash`
**Schema:** review_event.schema.json  
**Problem:** ReviewEvents are stored in repo G alongside waivers, yet they carry no source
provenance and no content hash. This is partly intentional — the schema description states that
provenance is derived from git log — but it means:
- A ReviewEvent cannot be independently verified by hash (unlike every other node type).
- It is inconsistent with all other node schemas.

**Design question:** Is a ReviewEvent a *node* (with a hash and source path) or a *metadata
record* (where git provenance is sufficient)? The current schema treats it as metadata, but it
is stored in a `jsonld` file alongside nodes. The answer affects whether ReviewEvents appear
in the Merkle tree.

---

### O4 — `edge-calls.schema.json` is missing
**File:** edges/calls.jsonld exists (empty, reserved for future use)  
**Problem:** All other edge types have a corresponding schema. `seg:Calls` has none. This means
calls edges cannot be validated if the file is ever populated.  
**Suggested fix:** Add a minimal `edge-calls.schema.json` now, even if it only validates
structure and leaves semantic constraints for later.

---

### O5 — `seg:expiry` on Waiver is an untyped string literal in the graph
**Context:** context.jsonld  
**Problem:** `seg:expiry` is not declared in the context, so it lands in the graph as a plain
string literal (`"2025-12-31"`) rather than an `xsd:date`. SPARQL date arithmetic
(`FILTER(?expiry > "2024-03-15"^^xsd:date)`) requires proper datatype binding. The Q5 test
worked around this with Python string comparison, which is fragile for non-ISO formats.  
**Suggested fix:** Add `"seg:expiry": { "@type": "xsd:date" }` to context.jsonld.

---

## Summary table

| # | Status | Schema(s) affected | Category |
|---|--------|-------------------|----------|
| F1 | Fixed | 6 edge schemas | Draft 2020-12 keyword misuse |
| O1 | Open | design_consistency_proof | IRI pattern too loose |
| O2 | Open | waiver | Missing provenance fields |
| O3 | Open | review_event | Design question — node vs metadata |
| O4 | Open | (missing) | Gap in schema coverage |
| O5 | Open | context.jsonld | Missing datatype annotation |
