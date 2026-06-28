# SEG — Python & Single-Repo Realization

Concrete realization of the Safety Evidence Graph for a Python, single-repo,
self-hosting project. The language-agnostic / C-oriented design of record is
the SEG design summary; binding decisions and rationale are in
`notes/decision_log_index.md`. This document records *how the design is bound to this
project* and is the reference the agent briefs build on. Where this document
and v4 appear to differ, v4 states the general design and this document states
the Python/single-repo binding of it.

---

## 1. Two phases

**Phase A — De-risking prototype.** Throwaway Python in `prototype/`, plain
modules invoked from the command line (not an installable package), pytest from
the start. All inputs mocked; extractors are assumed to exist and "just work"
from imagined outputs. Purpose: exercise the three core workflows end-to-end
and surface unknowns. Mandate is to *maximize unknowns surfaced*, not to be
reused.

**Phase B — Self-hosting implementation.** The real `seg` tool, built
test-first, made to generate an integrity proof of itself. Delivered as a
backlog of small vertical iterations; each iteration (from iteration 1)
ends in a per-iteration integrity proof over its cumulative scope.

The three core workflows (both phases): (1) check a graph for consistency,
(2) generate a proof, (3) detect suspect links after an update. The prototype
mock dataset is 2–3 system requirements, each refined into 2–3 software
requirements, 1–2 test specs per software requirement, implementations mapped
1:1 to software requirements, and a single test run. Per DEC-001 it MUST also
exercise transitive satisfaction in both directions (a fully-satisfied parent,
and a parent with one failing leaf), and SHOULD add one FAIL-with-valid-waiver
chain and one stale outcome to exercise the Gate-2/3 waiver and staleness logic
that the base dataset otherwise never touches. Define 2–3 concrete *mutation*
scenarios for workflow 3 (e.g. change a software-requirement body → its
`refines`/`verifies`/`implements` edges go suspect; change a test body →
`verifies` suspect with the `implHash` diagnostic).

---

## 2. Repository and branch topology (DEC-002)

One git repository, four long-lived branches that never merge into each other,
checked out as git worktrees into one workspace directory:

| Branch | Role (design repo) | Holds |
|---|---|---|
| A | requirements (repo A) | `doc/requirements/` (sphinx-needs) |
| B | impl + test specs (repo B) | `seg/` tool source, `doc/design/`, `doc/testspec/`, `prototype/` |
| C | test outcomes (repo C) | raw pytest result artifacts (the outcome extractor's input) |
| G | graph (repo G) | `nodes/ edges/ events/ proofs/ config/ schema/`, `context.jsonld` |

- The repo-G `sync`/`main` split is collapsed into the single G branch; the
  FSM (you) maintains it. No CI: link states are refreshed by running the
  sync/extraction step manually at checkpoints.
- The affirmation backlog is the set of non-`active` edges
  (`CoverageReport.suspectLinks`), not a branch diff.
- Branch-write ownership is per role: RE→A, SWE/TE→B, outcome step→C, FSM→G.
  Worktrees enforce one branch per checkout, so agent briefs state which branch
  each agent writes.
- `seg.yaml` points `repoA/repoB/repoC/repoG` at the four worktree directories.
  Branch A and B are distinct, so `repoASha ≠ repoBSha`; a requirement edit
  bumps only A and triggers re-affirmation, not a test re-run.

**Open repo-layout item.** `doc/` is conceptually one tree of four sphinx
documents but is physically split across worktrees A (requirements), B
(testspec, design) and C (testreport). Decide whether the docset is built
per-worktree or via a consolidated meta-build that reads across worktrees; the
sphinx template must be adapted accordingly.

---

## 3. Python node binding (DEC-003)

Hashing principle (language-agnostic, restated): sub-hashes are over **raw
source byte spans**; the parser is a **locator only**; span boundaries are
defined parser-independently; the parse tree never enters a hash.

| Node | Intent sub-hash | Execution sub-hash | Locator |
|---|---|---|---|
| Implementation | `apiHash` = raw bytes of signature + docstring | `bodyHash` = raw bytes of function body | `ast` |
| TestSpecification | `specHash` = raw bytes of test docstring | `implHash` = raw bytes of test body | `ast` |

- Implementer landmine: do **not** hash `ast.get_docstring(clean=True)` — it
  normalizes indentation. Slice the raw byte span instead
  (`ast.get_source_segment` is a verbatim slice and acceptable;
  `node.decorator_list`, the `FunctionDef` args, and the docstring literal node
  give the rest without importing the module).
- Span rule must be written down precisely (e.g. body = verbatim bytes from the
  `:` after the signature through the end of the function block, comments and
  whitespace included) so it is reproducible across Python versions.

### 3.1 Marker dialect

A **docstring field**, symmetric with C's in-comment doxygen `@`-tags:

```python
def auth_validate(token):
    """Validate an auth token against policy.

    :implements: SEG-REQ-014
    """
    ...
```

```python
def test_auth_validate_rejects_expired():
    """A token past its expiry is rejected.

    :verifies: SEG-REQ-014
    """
    ...
```

- The marker lives inside the hashed docstring, so re-targeting it changes the
  intent hash and correctly trips the edge suspect (matches C semantics).
- `ast` discards `#` comments, so a comment-pragma marker is not viable.
- Discovery: a function carrying an SEG docstring field is an SEG node;
  TestSpecifications are additionally pytest `test_*` functions. Test
  *identity* is a stable manual `TS-id` (independent of function name and file
  location), so moving a test does not change its hashes or identity.

### 3.2 Structure / identity / rendering vs integrity

- sphinx-needs + the `needs.json` builder (with `needs_reproducible_json`) own
  structure, IDs, relationships, and traceability rendering. For Python, an
  `ast`-based front-end emits a normalized intermediate that a custom Sphinx
  directive turns into in-memory sphinx-needs items via `nested_parse` —
  mirroring the existing C path (doxygen → XML → directive). Factor the
  need-synthesis core to be language-agnostic, fed by a doxygen-XML adapter and
  an `ast` adapter over a common intermediate.
- Raw-byte hashing is a **separate** path from `needs.json`; integrity does not
  depend on the doc toolchain.

### 3.3 Grouping (organizational only)

Folder → test suite, file → test group, function → test case, derived from the
**filesystem only**. It structures human-readable content and the sphinx-needs
hierarchy; it never feeds a hash, the Merkle computation, or the satisfaction
check. Its single mechanical use: the outcome extractor maps a pytest nodeid
(`path::class::function`) back to the stable `TS-id`.

---

## 4. Extractors (Python flavour)

Replacing the C/doxygen/twister extractors:

- **Requirements extractor** — reads the sphinx-needs `needs.json` for repo A
  (requirements authored as needs). Thin reader over reproducible `needs.json`.
- **Implementation + test-spec extractor** — `ast` over `seg/` and `test_*.py`
  on branch B: discovers SEG docstring-field functions, computes the four raw
  sub-hashes, reads `:implements:`/`:verifies:` for edges.
- **Test-outcome extractor** — parses pytest result artifacts on branch C
  (e.g. JUnit XML), maps each result to a `TS-id` via the filesystem structure,
  records `repoBSha`, computes `nodeHash`, derives `confirms`/`witnesses`. The
  raw artifacts live on C; the resulting `TestOutcome` node records are
  committed to G (`nodes/test_outcomes.jsonld`) — two steps.

`doc/testreport` is generated, not authored: pytest run → artifacts on C →
outcome extractor → outcome nodes on G; the sphinx `testreport` is optional
human rendering.

---

## 5. Build sequencing and the bootstrap (DEC-004)

- **SWE agent owns** the engine (graph builder, hashing/Merkle, gates, proof
  generator) and both new extractors. Critical path, sequenced first.
- **Iteration 0:** no proof (the prover does not exist yet). DoD = the minimal
  engine's pytest suite is green and it can run the three workflows against
  data. Informed by the prototype.
- **Iterations 1+:** each scopes a complete leaf or complete small subtree (a
  system requirement only once its last child lands — DEC-001), implements +
  test-specs it, runs the suite, the FSM affirms new edges by genuine review,
  then `seg proof generate` over the cumulative scope. The green proof is the
  iteration's integrity DoD.
- **Breadth point:** when all top-level requirements are identified and
  satisfied, a proof additionally carries the human trust judgment. Before
  that, proofs are integrity checkpoints only.
- The `seg` tool ships its own no-op marker support so its implementation
  functions can carry `:implements:` fields pointing at the tool's own
  requirements — plan this into iteration 0.

### 5.1 Agents

| Agent | Owns | Writes to |
|---|---|---|
| Prototype agent | Phase A prototype in `prototype/` | B (or scratch) |
| Requirements Engineer | requirements as sphinx-needs | A |
| Software Engineer | `seg` engine + both extractors + design + implementations | B |
| Test Engineer | test specs; runs the suite | B (specs), C (results) |
| FSM (you) | schema/context, waivers, affirmations, `seg proof generate` | G |

**Affirmation discipline (hard rule).** Agents never affirm. The FSM affirms
pending/suspect *strong* edges by genuine review, using `subHashChanged` and
`CoverageReport.suspectLinks` as the worklist and recording reasoning in
ReviewEvents. Affirmation cannot clear `broken` edges (fix the endpoint) or
stale/suspect-sink states (re-run). As the sole human you are author + reviewer
+ FSM, so these affirmations lack separation of duties — acceptable for
mechanism-validation dogfooding, not a high-assurance safety case.

---

## 6. Open / deferred items

- Namespace genericity: `zephyrproject.org` hardcoded base/vocab; relocation to
  a neutral domain deferred (v4 §14).
- `seg:specId` vs `seg:testSpecId` term consolidation.
- Consolidating on tree-sitter as a single locator engine for C and Python.
- `doc/` sphinx build approach across split worktrees (§2).
- Partial-vs-total top-level scope signal: schema addition to `coverage_report`
  pending (DEC-002).
