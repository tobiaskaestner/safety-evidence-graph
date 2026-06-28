# SEG Decision Log — Development stage

Locked engineering decisions for the real `seg` tool (the core-engine stream).
This is one of two stage-slices of the SEG decision log; **DEC-IDs are globally
unique and stable across both slices**. Full map: `notes/decision_log_index.md`.

**Holds:** DEC-001, DEC-002, DEC-003 (binding half), DEC-004, DEC-005, DEC-006.
DEC-003 is split — its language-agnostic raw-byte-hashing *principle* lives in the
research slice (`research/notes/decision_log.md`); the *Python/marker binding* is
below. The composability/SPDX and direction DECs (007–028) are in the research slice.

**Companion docs:** design-of-record in `development/design/` (design summary,
architecture constraints, python realization, CLI reference); agent briefs in
`development/notes/`.

Status legend: **Accepted** = locked; changing it requires a new superseding
decision entry.

---

## DEC-001 — Hierarchical requirement coverage by transitive closure
 
**Status:** Accepted
 
**Decision.** Requirement coverage is evaluated recursively over the `refines`
DAG, against the full graph (never a partial scope):
- A *leaf* requirement (no incoming `refines` edge) is satisfied iff it has ≥1
  active `verifies` edge and ≥1 active `implements` edge and every confirming
  outcome is PASS or validly waived.
- A *non-leaf* requirement (≥1 child) is satisfied iff every child in the
  graph is satisfied, and any direct `verifies`/`implements` edges it carries
  also pass (**enforce-if-present**).
- A requirement with no children and no coverage edges is a structural
  **orphan**, not vacuously satisfied.
- `refines` MUST be acyclic; a cycle or self-loop is a graph-level error.
- Scoping a non-leaf obligates its entire `refines` subtree; the gate may not
  declare a parent satisfied while any real child is out of scope.
**Rationale.** The flat "every requirement needs ≥1 verifies + ≥1 implements"
rule would flag every system (parent) requirement as a structural gap, since
parents carry only `refines` and no direct coverage — the test dataset (system
→ software requirements) triggers this on day one. Transitive closure also
matches the recursive satisfaction rule's own shape — children discharge
parents. (Earlier drafts cited the §7.2 deep-Merkle traversal as corroboration;
that aggregation was retired in DEC-012, so the rationale now rests on the
satisfaction recursion and the clingo two-answer-set result.) Vacuous-truth, partial-scope, and
cycle holes are closed explicitly because each otherwise yields a *green proof
that lies*.
 
**Consequences.**
- v4 §12.2 flat rule replaced by the leaf/non-leaf rule; new v4 §12.5 states
  satisfaction; v4 §4.6 gains the `refines`-acyclic constraint. (Applied.)
- `CoverageReport.structuralGaps` reports gaps at the leaf, never up the
  ancestor chain; a non-leaf appears only as an orphan.
- WBS: an iteration cannot close by proving a top-level requirement until its
  last child exists; iterations scope a complete leaf or a complete small
  subtree. A system requirement is scoped in the iteration where its final
  child lands.
- Prototype acceptance criterion: the mock dataset must exercise transitive
  satisfaction in both directions — one fully-decomposed parent whose children
  are all satisfied, and one where a single leaf fails and the failure
  propagates to the parent with the gap reported at the leaf.
**Honest limitation.** Proves coverage of the decomposition *as declared and
affirmed*; cannot prove the decomposition is complete. Completeness is human
(see DEC-002).
 
---
 
## DEC-002 — Single repo, four branches as worktrees; trust boundary
 
**Status:** Accepted
 
**Decision (versioning).** One git repository for self-containment, with four
long-lived, never-merged branches checked out as worktrees into one workspace
(mimicking a west multi-repo workspace):
- **A** — requirements (`doc/requirements`, sphinx-needs)
- **B** — implementation + test specs + the `seg` tool source + design doc
  (`doc/design`, `doc/testspec`)
- **C** — raw test results (pytest artifacts; the outcome extractor's input)
- **G** — graph state (`nodes/ edges/ events/ proofs/ config/ schema/`)
The design's repo-G `sync`/`main` split is **collapsed** into the single
FSM-maintained G branch. There is **no CI**; the FSM refreshes link states by
running the sync/extraction step manually at checkpoints. The affirmation
backlog is therefore the set of non-`active` edges (`CoverageReport.suspectLinks`),
not a branch diff.
 
**Decision (trust boundary).** A generated proof is a *mechanical attestation*
("for scope S, the design graph is consistent and the evidence executed and
passed"). Whether it *warrants a safety conclusion* is a human judgment about
whether S captures everything that matters. The three layers: the tool asserts
S is consistent and tested; the tool further reports whether S equals all
top-level requirements *currently in the graph* (the **partial-vs-total scope
signal**); only the human asserts the known top-level set is *complete*. Trust
requires all three. **Per-iteration proofs are integrity checkpoints, not
safety claims.**
 
**Rationale.** Worktree-per-branch preserves the design's distinct repo paths
and four distinct repo SHAs (the EvidenceManifest stays meaningful) while
keeping one repo. Four branches (not three) keep requirements off branch B so
a requirement-text edit triggers re-affirmation only, not a spurious full
test-suite re-run via staleness. Collapsing sync/main is safe because Gate 2
already refuses a proof while any in-scope edge is non-active — the gate
enforces what the branch separation enforced structurally. The trust boundary
matches functional-safety practice (tool yields evidence, assessor yields the
verdict) and prevents over-reading a partial-scope proof as a system claim.
 
**Consequences.**
- The tool MUST compute and surface a partial-vs-total top-level scope signal
  (top-level requirement = one that is never the source of a `refines` edge).
  Pending schema addition to `coverage_report` (a scope-completeness field);
  not yet applied.
- `doc/` is physically split across worktrees A/B/C; the sphinx build approach
  (per-worktree vs consolidated meta-build) is an open repo-layout item.
- Defense-in-depth reduced from two mechanisms (branch separation + gate) to
  one (gate); reintroduce sync/main if this ever goes multi-person.
- For a clean self-attestation, run `seg`@SHA to prove source@SHA at the same
  SHA.
---
 
## DEC-003 (binding) — Python node + marker dialect

**Status:** Accepted

> **Split entry.** DEC-003's language-agnostic raw-byte-hashing *principle* lives
> in the research slice (`research/notes/decision_log.md`). This half holds the
> Python / single-repo binding.

**Decision (Python binding).**
- *Implementation node:* `apiHash` = raw bytes of signature + docstring;
  `bodyHash` = raw bytes of function body. Located via `ast`.
- *TestSpecification node:* `specHash` = raw bytes of test docstring (intent);
  `implHash` = raw bytes of test function body.
- *Marker:* a **docstring field** (e.g. `:implements: SEG-REQ-014`,
  `:verifies: SEG-REQ-014`), symmetric with C's in-comment doxygen `@`-tags,
  and — because the marker lives inside the hashed docstring — re-targeting it
  changes the intent hash and correctly trips the edge suspect. (Decorator is
  the alternative only if marker-outside-the-hash semantics are ever wanted.)
- *Structure / identity / rendering* flow through sphinx-needs and `needs.json`
  (built with `needs_reproducible_json`), kept separate from the raw-byte
  integrity layer.
- *Grouping:* folder/file/function → suite/group/testcase, derived from the
  **filesystem only** (not pytest classes or markers). Organizational and
  human-readable only — it never feeds a hash, the Merkle computation, or the
  satisfaction check. Its one mechanical use is letting the outcome extractor
  map a pytest nodeid back to the stable `TS-id`.

**Rationale.** Docstring-field markers preserve C/Python symmetry and the
existing hash semantics. Grouping must stay out of the integrity layer or a
pure test reorganization (moving a file) would spuriously mark `verifies` edges
suspect — which is why test identity is a stable manual `TS-id`, independent of
name and location.

**Consequences.**
- Concrete landmine for implementers: `ast.get_docstring(clean=True)`
  normalizes indentation — do **not** hash its output; slice the raw source
  byte span (`ast.get_source_segment` is a verbatim slice and acceptable).
- `ast` discards comments, so a `#`-pragma marker is not viable; the marker
  must be in the docstring (chosen) or a decorator.
- Open/deferred: consolidating on tree-sitter as a single locator engine for
  both C and Python (it ships both grammars, preserves comments, gives
  byte-exact offsets) — reversible Phase-B call; `ast` for the prototype.
- Open/deferred: `seg:specId` vs `seg:testSpecId` term consolidation;
  namespace genericity.

**See also.** DEC-003 (principle) for the language-agnostic raw-byte hashing
rationale (research slice).

---

## DEC-004 — Engine ownership and the build-sequencing bootstrap
 
**Status:** Accepted
 
**Decision.** The Software Engineer agent owns the engine (graph builder,
hashing/Merkle, gates, proof generator) and **both** extractors (Python
`ast`-based content extractor; pytest-outcome extractor). This is sequenced
**first** and is critical-path. **Iteration 0** produces no proof — the prover
does not exist yet; its definition-of-done is a pytest-green minimal engine
that can run the three target workflows (consistency check, proof generation,
suspect detection). **Iterations 1+** each generate a per-iteration proof as an
integrity checkpoint; the **breadth point** (all top-level requirements
identified and satisfied) is when a proof additionally carries the human trust
judgment. The FSM (the sole human) affirms pending/suspect edges by genuine
review, recording reasoning in ReviewEvents; **agents never affirm**.
 
**Rationale.** You cannot self-prove the prover before the prover exists
(compiler bootstrapping), so iteration 0 is validated by ordinary pytest. The
engine gates everything else, so its ownership and sequencing must be explicit.
Affirmation has safety value only as a review act; reflexive "clear the
backlog" affirmation makes the integrity model a rubber stamp, and an agent
that auto-affirms is that rubber stamp in automated form.
 
**Consequences.**
- WBS critical path: prototype informs the engine; the engine is the SWE
  agent's first deliverable; RE/TE/SWE content iterations depend on it.
- Affirmation resolves only **pending/suspect strong edges**. It cannot clear
  a `broken` edge (needs an endpoint fix) or a stale outcome / suspect sink
  edge (needs a re-run). Affirmation is not a universal "make it green" button.
- Non-trivial affirmations record a one-line reason in the ReviewEvent
  `comment`; empty comments across the board indicate rubber-stamping and
  defeat the dogfooding of the workflow.
**Honest limitation.** As the single human you are author, reviewer, and FSM at
once — no separation of duties. Acceptable for a dogfooding exercise validating
the *mechanism*; the resulting self-proof attests "the sole developer accepted
this binding," weaker than independent review, and must not be over-read as a
high-assurance safety case.
 
---
 
## DEC-005 — Transitive suspicion auto-clears on descendant re-affirmation
 
**Status:** Accepted
 
**Decision.** `transitivelySuspect` is a **derived** state, not a separately
affirmable one. An edge is `transitivelySuspect` iff a strong-descendant edge is
non-`active` while the edge's own endpoints are unchanged (its `edgeHash` still
matches). It clears **automatically by recomputation** once its descendants
return to `active`. Human affirmation is required only for edges whose own
endpoints changed — `directlyOutdated` (one endpoint's content moved) and
`doublyOutdated` (both) — never for `transitivelySuspect` edges.
 
**Affirmation workflow this implies.**
- **Orient top-down** — start at the top-level affected requirement to see the
  whole affected subtree and grasp the blast radius (navigation only).
- **Affirm at the change sites** — the human reviews and affirms the
  directly/doubly-outdated edges clustered around the node(s) whose content
  actually changed; this is where the judgment call lives.
- **Ancestors clear themselves** — once the changed edges are re-affirmed,
  transitive suspicion on ancestors resolves by recomputation; no separate
  affirmation of unchanged higher-level edges.
**Rationale.** A transitively-suspect edge's own two nodes did not change (only a
descendant did), so re-affirming it would assert something that did not move —
meaningless work that also dilutes the safety value of affirmation. Anchoring
affirmation at the actual change keeps each ReviewEvent tied to a real content
delta, and lets the human review the cause rather than the symptom.
 
**Consequences.**
- The engine computes `transitivelySuspect` as a derived state and re-derives it
  on each recomputation; affirmation sets only `directlyOutdated`/`doublyOutdated`
  edges back to `active`.
- Supports the top-down-orient / change-site-affirm traversal in tooling and the
  CoverageReport `suspectLinks` worklist.
- Related (not part of this decision, tracked separately as candidate
  requirements): the human affirmation **diff** — recording per-endpoint source
  commit SHAs (and endpoint sub-hashes) at affirmation so before→after content
  and the ordered intermediate changes can be reconstructed from source history.
---
 
## DEC-006 — Capture the affirmation anchor now; defer the diff feature
 
**Status:** Accepted
 
**Decision.** Every ReviewEvent records, at affirmation time, the source-repo
commit SHA of each endpoint's repo (`seg:affirmedAt.from` / `.to`) — required.
The human-facing affirmation **diff** (before→after endpoint content and the
ordered intermediate changes) is **deferred** to a later backlog item; only the
data capture is done now.
 
**Rationale.** To affirm a suspect link a human must see what the endpoint looked
like when the link was last active versus now. That is computable — content lives
in the versioned source repos and is recoverable from `source@sha` via the node's
sourcePath and locator (a transient read; the graph still stores only hashes). But
the *anchor* — which source commit each endpoint was at when affirmed — is only
knowable at the moment of affirmation and **cannot be backfilled**: repo G does
not otherwise correlate source-repo SHAs to an affirmation between proofs. So the
field must exist before any affirmation we would later want to diff, even though
the diff feature itself is reversible and can come later.
 
**Consequences.**
- `review_event.schema.json` gains a required `seg:affirmedAt` object (two source
  SHAs, widened 40/64-hex pattern); v4 §ReviewEvent describes its purpose.
- The engine must record both endpoint source SHAs whenever it writes a
  ReviewEvent (including bootstrap bulk affirmations).
- Deferred (candidate RE requirements, via the backlog): the diff retrieval —
  before/after content from `source@affirmedSha` vs HEAD, and the ordered
  per-commit change sequence over `affirmedSha..HEAD`. Requires the tool to read
  source git history (`git show <sha>:<path>`), a new access pattern beyond HEAD.
- Pairs with DEC-005: orient top-down, affirm at the change sites; the diff serves
  the judgment at those directly/doubly-outdated sites.
---
 
