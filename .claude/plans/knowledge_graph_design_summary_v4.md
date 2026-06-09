# Knowledge Graph Design Summary
## Auditable Safety Evidence Graph — Design Session Notes (v4)

---

## 0. Changelog (v3 → v4)

This revision resolves inconsistencies found in a cross-check of the design
summary against the JSON schemas and CLI reference. No design intent changed;
these are corrections and clarifications.

- **Witnesses verification corrected.** The `witnesses` mechanism is the
  freshness check (recorded `repoBSha` vs current repo B HEAD → stale on
  mismatch). The auditor's independent check recomputes node hashes at the
  recorded SHA and compares them against the sealed `nodeManifest` — *not*
  against hashes "stored in repo G," which are never persisted in live node
  records. Fixed in `edge-witnesses` and `execution_coverage_record` schemas
  and §2.4 / §4.1 / §9.
- **Error severity corrected.** "FAIL, no waiver" is a **Warning** (blocks
  proof), not "Info (blocks proof)" — which contradicted the severity
  contract and ranked a FAIL below a SKIP (§5).
- **Merkle dependency direction made explicit.** `strong_deps(N)` is defined
  as the in-neighbours of N (§7.2).
- **Edge IRI identifiers declared opaque.** Components are read from
  `seg:from` / `seg:to`, never parsed back out of the edge `id` (§4.7).
- **IRI / context convention stated.** Instance files carry absolute IRIs
  (§8.4).
- **SHA width unified.** All git-SHA fields in the proof/report schemas now
  accept 40- or 64-hex (SHA-1 / SHA-256), matching `test_outcome` and §7.1.
- **CoverageReport completeness.** `suspectLinks.linkState` now includes
  `pending` and `broken`, the bootstrap/missing-node states that also block
  proof.
- **Sub-hash casing unified** to camelCase (`specHash`/`implHash`/`apiHash`/
  `bodyHash`) across schema descriptions.
- **Excuses constraint** reclassified as graph-level error only (schemas
  cannot emit warnings).
- **DesignConsistencyProof storage path** corrected to the four-file
  `proofs/{snapshotId}/` directory, and its "Part 2" reference corrected to
  the ExecutionCoverageRecord.
- **Denormalized waiver expiry** documented as intentional (§6 / §9).
- Namespace genericity (project-specific `zephyrproject.org` base/vocab)
  remains deferred — see §14.

**Companion documents (do not duplicate into this spec):** binding design
decisions and their rationale live in `seg_decision_log.md` (DEC-001…DEC-004);
the concrete Python/single-repo realization (node binding, marker dialect,
extractors, branch topology, build sequencing) lives in
`seg_python_realization.md`. This spec remains the language-agnostic,
C/doxygen-oriented design of record. Where a decision *corrected* a wrong
statement here (coverage rule, `refines` acyclicity) the correction is applied
inline; refinements and realization details are recorded in the companions to
keep this spec stable.

---

## 1. Purpose and Goals

The system has two distinct but complementary goals:

**Goal 1 — Point-in-time proof**
At a specific moment (identified by a test run ID and git SHAs as provenance
metadata), every requirement in scope is implemented, tested, and the evidence
is internally consistent. This is the audit submission artefact — static,
immutable once generated, answering the functional safety auditor's question:
*"prove to me that your software does what you say it does."* The Merkle root
is the cryptographic fingerprint of this proof.

**Goal 2 — Continuous integrity monitoring**
As the codebase evolves, automatically detect which evidence chains have
broken, which links have gone suspect, and surface exactly what needs human
attention. This turns the graph from a one-time audit exercise into a
continuous engineering quality signal.

These two goals have different consumers: Goal 1 serves the auditor
(external, periodic, formal); Goal 2 serves the engineering team (internal,
continuous, operational).

---

## 2. Node Types

Five node types exist. Four are content nodes (sourced from git repos A/B/C);
one is a graph-level assertion node (sourced from repo G).

**Key principle on node hashes:** node hashes (nodeHash, apiHash, bodyHash,
specHash, implHash, merkleHash) are computed transiently by the extractor on
each CI run and used immediately for edgeHash computation and suspect
detection. They are NOT stored in the live node records in repo G. The only
place node hashes are persisted is in sealed proof documents (the nodeManifest
in DesignConsistencyProof, which stores both nodeHash and merkleHash per
node). Those sealed proof documents are themselves committed under
`proofs/{snapshotId}/` in repo G, so the precise statement is: hashes never
live in `nodes/*.jsonld`, only in sealed proofs. This avoids redundant
storage in the working graph — the hash is always recomputable from source
content, and the sealed copy exists so an auditor can verify a frozen proof
without re-running extraction.

**Lifecycle state:** explicit lifecycle fields (draft, active, deprecated) are
not needed. Lifecycle is fully computable from two signals:
- **Presence on main** — if the extractor finds a node in the current source
  repo state, it is active. If not, it is retired.
- **Edge integrity state** — pending, active, suspect variants, broken.

When the extractor finds a node in repo G that no longer exists in the source
repo, all edges touching that node are marked `broken`.

### 2.1 Requirement
- **Source:** repo A (sphinx-needs `.rst` files)
- **ID:** manually assigned by Requirements Engineer (e.g. `REQ-042`)
- **Discovery:** automatic — the extractor finds all sphinx-needs items on
  every CI run against repo A
- **Content:** sphinx-needs item text body and fields
- **Hash structure:** single `nodeHash` (purely textual, no intent/execution
  split). Computed transiently, not stored in live node records.
- **Relationship declaration:** `links:` field in sphinx-needs item declares
  **refines** edges (child requirement declares what it refines)
- **Authored by:** Requirements Engineer

### 2.2 Test Specification
- **Source:** repo B (doxygen comment above test function + test function body)
- **ID:** manually assigned via `@testcase-id` doxygen tag (e.g. `TS-017`)
- **Discovery:** marker-based — extractor only processes functions carrying
  `@testcase` doxygen tag
- **Content:** test intent (doxygen comment) + test execution logic (function
  body)
- **Hash structure:**
  - `specHash` — hash of doxygen comment (the *intent*)
  - `implHash` — hash of test function body (the *execution logic*)
  - `nodeHash` — aggregate of `specHash` + `implHash`
  All hashes computed transiently, not stored in live node records.
- **Sub-hash diagnostic signal:** when a `verifies` edge goes suspect, the
  notifier reports which sub-hash changed:
  - `specHash` changed → "the declared intent of this test spec changed —
    review whether it still verifies the requirement"
  - `implHash` changed → "the execution of this test spec changed — a new
    test run is likely needed"
  - Both changed → "both intent and execution changed — full review required"
  The sub-hash distinction is informational only: the link state model marks
  the edge suspect regardless of which sub-hash changed.
- **Relationship declaration:** `@verifies REQ-042` doxygen tag declares
  **verifies** edges; many-to-many supported via multiple tags
- **Authored by:** Test Engineer

### 2.3 Implementation
- **Source:** repo B (doxygen comment in `.h` + function body in `.c`)
- **ID:** function name (e.g. `auth_validate`) — locator for extractor only,
  not a semantic anchor for evidence
- **Discovery:** marker-based — extractor only processes functions carrying
  `@safety` doxygen tag in header
- **Content:** API design (doxygen comment in `.h`) + implementation (function
  body in `.c`)
- **Hash structure:**
  - `apiHash` — hash of doxygen comment in header (the *API design*)
  - `bodyHash` — hash of function body in `.c` (the *implementation*)
  - `nodeHash` — aggregate of `apiHash` + `bodyHash`
  All hashes computed transiently, not stored in live node records.
- **Sub-hash diagnostic signal:** when an `implements` edge goes suspect:
  - `apiHash` changed → "the declared intent of this implementation changed —
    review whether it still satisfies the requirement"
  - `bodyHash` changed → "the execution of this implementation changed — a
    new test run is likely needed"
  - Both changed → "both intent and execution changed — full review required"
- **Relationship declaration:** `@implements REQ-042` doxygen tag declares
  **implements** edges; many-to-many supported via multiple tags.
- **Authored by:** Software Engineer
- **Note:** no `@node-id` tag needed. Function name is sufficient as a
  locator. A rename that leaves the doxygen comment and `@implements` tags
  intact is not a meaningful change to the evidence.

### 2.4 Test Outcome
- **Source:** repo C (twister test runner output, text files)
- **ID:** derived automatically: `{run_id}/{testcase_id}` (e.g. `RUN-44/TS-017`)
- **Discovery:** fully automatic — no markers needed
- **Content:**
  ```
  run_id:         RUN-44
  spec_id:        TS-017 (IRI reference)
  repo_b_sha:     d4e5f6...   # git SHA of repo B at test execution time
  outcome:        PASS | FAIL | ERROR | SKIPPED
  source_repo:    repoC
  source_path:    path/to/twister.log
  ```
- **Hash structure:** single `nodeHash` over all content fields. Computed
  transiently, not stored in live node records.
- **Edges created automatically:**
  - `confirms` → test spec identified by `spec_id`
  - `witnesses` → implementation nodes (verified via `repo_b_sha` at proof
    generation time)
- **Immutability:** test outcome nodes are never updated. A new test run
  produces new nodes. Old nodes are retained permanently.
- **Generated by:** CI pipeline (twister + test outcome extractor)

**On staleness:** at proof generation time, `repo_b_sha` is compared against
current repo B HEAD. If they differ, the outcome is stale and discarded from
the proof. Stale outcomes do not block proof generation if fresh outcomes with
the same `spec_id` satisfy coverage conditions. All discarded stale outcomes
are recorded in the CoverageReport.

### 2.5 Waiver
- **Source:** repo G (currently; `seg:sourceRepo` and `seg:sourcePath` retained
  for portability if waivers move to a dedicated repo in future)
- **ID:** manually assigned by FSM (e.g. `WAV-001`)
- **Content:**
  ```
  waiver_id:      WAV-001
  outcome_id:     RUN-44/TS-017 (IRI reference)
  justification:  "Known timing issue in test harness..."
  expiry:         2024-06-15    # optional but recommended
  source_repo:    repoG
  source_path:    nodes/waivers.jsonld
  ```
- **Provenance (from git log, not stored in content):**
  - `approver` — git committer identity, cross-referenced against
    `fsm_authorised_committers.yaml`
  - `approved_at` — git commit timestamp
  - Both `identity` and `github_username` must match the same entry in
    the authorised committers file with a valid date range
- **Relationship:** `excuses` → Test Outcome
- **Owned by:** Functional Safety Manager exclusively
- **Immutability:** append-only. Superseded waivers are retired by creating
  a new waiver, never by editing.

### 2.6 Hash Structure Summary

| Node Type | "Intent" sub-hash | "Execution" sub-hash | Aggregate |
|---|---|---|---|
| Requirement | — | — | `nodeHash` |
| Test Specification | `specHash` (doxygen) | `implHash` (test body) | `nodeHash` |
| Implementation | `apiHash` (doxygen/`.h`) | `bodyHash` (`.c`) | `nodeHash` |
| Test Outcome | — | — | `nodeHash` |
| Waiver | — | — | `nodeHash` |

All hashes computed transiently by extractors. Persisted only in sealed
proof documents (DesignConsistencyProof nodeManifest).

### 2.7 Node Type × Repo × Owner Summary

| Node type | Repo | Authored/generated by | Owned by |
|---|---|---|---|
| Requirement | A | Requirements Engineer | Requirements Engineer |
| Test Specification | B | Test Engineer | Test Engineer |
| Implementation | B | Software Engineer | Software Engineer |
| Test Outcome | C | CI pipeline | Test Engineer / CI |
| Waiver | G | Functional Safety Manager | FSM exclusively |

---

## 3. Authoring Marker Ecosystem

| Node type | Discovery marker | ID | Relationship tag(s) |
|---|---|---|---|
| Requirement | sphinx-needs `.. need::` | Manual ID field | `links:` field (refines) |
| Implementation | `@safety` doxygen tag | Function name | `@implements REQ-xxx` |
| Test Specification | `@testcase` doxygen tag | `@testcase-id TS-xxx` | `@verifies REQ-xxx` |
| Test Outcome | N/A (auto-generated) | `{run_id}/{testcase_id}` | N/A (auto-derived) |
| Waiver | N/A (graph tool) | Manual ID by FSM | N/A (graph tool) |

---

## 4. Relationship Types and Propagation Rules

### 4.1 Relationship Matrix

| Source ↓ \ Target → | Requirement | Test Spec | Implementation | Test Outcome | Waiver |
|---|---|---|---|---|---|
| **Requirement** | refines | — | — | — | — |
| **Test Spec** | verifies | — | — | — | — |
| **Implementation** | implements | — | calls* | — | — |
| **Test Outcome** | — | confirms | witnesses | — | — |
| **Waiver** | — | — | — | excuses | — |

*`calls` is reserved for future use. Not implemented in any extractor, gate,
notifier, or proof step. No suspicion propagation.

`witnesses`: proper graph edge from Test Outcome to Implementation nodes.
The `repo_b_sha` field on the Test Outcome is the verification mechanism —
at proof generation time, current repo B HEAD SHA is compared against
`repo_b_sha`. A mismatch marks the outcome stale (see section 2.4). Separately,
an auditor verifying a sealed package re-establishes the implementation state
by rerunning the implementation extractor at the recorded `repo_b_sha` and
comparing the resulting node hashes against the `nodeManifest` in the
DesignConsistencyProof — not against any hash stored in a live node record,
since none exist there.

All edges directed upward in the V-model except `calls` (caller → callee)
and `excuses` (waiver → test outcome, the only downward edge).

### 4.2 Suspicion Propagation Rules

| Relationship | Propagation | Resolution mechanism |
|---|---|---|
| refines | ⚡ Strong | Human affirmation by Requirements Engineer |
| verifies | ⚡ Strong | Human affirmation by RE + Test Engineer |
| implements | ⚡ Strong | Human affirmation by Software Engineer |
| calls* | ○ None | N/A — reserved for future use |
| confirms | ✕ Sink | New test run required |
| witnesses | ✕ Sink | New test run required |
| excuses | ✕ Sink | N/A — waiver is terminal |

### 4.3 Link States

| State | Meaning |
|---|---|
| `pending` | Edge exists but has never been affirmed. Initial bootstrap state. Blocks proof. |
| `active` | Both endpoints unchanged since last affirmation. Valid for proof. |
| `directlyOutdated` | This node's own content changed. Blocks proof. |
| `transitivelySuspect` | A dependency changed. Blocks proof. |
| `doublyOutdated` | Both this node and a dependency changed. Blocks proof. |
| `broken` | One or both endpoint nodes no longer exist in their source repo. Cannot be resolved by affirmation — missing node must be restored, edge removed, or endpoint updated. Blocks proof. |

### 4.4 Edge Hash Computation

The `edgeHash` on strong-propagation edges is computed as:
```
edgeHash = SHA256(from || to || type || nodeHash(from) || nodeHash(to))
```

This cryptographically binds the edge to the content of both endpoints at
the moment of affirmation. The suspect link detector recomputes this hash
using current node hashes — a mismatch marks the edge suspect.

The point of the graph is to cryptographically bind relationships to content.
The relationships themselves are declared by authoring tools (@verifies,
@implements, @refines tags). The graph's role is to record and protect the
content hash bindings.

### 4.5 Bootstrapping

When the graph is first set up, all edges are assigned `linkState: pending`.
No edge has ever been affirmed. The bulk affirmation mode of `seg graph affirm`
is the mechanism for the initial affirmation sweep:

```
seg graph affirm --edge-type implements --scope REQ-001..REQ-050 --role SoftwareEngineer
```

After the bootstrap sweep completes and all in-scope edges are `active`,
standard Gate 2 conditions apply unchanged. No special relaxed conditions
for the first proof.

Git commit convention for bulk affirmations: one commit per bulk operation,
query string recorded in the commit message.

### 4.6 Schema Constraints

- A Test Outcome is only valid as audit evidence if it has both a `confirms`
  edge and a `witnesses` edge.
- Suspect links only block proof generation for scopes whose evidence chains
  pass through those links.
- Proof generation is per-scope.
- The `refines` relation MUST be acyclic; a cycle or self-loop is a
  graph-level error. (Both the deep-Merkle closure in §7.2 and the recursive
  satisfaction rule in §12.5 require a DAG to terminate. The other strong
  edges cannot form cycles — nothing strong points back into a test spec or
  implementation — so this constraint applies to `refines` specifically.)

### 4.7 Edge Identifiers Are Opaque

Edge `id` IRIs are constructed for global uniqueness and human readability
(e.g. `.../edge/confirms/{runId}-{testSpecId}`), but they are treated as
opaque keys. Because component tokens such as `runId` themselves contain
hyphens, the hyphen-joined `id` is not reliably parseable back into its
parts. Tooling MUST read an edge's endpoints from the `seg:from` and `seg:to`
fields — never by splitting the `id`. Every component needed downstream is
recoverable from the endpoint IRIs, so no information is lost by this rule.

---

## 5. Error Handling Contract

| Severity | Blocks commit? | Blocks proof generation? |
|---|---|---|
| Error | Yes | Yes |
| Warning | No | Yes |
| Info | No | No* |

*Info items appear in the CoverageReport.

### Per-condition table

**Requirements extractor:**

| Condition | Severity |
|---|---|
| Duplicate requirement ID | Error |
| Broken `links:` reference | Warning |

**Implementation extractor:**

| Condition | Severity |
|---|---|
| `@safety` present but no doxygen comment body | Error |
| Function body not found for tagged header | Error |
| Duplicate function name across translation units | Error |
| `@safety` present but no `@implements` tag | Warning |
| `@implements` references non-existent requirement ID | Warning |

**Test specification extractor:**

| Condition | Severity |
|---|---|
| `@testcase` present but no `@testcase-id` | Error |
| `@testcase` present but no doxygen comment body | Error |
| Test function body not found | Error |
| Duplicate `@testcase-id` across test files | Error |
| `@testcase` present but no `@verifies` tag | Warning |
| `@verifies` references non-existent requirement ID | Warning |

**Test outcome extractor:**

| Condition | Severity |
|---|---|
| Missing `repo_b_sha` | Error |
| Duplicate `run_id/testcase_id` | Error |
| `spec_id` references non-existent test spec | Warning |
| Outcome is SKIPPED, no waiver | Warning |
| Outcome is ERROR, no waiver | Warning |
| Outcome is FAIL, no waiver | Warning (blocks proof) |
| Outcome is FAIL, valid waiver | Info (does not block proof) |
| Outcome is FAIL, expired waiver | Warning |
| `repo_b_sha` does not match current HEAD of repo B | Info (flagged in CoverageReport as stale) |

---

## 6. Waiver Rules

| Outcome state | Proof effect |
|---|---|
| PASS | Chain satisfied |
| FAIL, no waiver | Blocks proof |
| FAIL, valid waiver | Chain conditionally satisfied |
| FAIL, expired waiver | Blocks proof |
| SKIPPED, no waiver | Blocks proof |
| ERROR, no waiver | Blocks proof |

**On denormalized expiry (intentional):** a waiver's `seg:expiry` is the
single source of truth, stored on the Waiver node. When a waiver excuses an
in-scope outcome, the ExecutionCoverageRecord carries a *copy* of that date as
`seg:waiverExpiry` alongside the `seg:waiverId` reference. This denormalization
is deliberate — it lets the Gate 3 release check confirm no waiver has expired
without traversing back into the graph. The two terms (`seg:expiry` on the
node, `seg:waiverExpiry` in the record) are the same value by construction.

---

## 7. Merkle Hash Structure

### 7.1 Hash Algorithm

SHA-256 throughout. This applies to all nodeHash, edgeHash, merkleHash, and
merkleRoot computations. Git object IDs (repo SHAs) may be SHA-1 (40 hex
chars) or SHA-256 (64 hex chars) depending on repo configuration — both are
supported. Every git-SHA-bearing field (the `repoBSha` on TestOutcome, the
four repo SHAs in the EvidenceManifest, `repoBSha` in the
ExecutionCoverageRecord, and `recordedSha`/`currentSha` in the CoverageReport)
uses the same `^[0-9a-f]{40}([0-9a-f]{24})?$` pattern. SEG's own computed
hashes (nodeHash, edgeHash, merkleHash, merkleRoot) are always SHA-256 and
fixed at 64 hex chars.

### 7.2 Merkle Hash Computation

Deep Merkle — full transitive closure over strong-propagation edges.

**Dependency direction (critical).** `strong_deps(N)` is the set of *in-neighbours*
of N over strong-propagation edges: every node M such that a `refines`,
`verifies`, or `implements` edge points **to** N (i.e. `seg:to == N`). Because
all strong edges point upward toward the requirement they support, Merkle
aggregation runs **opposite to edge direction**: a Requirement's dependencies
are the child Requirements, TestSpecifications, and Implementations that point
at it; TestSpecifications and Implementations have no strong in-neighbours and
are therefore the **leaves**; top-level Requirements (those nothing else
refines within scope) are the **roots**. Both implementers of the traversal
must use this definition or they will compute different — but each
self-consistent — Merkle roots.

**Leaf nodes** (no strong dependencies within scope):
```
merkleHash(N) = SHA256(nodeHash(N))
```

**Non-leaf nodes:**
```
merkleHash(N) = SHA256(nodeHash(N) || sorted_lexicographic(merkleHash(dep) for dep in strong_deps(N)))
```

Sibling hashes are sorted **lexicographically on their hex string values**
before concatenation. This ensures deterministic computation across
implementations.

Only **refines**, **verifies**, and **implements** edges participate in
Merkle computation. **calls**, **confirms**, **witnesses**, and **excuses**
do not.

### 7.3 Evidence Root

There is no explicit root node in the graph. At proof generation time, an
implicit evidence root is computed over the top-level in-scope requirements:

```
merkleRoot = SHA256(canonicalJSON(metadata) || sorted_lexicographic(merkleHash(req) for req in top_level_scope_requirements))
```

Where `metadata` is RFC 8785 Canonical JSON over:
```json
{
  "snapshotId": "2024-03-15T14:32:00Z-a1b2c3d4e5f6",
  "scope": ["https://zephyrproject.org/safety/req/REQ-001", ...],
  "repoASha": "aabb...",
  "repoBSha": "ccdd...",
  "repoCSha": "eeff...",
  "repoGSha": "0011..."
}
```

### 7.4 The Two Subgraphs

**The design graph** — Merkle root computed over this:
- Nodes: Requirements, Test Specifications, Implementations
- Edges: refines, verifies, implements
- Proves: design consistency — "is what we said we'd build internally consistent?"

**The evidence graph** — adds:
- Nodes: Test Outcomes, Waivers
- Edges: confirms, witnesses, excuses
- Proves: execution coverage — "did we actually build and test what we said?"

Neither subgraph alone constitutes proof of requirement satisfaction. Both
are required.

### 7.5 Snapshot ID Format

```
{isoTimestamp}-{SHA256(repoASha || repoBSha || repoCSha || repoGSha)[0:12]}
```

Example: `2024-03-15T14:32:00Z-a1b2c3d4e5f6`

---

## 8. Repository Structure

| Repo | Contents | Owned by |
|---|---|---|
| Repo A | Requirements (sphinx-needs `.rst` files) | Requirements Engineer |
| Repo B | Implementation (`.c`/`.h`) + Test Specifications | Software Engineer + Test Engineer |
| Repo C | Test Outcomes (twister log files) | CI Pipeline / Test Engineer |
| Repo G | Graph state (nodes, edges, events, proofs, config) | Functional Safety Manager |

### 8.1 Repo G Directory Structure

```
repo-g/
  config.json                   # project-specific parameters (namespace,
                                #   org, repo URLs, standard, SIL level)
  context.jsonld                # shared JSON-LD context, seg: namespace
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
    calls.jsonld                # empty — reserved for future use
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
  schema/
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
    edge-calls.schema.json
    review_event.schema.json
    design_consistency_proof.schema.json
    execution_coverage_record.schema.json
    coverage_report.schema.json
    evidence_manifest.schema.json
```

### 8.2 Repo G Branching

Repo G has two long-lived branches:

**Sync branch** — CI-owned. Updated on a schedule by `seg graph sync`.
Reflects current state of source repos A, B, C against the graph. Accumulates
the affirmation backlog. Read-only for humans. Never merged to main directly.
After every merge to main, CI rebases sync onto new main — affirmed edges
disappear from the backlog.

**Main branch** — Human-owned. Advances only through deliberate PRs:
affirmations, waivers, schema changes. Proof generation always runs against
main. Reviewed and merged by the FSM.

What CI writes to sync:
- `nodes/*.jsonld` — new, updated, retired node records
- `edges/*.jsonld` — new edges (linkState: pending), updated linkState on
  existing edges

What affirmation PRs write to main:
- `edges/refines.jsonld`, `edges/verifies.jsonld`, `edges/implements.jsonld`
  — updated `seg:edgeHash` and `seg:linkState` (→ active)
- `events/review_events.jsonld` — new review event records

The diff between main and sync at any point is the affirmation backlog.

### 8.3 Authorised Committer List

`config/fsm_authorised_committers.yaml` governs who may commit to repo G
as FSM. Checked at proof generation time for every waiver in scope. Both
git committer identity string and GitHub username must match.

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

Changes to this file must be committed by a currently authorised FSM.

### 8.4 IRI and Context Conventions

Instance documents (`nodes/*.jsonld`, `edges/*.jsonld`, sealed proofs) store
**absolute** IRIs for every `id`, `seg:from`, `seg:to`, and cross-reference
field. This matches the absolute-URI patterns enforced by the node and edge
schemas and guarantees cross-repo uniqueness. The `@base` and `@vocab` entries
in `context.jsonld` exist for JSON-LD term expansion (resolving `seg:` terms
and `@type` values) and for compact authoring — not for relative-IRI
resolution of node identifiers. A validator therefore sees the same absolute
string the schema pattern expects; `@base` never has to be applied to make a
record validate.

---

## 9. Proof Generation Pipeline

The proof generator is a pure computation tool — no git operations, no
network calls. See `seg_cli_reference.md` for the full command surface.

### 9.1 Steps

**Step 1 — `seg proof check-readiness`**
Evaluate all Gate 2 conditions for the defined scope. On hard blocker: return
CoverageReport with `overallStatus: blocked`, refuse generation.

**Step 2 — `seg proof collect-scope`**
Traverse graph from scope requirements via strong-propagation edges. Collect
in-scope Requirements, TestSpecifications, Implementations, TestOutcomes.

**Step 3 — Rerun extractors**
For each in-scope node, rerun the appropriate extractor against current repo
HEAD to get current node hashes. Transient computation — hashes not read from
repo G.

**Step 4 — `seg proof verify-witnesses`**
Compare `seg:repoBSha` on each in-scope TestOutcome against current repo B
HEAD. Fresh outcomes (matching SHA) are used in the proof. Stale outcomes
(mismatching SHA) are discarded and recorded in the CoverageReport. Stale
outcomes only block proof if their removal creates a coverage gap.

**Step 5 — Compute Merkle hashes**
Bottom-up topological traversal of the design graph. Compute merkleHash for
each in-scope node. Compute evidence root (merkleRoot) over top-level
scope requirements.

**Step 6 — Assemble four proof documents**
In dependency order:
1. `design_consistency_proof.jsonld` — merkleRoot + nodeManifest
2. `execution_coverage_record.jsonld` — fresh outcomes + waiver references
3. `coverage_report.jsonld` — gaps, suspect links, stale outcomes, status
4. `evidence_manifest.jsonld` — IRIs to the above three + four repo SHAs

**`seg proof generate`** writes all four to `--output-dir`. No git side
effects. FSM places the output into `proofs/{snapshotId}/` and commits as
a PR.

### 9.2 SPDX Export

**`seg export spdx`** transforms a sealed evidence package into SPDX 3.1
JSON-LD. One-way transformation. SEG-specific fields retained as `seg:`
custom properties. `creationInfo` populated from git log at export time.

Type mappings: Requirement→spdx:Requirement, Implementation→spdx:Artifact,
TestSpecification→spdx:Artifact, TestOutcome→spdx:Action,
Waiver→spdx:Annotation, ReviewEvent→spdx:Annotation.

---

## 10. Tool Catalogue

### 10.1 SEG CLI

The `seg` tool follows the convention `seg <noun> <verb>`. Configuration
from `seg.yaml` in the west workspace root; overridable via command-line
flags. See `seg_cli_reference.md` for the full command reference.

Command surface summary:
- `seg extract requirements|implementations|test-specs|test-outcomes`
- `seg graph sync` — CI sync job
- `seg graph affirm` — human affirmation, single or bulk
- `seg proof check-readiness` — Gate 2 pre-check
- `seg proof collect-scope` — scope traversal
- `seg proof verify-witnesses` — staleness check
- `seg proof generate` — full proof generation
- `seg export spdx` — SPDX 3.1 export

All read-only proof commands accept `--branch main|sync`.

### 10.2 Extractors

One per content type. Compute node hashes transiently. Feed graph builder.
Also called internally by proof generator.

### 10.3 CI Pipeline

- Runs extractors on schedule against main branches of repos A, B, C
- Updates sync branch of repo G via `seg graph sync`
- Rebases sync onto main after every merge to main
- Runs extractor as ephemeral PR check on PRs to repos A, B, C (output
  posted as PR comment, nothing committed to repo G)
- Enforces Gate 1 (commit gate) on repos A, B, C
- Enforces Gate 3 (release gate) on release tags

---

## 11. What an Evidence Chain Looks Like

Two formally distinct parts. Both required.

**Part 1 — design consistency (Merkle root):**
> *"The design graph declares a complete and consistent evidence chain for
> REQ-042: TS-017 is declared to verify it, auth_validate is declared to
> implement it, and the Merkle root 7f2a... cryptographically commits to
> that declaration. Verifiable by recomputing from the nodeManifest."*

**Part 2 — execution coverage (ExecutionCoverageRecord):**
> *"RUN-44/TS-017 confirms TS-017 with result PASS, witnessed against repo B
> @ d4e5f6..., which matches current repo B HEAD."*

**Combined claim:**
> *"REQ-042 is satisfied because (a) the design graph declares a complete and
> consistent evidence chain, as fingerprinted by Merkle root 7f2a..., and
> (b) the execution coverage record confirms that chain was executed with a
> passing outcome against implementation state d4e5f6...."*

The EvidenceManifest is not itself Part 1 or Part 2 — it is the top-level
binder that references the DesignConsistencyProof (Part 1), the
ExecutionCoverageRecord (Part 2), and the CoverageReport, and anchors all
four source repo SHAs.

---

## 12. Enforcement Gates

| Gate | Owner | Trigger |
|---|---|---|
| Gate 1 — Commit gate | CI (automated) | Push to repo A, B, or C |
| Gate 2 — Proof gate | FSM | `seg proof generate` |
| Gate 3 — Release gate | Release Engineer | Release tag candidate |

### 12.1 Gate 1 — Commit Gate

Checks structural validity. Blocks commits with:
- Duplicate node IDs
- Missing mandatory markers
- Missing mandatory content
- Missing function bodies for tagged headers
- Missing `repo_b_sha` on test outcome records

Does NOT check: link references, suspect links, test pass/fail.

### 12.2 Gate 2 — Proof Gate (seg-proof-gate)

Evaluated by `seg proof check-readiness`. Produces CoverageReport.

Conditions for the defined scope, applying the recursive **satisfaction**
rule over the `refines` DAG (see §12.5):
- Every **leaf** requirement (no incoming `refines` edge) has ≥1 verifies edge
  and ≥1 implements edge
- Every **non-leaf** requirement has all of its children (as they exist in the
  graph) satisfied; any direct verifies/implements edges it also carries are
  enforced if present
- Every test spec has ≥1 fresh test outcome from the specified run
- Every test outcome has confirms and witnesses edges
- All strong edges in scope are active
- No in-scope node has unresolved warnings or errors
- All in-scope outcomes are PASS or have valid non-expired waiver
- All in-scope waivers have a named authorised approver

The resulting CoverageReport enumerates every in-scope strong edge that is not
`active` in its `suspectLinks` list. This includes the affirmation-resolvable
suspect states (`directlyOutdated`, `transitivelySuspect`, `doublyOutdated`)
as well as `pending` (never affirmed, e.g. during bootstrap) and `broken` (an
endpoint node no longer exists in its source repo). All of these block proof;
`pending` and `broken` are not affirmation-resolvable on their own (bootstrap
requires the initial affirmation sweep; `broken` requires restoring or
removing the missing endpoint).

### 12.3 Gate 3 — Release Gate

Thin check — does not re-evaluate evidence. Checks:
- Valid evidence package exists for release scope
- `repo_b_sha` matches release candidate commit
- Current Merkle root matches package Merkle root
- All waivers still non-expired

### 12.4 Proof Readiness Dashboard

Live Gate 2 view without triggering generation. Four panels:
structural completeness, link integrity, test outcome status, overall
readiness indicator (🟢/🟡/🔴).

### 12.5 Requirement Satisfaction (recursive)

Coverage is evaluated by transitive closure over the `refines` DAG, against
the **full graph**, not a partial scope:

- A **leaf** requirement (no incoming `refines` edge) is *satisfied* iff it
  has ≥1 active `verifies` edge and ≥1 active `implements` edge and every
  confirming outcome is PASS or validly waived.
- A **non-leaf** requirement (≥1 child) is *satisfied* iff **every** child in
  the graph is satisfied, **and** any direct `verifies`/`implements` edges it
  happens to carry also pass (enforce-if-present). A non-leaf always has ≥1
  child by construction — a requirement with no children and no coverage edges
  is a structural orphan, not vacuously satisfied.
- `refines` MUST be acyclic; a cycle or self-loop is a graph-level error (the
  recursion only terminates on a DAG — see §4.6).
- Scoping a non-leaf obligates its entire `refines` subtree; the gate may not
  declare a parent satisfied while any real child is out of scope.
- `CoverageReport.structuralGaps` reports a gap **at the leaf** where coverage
  is actually missing, never up the ancestor chain. A non-leaf appears only if
  it is an orphan.

**Honest limitation:** this proves coverage of the decomposition *as declared
and affirmed* — it cannot prove the decomposition is *complete*. Completeness
of the `refines` tree, and of the set of top-level requirements, is exactly
what human affirmation and the human trust judgment assert (see decision log
DEC-001, DEC-002).

---

## 13. Human Roles

### 13.1 Role Definitions

**Requirements Engineer** — authors requirements, affirms suspect refines/verifies links, defines audit scope.

**Software Engineer** — authors implementations, affirms suspect implements links.

**Test Engineer** — authors test specs, executes test suite, affirms suspect verifies links.

**Functional Safety Manager (FSM)** — owns repo G and graph schema, creates waivers, generates evidence packages, maintains extractors and CI. Does NOT author content in repos A, B, C.

**Release Engineer** — owns release process, checks Gate 3, escalates to FSM or engineering team as needed.

**Auditor** — external consumer of evidence packages, read-only access.

### 13.2 Role × Task × Tool Matrix

| Role | Task | Tool |
|---|---|---|
| Requirements Engineer | Author requirement | Sphinx-needs |
| Requirements Engineer | Review suspect link | `seg graph affirm` |
| Requirements Engineer | Define audit scope | `seg proof collect-scope` |
| Software Engineer | Author implementation | Doxygen + C toolchain |
| Software Engineer | Review suspect link | `seg graph affirm` |
| Test Engineer | Author test spec | Doxygen + test framework |
| Test Engineer | Execute test suite | Twister + `seg extract test-outcomes` |
| Test Engineer | Review suspect link | `seg graph affirm` |
| FSM | Create waiver | Graph manipulator |
| FSM | Monitor proof readiness | `seg proof check-readiness` |
| FSM | Generate evidence package | `seg proof generate` |
| FSM | Export to SPDX | `seg export spdx` |
| FSM | Maintain authorised committers | `fsm_authorised_committers.yaml` |
| Release Engineer | Check release readiness | Gate 3 check |
| CI Pipeline | Sync graph state | `seg graph sync` |
| CI Pipeline | Enforce commit gate | Gate 1 |
| CI Pipeline | Enforce release gate | Gate 3 |

---

## 14. Open Questions

### Parked for dedicated discussion (see `seg_git_workflow_discussion_plan.md`)
- Git branching workflow — dual-input problem for CI sync job
- Notification dampening policy
- Scheduled CI job input specification

### Not yet addressed
- Implementation language for the `seg` tool (starting in repo G, may move
  to own repo)
- **Namespace genericity (deferred).** `context.jsonld` hardcodes
  `zephyrproject.org` for both `@base` and the `seg#` vocabulary. The system
  is structurally generic, but true cross-project portability requires
  relocating the `seg#` vocab to a neutral domain and making the base
  project-configurable via `config.json`. Deferred by decision; the current
  "generic" claim should be read as "structurally generic, namespace
  project-specific for now."
- **`seg:specId` vs `seg:testSpecId` (optional cleanup).** Two term names for
  the same "IRI of a TestSpecification" relation — `seg:specId` on the
  TestOutcome node, `seg:testSpecId` in CoverageReport gap lists. Harmless
  but a candidate for consolidation to a single term in a future schema pass.

---

## 15. Separate Session: TSF Layer Exploration

See `tsf_layer_exploration_plan.md`. Key hypothesis: the integrity layer is
a precondition checker for the trust scoring layer. A clean integrity state
is necessary but not sufficient for a high trust score.
