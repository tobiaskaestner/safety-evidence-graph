# SEG Schema Test Drive — CLI Session Plan

## Context

This session continues work on the Safety Evidence Graph (SEG), a knowledge
graph system for collecting auditable evidence for functional safety
certification (IEC 61508, and other standards). The schema files for repo G
have been designed in a prior session and are being imported into a git repo.

The goal of this CLI session is to:
1. Synthesize realistic instance data conforming to the schemas
2. Validate the instance data against the schemas
3. Build a small graph from the instance data and verify it is traversable
4. Surface any schema gaps or inconsistencies

This is a test-drive — not production data. Keep the scope small and focused.
Repos A,B and C 't exist for the scope of this test drive.
It is assumed that so-called extractors exist that are capable of extracting the relevant information from these repositories including the repo's HEAD sha if needed. This step needs to be mocked.



---

## Namespace and Configuration

- **Namespace base:** `https://zephyrproject.org/safety`
- **SEG vocabulary prefix:** `seg:` → `https://zephyrproject.org/seg#`
- **Hash algorithm:** SHA256 throughout
- **Config file:** `config.json` in repo root defines concrete repo URLs

---

## Repo G Directory Structure

The safety-evidence-graph is the name for Repo G.


```
safety-evidence-graph/
  config.json
  context.jsonld
  nodes/
    requirements.jsonld
    implementations.jsonld
    test_specifications.jsonld
    test_outcomes.jsonld
    waivers.jsonld
  edges/
    refines.jsonld
    verifies.jsonld
    implements.jsonld
    confirms.jsonld
    witnesses.jsonld
    excuses.jsonld
    calls.jsonld                  # empty — reserved for future use
  events/
    review_events.jsonld
  proofs/
    {snapshotId}/
      evidence_manifest.jsonld
      design_consistency_proof.jsonld
      execution_coverage_record.jsonld
      coverage_report.jsonld
  config/
    fsm_authorised_committers.yaml
  schemas/
    requirement.schema.json
    implementation.schema.json
    test_specification.schema.json
    test_outcome.schema.json
    waiver.schema.json
    edge-base.schema.json
    edge-refines.schema.json
    edge-verifies.schema.json
    edge-implements.schema.json
    edge-confirms.schema.json
    edge-witnesses.schema.json
    edge-excuses.schema.json
    review_event.schema.json
    design_consistency_proof.schema.json
    execution_coverage_record.schema.json
    coverage_report.schema.json
    evidence_manifest.schema.json
```

---

## Scenario to Synthesize

Use the following minimal but realistic scenario. It covers all node types,
all meaningful edge types, one PASS outcome, one FAIL outcome with a waiver,
and one suspect link requiring a review event.

### Requirements (repo A)

| ID | Description | Refines |
|---|---|---|
| REQ-001 | The kernel scheduler shall preempt a running thread when a higher-priority thread becomes ready. | — |
| REQ-002 | The scheduler shall not preempt a thread executing within a critical section protected by irq_lock(). | REQ-001 |

### Implementations (repo B)

| Function | Implements | Notes |
|---|---|---|
| `z_sched_preempt` | REQ-001 | @safety tagged in kernel/sched.h |
| `z_sched_lock` | REQ-002 | @safety tagged in kernel/sched.h |

### Test Specifications (repo B)

| ID | Verifies | Notes |
|---|---|---|
| TS-017 | REQ-001 | Verifies preemption within one scheduler tick |
| TS-019 | REQ-002 | Verifies no preemption inside irq_lock — FAIL outcome |

### Test Outcomes (repo C, RUN-44)

| ID | Outcome | Notes |
|---|---|---|
| RUN-44/TS-017 | PASS | — |
| RUN-44/TS-019 | FAIL | Excused by WAV-001 |

### Waivers (repo G)

| ID | Excuses | Justification |
|---|---|---|
| WAV-001 | RUN-44/TS-019 | Known timing issue in Twister under QEMU. Not reproducible on target hardware. See issue #4521. |

### Review Events

One review event: the `verifies` edge TS-017 → REQ-001 went suspect because
`implHash` changed (test execution logic updated). Test Engineer affirmed the
edge — intent unchanged, no new test run required for this affirmation.

---

## Step 1 — Synthesize Instance Data

Generate realistic JSON-LD instance documents for each file listed above.

**Hash values:** use plausible-looking but synthetic SHA256 hex strings
(64 lowercase hex chars). They do not need to be real hashes — the goal is
structural validation, not cryptographic correctness. Use a consistent
naming convention so relationships are traceable, e.g.:
- `node_hash_req_001`, `node_hash_req_002`
- `api_hash_z_sched_preempt`, `body_hash_z_sched_preempt`
- etc.

**git SHAs:** use 40-char synthetic hex strings. Use one consistent
`repoBSha` across all test outcomes in RUN-44.

**IRIs:** follow the patterns defined in the schemas exactly.

**Validation:** after generating each file, validate it against the
corresponding schema using a JSON Schema validator. Recommended tool:
```bash
pip install jsonschema
python -m jsonschema -i instance.jsonld schema.json
```
Or use `ajv` if preferred:
```bash
npm install -g ajv-cli
ajv validate -s schema.json -d instance.jsonld
```

Fix any validation errors before proceeding to the next file.

**Generation order** (respects IRI dependencies):
1. `nodes/requirements.jsonld`
2. `nodes/implementations.jsonld`
3. `nodes/test_specifications.jsonld`
4. `nodes/test_outcomes.jsonld`
5. `nodes/waivers.jsonld`
6. `edges/refines.jsonld`
7. `edges/verifies.jsonld`
8. `edges/implements.jsonld`
9. `edges/confirms.jsonld`
10. `edges/witnesses.jsonld`
11. `edges/excuses.jsonld`
12. `events/review_events.jsonld`
13. `proofs/{snapshotId}/design_consistency_proof.jsonld`
14. `proofs/{snapshotId}/execution_coverage_record.jsonld`
15. `proofs/{snapshotId}/coverage_report.jsonld`
16. `proofs/{snapshotId}/evidence_manifest.jsonld`

---

## Step 2 — Build a Graph

Load the instance data into a graph and verify it is traversable.

Recommended approach: use Python with `rdflib` to load the JSON-LD files
and run SPARQL queries against the graph.

```bash
pip install rdflib
```

Load all instance files:
```python
from rdflib import ConjunctiveGraph

g = ConjunctiveGraph()
import glob
for f in glob.glob("**/*.jsonld", recursive=True):
    g.parse(f, format="json-ld")

print(f"Loaded {len(g)} triples")
```

### Queries to run

**Q1 — Evidence chain for REQ-001:**
Find all nodes and edges forming the evidence chain for REQ-001.
Expected: REQ-001 ← implements — z_sched_preempt, REQ-001 ← verifies — TS-017,
TS-017 ← confirms — RUN-44/TS-017 (PASS).

**Q2 — Evidence chain for REQ-002:**
Expected: REQ-002 ← implements — z_sched_lock, REQ-002 ← verifies — TS-019,
TS-019 ← confirms — RUN-44/TS-019 (FAIL), RUN-44/TS-019 ← excuses — WAV-001.

**Q3 — All suspect links:**
Query for all edges where `seg:linkState` is not `active`.
Expected: the verifies edge TS-017 → REQ-001 should appear as previously
suspect but now active (after review event). Adjust linkState in the instance
data to test both states.

**Q4 — Scope completeness check:**
For each requirement in scope, verify presence of at least one verifies edge
and at least one implements edge.

**Q5 — Waiver validity:**
Find all excuses edges and check that the referenced waiver has a non-expired
`seg:expiry` relative to a test date of 2024-03-15.

---

## Step 3 — Surface Schema Issues

After validation and graph traversal, note any of the following:

- Fields that are present in the instance data but not in the schema
  (caught by `additionalProperties: false`)
- Fields that are missing from the schema but needed for graph queries
- IRI patterns that are too strict or too loose
- Anything that was awkward to synthesize — this often indicates a schema
  design problem

Collect all issues as a numbered list and bring them back to the high-level
session for resolution.

---

## What to Bring Back

After the CLI session, return to the high-level session with:

1. A list of schema issues found during validation (if any)
2. A list of schema issues found during graph traversal (if any)
3. Any questions about the design that surfaced during implementation
4. Confirmation that the full scenario graph is loadable and queryable

The high-level session will then address the issues and move on to the next
open question: **bootstrapping process** — what constitutes a valid first
proof when the graph is set up for the first time.
