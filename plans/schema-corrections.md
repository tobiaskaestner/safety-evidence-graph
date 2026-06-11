# SEG Schema Corrections — CLI Session Plan

## Context

Apply a set of corrections to the SEG schema files in the repo. All changes
are well-defined — no design decisions needed. If anything is ambiguous, note
it and skip rather than guessing.

---

## Corrections to Apply

### 1 — `edge-base.schema.json`

Update the `seg:edgeHash` description to reflect the correct computation:
```
H(from || to || type || nodeHash(from) || nodeHash(to))
```

Add `pending` to the `seg:linkState` enum in `strongEdge`. The full enum
should be:
```json
["pending", "active", "directlyOutdated", "transitivelySuspect", "doublyOutdated"]
```

---

### 2 — `requirement.schema.json`

Remove `seg:nodeHash` and `seg:merkleHash` from `required` array and
`properties`. Node hashes are computed transiently by the extractor and
persisted only in sealed proof documents.

---

### 3 — `implementation.schema.json`

Remove `seg:nodeHash`, `seg:apiHash`, `seg:bodyHash`, and `seg:merkleHash`
from `required` array and `properties`. Same reasoning as above.

---

### 4 — `test_specification.schema.json`

Remove `seg:nodeHash`, `seg:specHash`, `seg:implHash`, and `seg:merkleHash`
from `required` array and `properties`. Same reasoning as above.

---

### 5 — `test_outcome.schema.json`

Remove `seg:nodeHash` from `required` array and `properties`. Same reasoning
as above.

---

### 6 — `waiver.schema.json`

Remove `seg:nodeHash` from `required` array and `properties`.

Add `seg:sourceRepo` and `seg:sourcePath` to `required` array and
`properties`:
- `seg:sourceRepo`: fixed value `repoG`
- `seg:sourcePath`: string, relative path to the waivers file within repo G

Rationale: waivers currently live in repo G but may move to a separate repo
in future. Keeping these fields consistent with all other node types
preserves that flexibility.

---

### 7 — `design_consistency_proof.schema.json`

Tighten the `id` pattern from:
```
^https://[^/]+/[^/]+/proof/.+$
```
to:
```
^https://[^/]+/[^/]+/proof/.+/design-consistency-proof$
```
This brings it in line with the fixed-suffix convention used by the other
three proof schemas.

---

### 8 — `context.jsonld`

Add `"@type": "xsd:date"` to the `seg:expiry` entry so SPARQL date
comparisons work correctly:
```json
"seg:expiry": { "@id": "seg:expiry", "@type": "xsd:date" }
```
Note: check whether the prefix in `context.jsonld` still says `iec61508:`
— update all occurrences to `seg:` if that rename has not yet been applied.

---

### 9 — Create `edge-calls.schema.json`

Create a minimal schema file for the calls edge. It should follow the same
structure as the other sink edge schemas but with a clear
reserved-for-future-use note in the description. No `strongEdge` composition
— calls carries no propagation, no edgeHash, no linkState. The `@graph` in
the corresponding `calls.jsonld` instance file remains empty.

---

### 10 — All edge schemas using `allOf` + `$ref`

Replace `additionalProperties: false` with `unevaluatedProperties: false`
in all edge schemas that use `allOf` + `$ref` composition. This is required
by JSON Schema draft 2020-12. Affected files:

- `edge-refines.schema.json`
- `edge-verifies.schema.json`
- `edge-implements.schema.json`
- `edge-confirms.schema.json`
- `edge-witnesses.schema.json`
- `edge-excuses.schema.json`

---

## Validation

After applying all corrections, rerun the full validation suite against the
synthesized instance data from the previous session. All files should pass.
Note any new failures and report back.

---

## What to Report Back

1. Confirmation that all corrections applied cleanly
2. Any validation failures after corrections
3. Any ambiguities encountered
