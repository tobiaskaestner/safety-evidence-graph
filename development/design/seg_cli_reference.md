# SEG CLI Reference

## Overview

The `seg` tool is the command-line interface for the Safety Evidence Graph
system. It follows the convention `seg <noun> <verb>` with optional flags.

Configuration is read from `seg.yaml` in the west workspace root. Command-line
flags override `seg.yaml` values when both are present.

All read-only commands accept a `--branch` flag (default: `main`) to query
against the sync branch during development.

---

## Configuration — `seg.yaml`

Lives in the west workspace root alongside `west.yml`. Not versioned in any
single repo — local paths vary per developer environment.

```yaml
repos:
  repoA: "../zephyr"
  repoB: "../zephyr"
  repoC: "../safety-evidence"
  repoG: "."

tools:
  extractor_requirements: "seg extract requirements"
  extractor_implementations: "seg extract implementations"
  extractor_test_specs: "seg extract test-specs"
  extractor_test_outcomes: "seg extract test-outcomes"
```

Ship `seg.yaml.example` in repo G; gitignore `seg.yaml`.

---

## Extractor Commands

Run by CI on every push to repos A, B, or C. Also called internally by the
proof generator. Can be run manually for debugging.

### `seg extract requirements`
Parses sphinx-needs `.rst` files in repo A. Finds all `.. need::` items.
Computes `nodeHash` for each requirement. Reads `links:` field for refines
edges.

```
seg extract requirements [--repoA <path>] [--sha <sha>]
```

### `seg extract implementations`
Parses `.h`/`.c` files in repo B. Finds `@safety`-tagged functions. Computes
`apiHash`, `bodyHash`, `nodeHash`. Reads `@implements` tags for implements
edges.

```
seg extract implementations [--repoB <path>] [--sha <sha>]
```

### `seg extract test-specs`
Parses test files in repo B. Finds `@testcase`-tagged functions. Computes
`specHash`, `implHash`, `nodeHash`. Reads `@verifies` tags for verifies edges.

```
seg extract test-specs [--repoB <path>] [--sha <sha>]
```

### `seg extract test-outcomes`
Parses twister log files in repo C. Maps results to `@testcase-id` values.
Captures `seg:repoBSha`. Computes `nodeHash`. Derives confirms and witnesses
edges.

```
seg extract test-outcomes [--repoC <path>] [--sha <sha>]
```

---

## Graph Commands

### `seg graph sync`
Runs all extractors against current HEAD of repos A, B, C. Compares output
against current repo G sync branch state. Writes updated node records and
edge link states to the sync branch. Run by CI on a schedule.

```
seg graph sync [--repoA <path>] [--repoB <path>] [--repoC <path>] [--repoG <path>]
```

### `seg graph affirm`
Affirms one or more suspect or pending edges. Recomputes edgeHash using
current node hashes. Sets linkState to active. Writes review event. Stages
changes for commit — does not commit.

```
seg graph affirm --edge <edgeIRI> [--role <role>] [--comment <text>]
seg graph affirm --edge-type <type> [--scope <scopeLabel>] [--role <role>]
```

Bulk affirmation example:
```
seg graph affirm --edge-type implements --scope REQ-001..REQ-050 --role SoftwareEngineer
```

---

## Proof Commands

All proof commands are read-only unless stated otherwise. They do not commit
to any repo.

### `seg proof check-readiness`
Evaluates all Gate 2 conditions for a defined scope and test run. Returns a
`CoverageReport` showing overall status (ready / pending / blocked) and
structured gap details. Does not generate a proof.

```
seg proof check-readiness --scope <scopeLabel> --run-id <runId> [--branch main|sync]
```

### `seg proof collect-scope`
Traverses the graph from the scope requirements via strong-propagation edges.
Returns the full set of in-scope node IRIs grouped by type (Requirements,
TestSpecifications, Implementations, TestOutcomes).

```
seg proof collect-scope --scope <scopeLabel> --run-id <runId> [--branch main|sync]
```

### `seg proof verify-witnesses`
For each in-scope TestOutcome, compares `seg:repoBSha` against current repo B
HEAD. Returns two lists: fresh outcomes (valid for proof) and stale outcomes
(discarded). Stale outcomes do not block proof generation if fresh outcomes
satisfy coverage conditions.

```
seg proof verify-witnesses --scope <scopeLabel> --run-id <runId> [--branch main|sync]
```

### `seg proof generate`
Generates a complete evidence package for a defined scope and test run.
Runs Steps 1-6 of the proof generation pipeline:
1. Gate 2 pre-check (`seg proof check-readiness`)
2. Collect in-scope nodes (`seg proof collect-scope`)
3. Rerun extractors at current HEADs (internal)
4. Verify witnesses edges (`seg proof verify-witnesses`)
5. Compute Merkle hashes (internal)
6. Assemble four proof documents

Writes four files to `--output-dir`:
- `design_consistency_proof.jsonld`
- `execution_coverage_record.jsonld`
- `coverage_report.jsonld`
- `evidence_manifest.jsonld`

No git operations. The FSM manually places the output into
`proofs/{snapshotId}/` in their repo G working tree and commits as a PR.

```
seg proof generate \
  --scope <scopeLabel> \
  --run-id <runId> \
  --output-dir <path> \
  [--branch main] \
  [--repoA <path>] [--repoB <path>] [--repoC <path>] [--repoG <path>]
```

**Snapshot ID format:**
```
{isoTimestamp}-{SHA256(repoASha || repoBSha || repoCSha || repoGSha)[0:12]}
```
Example: `2024-03-15T14:32:00Z-a1b2c3d4e5f6`

**Merkle root computation:**
```
merkleRoot = SHA256(canonicalJSON(metadata) || sorted_lexicographic(merkleHash(req) for req in top_level_scope_requirements))
```
Where metadata is RFC 8785 Canonical JSON over snapshotId, scope, and four
repo SHAs. Sibling hashes sorted lexicographically on hex string values.

---

## Export Commands

### `seg export spdx`
Transforms a sealed evidence package from SEG native JSON-LD format into
valid SPDX 3.1 JSON-LD. One-way transformation — SPDX is an export format,
not a working format.

SEG-specific fields (`seg:justification`, `seg:expiry`, `seg:affirmingRole`,
etc.) are retained as custom properties in the SPDX export. SEG relationship
types are retained as `seg:relationshipType` custom properties alongside the
SPDX `relationshipType` mapping.

`creationInfo` is populated from git log of the proof directory at export time.

```
seg export spdx --proof-dir <path> --output-dir <path>
```

**Type mappings:**

| SEG type | SPDX type |
|---|---|
| `seg:Requirement` | `spdx:Requirement` |
| `seg:Implementation` | `spdx:Artifact` |
| `seg:TestSpecification` | `spdx:Artifact` |
| `seg:TestOutcome` | `spdx:Action` |
| `seg:Waiver` | `spdx:Annotation` |
| `seg:ReviewEvent` | `spdx:Annotation` |
| `seg:Refines` | `spdx:Relationship` / `refinedBy` |
| `seg:Verifies` | `spdx:Relationship` / `testedBy` |
| `seg:Implements` | `spdx:Relationship` / `describedBy` |
| `seg:Confirms` | `spdx:Relationship` / `testedBy` |
| `seg:Witnesses` | `spdx:Relationship` / `evidencedBy` |
| `seg:Excuses` | `spdx:Relationship` / `other` |

---

## Authorised Committer Management

### `fsm_authorised_committers.yaml`

Located at `config/fsm_authorised_committers.yaml` in repo G. Governs who
may commit to repo G acting in the Functional Safety Manager role. Checked
at proof generation time for every waiver in scope. Changes to this file
must be committed by a currently authorised FSM.

```yaml
authorised_committers:
  - identity: "David Smith <david.smith@example.org>"
    github_username: "dsmith-safety"
    valid_from: "2024-01-01"
    valid_until: null
    comment: "Initial FSM appointment."

  - identity: "Eva Jones <eva.jones@example.org>"
    github_username: "evajones-fsm"
    valid_from: "2022-06-01"
    valid_until: "2023-12-31"
    comment: "Former FSM. Waivers approved during valid period remain valid."
```

The proof generator checks both `identity` (git committer string) and
`github_username` (GitHub PR merge metadata) against this file for every
waiver in scope. Both tokens must match the same entry with a valid date
range covering the commit date.
