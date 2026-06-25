# SEG Decision Log
 
Binding design decisions for the Safety Evidence Graph (SEG) project. This is
the authoritative, citeable record. The language-agnostic / C-oriented design
of record is the SEG design summary; the concrete Python +
single-repo realization is `seg_python_realization.md`. Agent briefs cite
decisions by ID (DEC-00x).
 
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
 
## DEC-003 — Python node + marker dialect; raw-byte hashing
 
**Status:** Accepted
 
**Decision (hashing principle, language-agnostic).** Content sub-hashes are
computed over **raw source byte spans**. A static parser (Python `ast` now,
tree-sitter later/for C, doxygen for C structure) is a **locator only** — it
identifies the byte span of the intent text and of the body; the SHA-256 is
over the raw bytes of that span. The parse tree, re-serialized or normalized,
**never** enters a hash. Span boundaries are defined parser-independently so a
parser/grammar version bump does not shift a span and rebreak hashes. This
applies to C too: the C intent hash is over the raw doxygen-comment bytes in
the source file, **not** over the doxygen-XML-reflowed text.
 
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
**Rationale.** A static parser mirrors doxygen (which never executes C);
autodoc would import/execute the module and cannot yield raw body source, so
it is unsuitable for the execution sub-hash. Raw-byte hashing keeps the crypto
anchor bound to the exact bytes a reviewer reads and decouples integrity from
doxygen/sphinx-needs/grammar version churn. Docstring-field markers preserve
C/Python symmetry and the existing hash semantics. Grouping must stay out of
the integrity layer or a pure test reorganization (moving a file) would
spuriously mark `verifies` edges suspect — which is why test identity is a
stable manual `TS-id`, independent of name and location.
 
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
 
## DEC-007 — Graph-type meta-model & configurable satisfaction (future direction; v1 seams now)
 
**Status:** Accepted (direction + the v1 seam constraint are binding; the meta-model
design itself is future work)
 
**Decision.** SEG will evolve from a hardcoded taxonomy toward a configurable
*graph-type definition*, in layered versions:
- **v1** — fixed vocabulary, fixed satisfaction (current; self-hosting dogfood).
- **v2** — configurable **vocabulary**: node types, edge types (endpoint types,
  direction), the **strong** flag, and the **logical hash-field selection** per
  node type.
- **v3** — configurable **satisfaction logic**.
**Boundaries (what generalizes, what does not).**
- **Generalize the vocabulary and the satisfaction predicate.** What varies per
  domain is the vocabulary and what "satisfied/valid" means for that graph.
- **Keep the integrity mechanics fixed and universal:** content→hash binding,
  suspicion propagation along strong edges, Merkle over strong edges, and the
  link-state semantics are SEG's invariant core, parameterized by the declared
  vocabulary but never redefinable per graph type. Making them configurable would
  dissolve SEG's identity into a generic rules engine.
- **Hash-field layering (preserves DEC-003).** The graph-type definition picks the
  *logical* hash-field structure per node type; the language binding still maps
  each logical field to raw source byte spans via the parser-as-locator discipline.
**Satisfaction language — must be a decidable, auditable formalism, not a
Turing-complete one.** Satisfaction rules decide proof validity, so they are part
of the trusted base and must be **terminating, deterministic, side-effect-free,
and human-auditable**. The chosen target is **stratified Datalog**: recursion and
transitive closure (the `refines` subtree) are native, stratified negation covers
"no failing outcome unless waived", existence/universal conditions cover the edge
requirements, and termination with a deterministic fixpoint is guaranteed. A
general functional or Prolog-style logic language, or arbitrary Python compiled to
the VM, is explicitly **rejected** for the default/safety path: Turing-completeness
is an anti-feature here (non-termination, non-determinism, unauditable proof
logic, arbitrary code in the evaluation path). Embedding a stratified-Datalog
evaluator is a bounded, textbook task. Any Turing-complete escape hatch, if ever
offered, is an explicitly-"unsafe", non-safety-graph mode — never the default.
 
**Trusted base & proof binding.** The vocabulary definition, the hash-field
selection, and the satisfaction ruleset are all security-relevant config: each
changes what a hash or a "satisfied" verdict *means*. When configurable, each must
be versioned, hashed, and **bound into the proof** (a proof records which
definition/ruleset, at which version, produced it), or two parties could compute
different "valid" proofs of the same graph.
 
**Binding v1 constraint (the actionable part — see the architecture constraints
doc).** The v1 engine must isolate, behind clean internal seams:
1. the **taxonomy** (node/edge types, strong flag, hash-field selection) behind a
   single graph-model/schema provider, populated by hardcoded constants framed as
   "the built-in safety-evidence graph type"; and
2. **satisfaction** as a pure, deterministic, side-effect-free predicate over the
   typed graph, behind a `SatisfactionEvaluator` interface (v1's DEC-001 logic
   lives in that form — already essentially a Datalog program written in Python).
So v2 becomes a provider swap and v3 an evaluator swap, not rewrites.
 
**Rationale.** A meta-model is the natural evolution (cf. SHACL/ShEx, GraphQL SDL,
ontologies) and the feedback shows clear demand. Deferring the build but respecting
the seams now is nearly free while the engine is being written and very expensive
to retrofit. The decidability constraint is what keeps a configurable safety tool
trustworthy.
 
**Consequences.**
- Architecture constraints AC-001 (taxonomy seam), AC-002 (satisfaction seam),
  AC-011 (trusted-base config proof-bound), AC-013 (integrity mechanics fixed)
  derive from this decision.
- Does **not** touch the v1 backlog; the meta-model, the definition format, the
  TCB/versioning, and the Datalog evaluator become their own requirements when the
  relevant version is taken up.
---
 
## DEC-008 — Additional interfaces (REST) are a future direction; engine-as-library now
 
**Status:** Accepted (direction + the v1 engine-as-library seam are binding; any API
itself is future work)
 
**Decision.** SEG may grow interfaces beyond the CLI (notably a REST API). These are
a future direction, not v1, and do not touch the v1 backlog. The binding v1
constraint is structural: the engine is a **library with a clean programmatic
core**, and the CLI is a **thin presentation layer** over it (AC-014). Any later
interface — REST, a review UI, a TUI — is then a thin adapter over the same core,
not a rewrite (the interface analog of the AC-003 input-adapter seam).
 
**Split: query vs manipulate.**
- A **read/query** surface (suspect-link worklist, CoverageReport, readiness, a
  sealed proof) is the safe, valuable half. It is a view over **committed** state —
  it must read committed HEADs, never mutable working trees, or reproducibility is
  lost.
- A **write/manipulate** surface conflicts with the locked model unless tightly
  constrained: the graph is mutated by **git commits** (DEC-002), affirmation is a
  **human judgment** the FSM operates (DEC-004, AC-006), and provenance comes from
  **git log**. A headless write-through API would bypass all three and reintroduce
  the rubber-stamp failure mode.
**Permitted shape for a write API.** Only as the **backend of a human-in-the-loop
review surface** that commits with the human's git identity — preserving provenance
and human judgment. This is the natural home for the deferred affirmation diff
(DEC-006: before→after content + ordered changes, human reviews then affirms). The
bright line is **human-in-the-loop + git-committed**; headless automation of
`affirm` or proof generation is never permitted.
 
**Constraints any future API must respect.** Read committed state (reproducibility);
no headless write-through to the authoritative graph; affirm and proof generation
remain human-operated authority (AC-006); authentication/audit are required before
any multi-user deployment (a running service is an attack surface a single-user CLI
is not).
 
**Rationale.** The query half has clear integration value; the write half is
speculative and largely against the grain unless framed as a human review backend.
Either way, the engine-as-library seam is nearly free now and expensive to retrofit
once logic has settled into the CLI handlers — and the SWE is building the CLI and
engine now.
 
**Consequences.**
- Architecture constraint AC-014 (engine-as-library / thin CLI) derives from this.
- No v1 backlog impact; the API surface, its auth/audit model, and the review UI
  become their own requirements when that version is taken up.
---
 
## DEC-009 — Configurable repo topology (source-binding facet of the DEC-007 meta-model)
 
**Status:** Accepted (direction + the v1 config seam are binding; the configurable
topology itself is future work, paired with DEC-007)
 
**Decision.** The repo topology — how many repos exist, their names, their roles,
and which node types draw their source from which repo — becomes user-configurable.
This is not a new axis: it is the *content-source/topology facet* of the DEC-007
graph-type meta-model ("where a node type's source lives" is an attribute of the
node type). v1 ships the built-in four-repo safety topology (A=requirements,
B=impl+testspec, C=outcomes, G=graph); v2 externalizes it alongside the vocabulary.
 
**Fixed core stays fixed.** Staleness, hashing, and Merkle do not change. Staleness
in particular generalizes for free: an outcome's freshness binds to the HEAD of the
repo holding the source it depends on (the witnesses→implementation→source-repo
chain). You do not configure staleness *semantics* — you configure the *source
mapping*, and the binding follows. Keep the mechanic; make the binding data.
 
**What becomes configurable (the bindings).**
- The set of repos, their names, and their roles (source-for-node-types,
  graph-store, artifact-store) — today hardcoded A/B/C/G.
- The node-type → source-repo mapping (today requirements→A, impl/testspec→B,
  outcomes→C) — part of the DEC-007 node-type definition.
- Already config today: `seg.yaml` maps repo names to physical paths/worktrees, so
  the *physical* mapping is done; only the count/names/roles are hardcoded.
**Trusted base & proof binding (as DEC-007).** The topology is security-relevant —
it determines what a proof anchors to. So when configurable it is versioned and
proof-bound. Concrete future schema touch-points: the node schemas' `sourceRepo`
**enum** (`repoA/B/C`) loosens to a config-validated logical repo name; the
`EvidenceManifest`'s four fixed SHA fields (`repoASha…repoGSha`) become a
`{repo-name → SHA}` map of arbitrary cardinality; and the `snapshotId` hash is
taken over the configured repo-SHA set rather than a fixed four.
 
**Binding v1 constraint.** The engine — especially the extractors and the
manifest-writer (the imminent self-hosting slice) — reads the repo set, roles, and
node-type→source mapping from config; it does not scatter `repoA/repoB/...` literals
through the code. v1 populates this with the built-in four-repo safety topology
behind the config seam. See AC-015.
 
**Rationale.** Same generalization family as DEC-007/DEC-008, applied to the repo
dimension; recording it now with a cheap v1 seam is near-free while the extractors
are being built and a rewrite if retrofitted. Keeping it future-direction-plus-seam
(not v1 work) is what keeps the "generalize everything" pull from derailing the
self-hosting goal.
 
**Consequences.**
- Architecture constraint AC-015 (repo topology behind config) derives from this.
- Future schema changes (deferred): `sourceRepo` enum → config-validated name;
  `EvidenceManifest` fixed SHAs → named map; `snapshotId` over the configured set.
- No v1 backlog impact; the configurable topology ships with the DEC-007 vocabulary
  work as one meta-model version.
---
 
## DEC-010 — Compositional (assume-guarantee) proof
 
**Status:** Accepted (direction recorded; major future capability — v3+/north-star.
v1 only preserves the enabling invariants. Does not touch the v1 backlog.)
 
**Decision.** A proof may rely on another project's sealed proof rather than
re-proving an imported component. The product maker imports the requirement
*boundary* of a dependency (e.g. the Zephyr RTOS requirements it relies on),
pinned by content hash, and references the dependency's sealed proof as the
evidence that discharges them. This is **assume-guarantee composition**: the
product *assumes* the imported requirements hold; the referenced proof *guarantees*
them; the composition is valid **iff the product's assumptions are a subset of the
scope that proof actually proved**.
 
**Modeling (extends the existing design, does not replace it).**
- New concept: an *imported requirement* node (pinned by hash) and a
  `dependsOn`/`imports` edge to it; the *evidence* is an external-proof reference,
  not internal verifies/implements edges. This is **not** a Waiver (a waiver excuses
  a failure; this is positive evidence sourced from elsewhere).
- DEC-001 satisfaction gains a **third discharge case** alongside leaf (direct
  coverage) and non-leaf (children satisfied): an imported requirement is satisfied
  iff a valid, scope-covering external proof attests it. Composes cleanly with the
  configurable/Datalog satisfaction direction (DEC-007) — it is just another rule.
- The external proof is **referenced and fingerprinted** (snapshotId, Merkle root,
  repo SHAs, proven scope) in the EvidenceManifest — **not** folded into the
  product's Merkle. The product's design fingerprint stays self-contained; the
  evidence half points outward (the existing design/evidence separation).
**Two non-negotiable soundness checks.**
1. **Scope-match** — every imported requirement the product depends on must lie
   within the scope the referenced proof actually covers (assumptions ⊆ proven
   scope), or the composition is refused. This makes the partial-vs-total scope
   signal (DEC-002) load-bearing; every proof already publishes its scope.
2. **Version-pin** — imported requirements are pinned by hash to the proved version;
   upgrading the dependency makes the reference stale until re-validated
   (cross-graph staleness, the boundary analog of repo-B staleness; rhymes with the
   DEC-006 anchor).
**Trust stays verifiable.** The auditor's chain extends: verify the product proof →
it references the dependency proof → verify that independently by recomputing its
Merkle root from its nodeManifest (already supported). A product proof can also
mechanically distinguish **discharged** external assumptions (backed by a verifiable
covering proof) from **undischarged** ones (merely asserted) — the composability
analog of the partial-vs-total signal and an honest extension of integrity-vs-trust.
 
**Hard prerequisite this surfaces.** Cross-project composition requires
globally-unique, stable requirement IRIs. The **namespace genericity deferred in
v4 §14 / DEC-002** therefore stops being optional — two projects cannot compose if
their IRIs collide. Composition is the capability that will force that item.
 
**Binding v1 constraint (light).** No new v1 code; v1 must only *preserve the
invariants* composition will need: proofs independently verifiable, scope published
explicitly in every proof, requirement IRIs globally unique and stable, and the
satisfaction evaluator (AC-002) extensible to a new discharge case.
 
**Consequences.**
- Architecture constraint AC-016 (preserve composition-enabling invariants).
- Future schema/work (deferred): imported-requirement node + `dependsOn` edge +
  external-proof-reference evidence; EvidenceManifest section for referenced proofs;
  the scope-match and version-pin checks; resolution of the namespace prerequisite.
- No v1 backlog impact; lands well after the DEC-007 meta-model and the namespace
  story.
---
 
## DEC-012 — Retire `deep` fingerprint aggregation; design commitment is a flat set-commitment, openable sub-mode reserved for selective disclosure
 
**Status:** Accepted (partially supersedes the v4.1 §7 deep-Merkle design; refines
the `fingerprint` facet of DEC-007)
 
**Decision.**
- The design commitment is computed as a **`flat` set-commitment** over the
  design-graph node/edge set (canonical sort of ⟨from, to, type⟩ edge tuples + node
  hashes, hashed to a root) — **not** by recursive topology-aware aggregation up the
  `refines` DAG.
- The `fingerprint` facet's `flat` mode splits into two sub-modes:
  - **`flat-sealed`** — accumulate the sorted set to a single scalar root. The
    default; serves the global recomputable commitment and tamper-evidence. No member
    opening.
  - **`flat-openable`** — commit to the sorted set as a Merkle tree and retain it, so
    individual members open with O(log n) inclusion paths (a vector commitment).
    Reserved for authority-decoupled selective disclosure.
- **`deep` is retired, not removed.** It remains defined in the facet vocabulary as a
  topology-aware aggregation mode with **no current consumer**, re-openable if a
  future use genuinely requires per-node topology-bound aggregates. No built-in graph
  type sets it; the engine need not compute it.
**Rationale.** A sweep for any verifier that needs `deep`'s distinctive property —
non-localising, topology-aware aggregation up the DAG — found none:
- *Tamper-evidence / topology binding* is delivered by a flat commitment over the
  **edge set**: rewiring, adding, or removing an edge changes the set and the root.
  `deep` adds per-node aggregate *values* that are non-localising by spec and that
  nothing reads.
- *The global recomputable proof* (paper contribution 2; design summary Goal 1) is a
  "recompute the whole case" property — a flat-scalar property. The verifier holds the
  full nodeManifest and recomputes; full-disclosure-and-recompute is the regime in
  which flat and deep are equivalent.
- *Composability (DEC-010)* verifies a foreign proof by recomputing its Merkle root
  from the full nodeManifest (AC-016) — also full-disclosure-recompute, no selective
  opening. `deep` earns nothing there either.
- *Satisfaction* is a Datalog fixpoint over `refines`, independent of the commitment
  layer; it never needed `deep`.
The one genuinely tree-unique capability is **succinct selective opening** — proving
one member is in the committed set while withholding the rest (Bitcoin SPV is the
archetype: light clients verify inclusion against a header without the block). SEG's
analogue is cross-organization selective disclosure (a silicon vendor opens its
boundary requirements to a product maker while withholding its witnessing/evidence
nodes). Two findings bound it:
1. Even there, an authority signature (a notified body signing the disclosed subset,
   or signing per-guarantee claims) substitutes for an inclusion proof — so a tree is
   required only when disclosure must be **holder-generated and authority-decoupled**
   (one seal → many holder-minted disclosures, each provably a face of the signed
   version).
2. When it *is* required, the gain over the flat alternative (ship the complement
   hashes, O(n)) is purely **succinctness**: O(k log n) openings vs O(n) per
   verification event. At ~100 boundary nodes in a graph of ~10k–50k, the asymptotic
   gap is ~15–54× but the absolute flat cost is sub-MB and low-ms — so adoption is a
   **scale-and-frequency bet** (many consumers × many versions), not a correctness
   need.
Crucially, this capability is a refinement of **`flat`**, not `deep`: what opens is a
flat membership claim about individual boundary nodes. `deep`'s recursive content-fold
up `refines` has no clean per-node inclusion path and cannot deliver it. So the same
analysis retires `deep` and motivates `flat-openable`.
 
**What does not change.** "Retire `deep`" is not "retire Merkle." `flat-openable` is
itself a Merkle tree (over the set). The local/global two-mode commitment (`edgeHash`
local + a global design root), the sealed proof object, and the global recomputable
commitment all survive — one aggregation mode is excised, the commitment layer is
intact.
 
**Consequences (revisions this entry authorizes; applied in order).**
1. `seg_prior_art.md` + `seg_reconciliation.md` Layer 4 — fix the crypto attribution:
   vector-commitment / logarithmic-opening belongs to `flat-openable`, not `deep`;
   reclassify `deep` as structure-binding with no consumer; correct the "`flat` =
   accumulator with membership proofs" overclaim (`flat-sealed` is a non-openable
   scalar).
2. `seg_glossary.md` + `seg_definition_language.md` — split `flat` into `flat-sealed`
   / `flat-openable`; mark `deep` retired (defined, dormant).
3. `knowledge_graph_design_summary_v4.1.md` §7 — re-spec the design root from deep
   transitive-closure aggregation to a `flat-sealed` commitment over the design-graph
   set; adjust AC-007/AC-013 wording (Merkle survives; "deep/transitive" wording goes).
4. `seg_paper_seed.md` §3.2/§4/§6 — the global recomputable commitment is `flat`, not
   "two-mode/deep"; revise the "deep-fingerprint union" acyclicity invariant.
5. Entailment lattice — the `deep ⟹ acyclic` (hard) arrow loses its antecedent;
   `refines` acyclicity now rests solely on the satisfaction-role (soft) entailment,
   which `seg_demo_clingo_verdict.py` already established as a reproduced result (two
   answer sets on a cycle).
6. Cross-ref cleanup: DEC-001's rationale clause ("the only rule consistent with the
   §7.2 Merkle traversal, which already aggregates a parent from its in-neighbours")
   cites deep aggregation as corroboration; transitive-closure satisfaction stands on
   its own and on the clingo result, but that clause should be reworded.
**Honest limitation / still open.**
- `flat-openable` mechanics are unspecified — sibling sort order, inclusion-path
  format, multiproof sharing across the boundary set (the residual Merkle-detail item
  in the open threads).
- The scale threshold above which `flat-openable` pays for itself is a deployment bet,
  not a settled number; the Zephyr-SoC supply-chain shape (one NB signature for many
  makers vs NB-in-the-loop each time) is the deciding variable and is not yet confirmed.
---
 
## DEC-013 — v1 self-hosting drops the global commitment layer; `fingerprint` deferred to the composability phase
 
**Status:** Accepted (supersedes the v1-scope clause of DEC-012 — i.e. its consequence
that v1 computes a `flat-sealed` root; leaves DEC-012's facet vocabulary intact)
 
**Decision.**
- v1 self-hosting has **no global commitment layer**. v1 integrity is:
  - **`edgeHash`** (`binds`) — local, content-bound, affirmation-time integrity; the
    basis of drift detection. **Not droppable.**
  - **FSM signature over the sealed bundle** — global, authority-attested integrity.
- The entire `fingerprint` layer — the design root and all of its modes (`flat-sealed`,
  `flat-openable`, `deep`) — is **deferred to the composability phase (Phase C)**. It is
  removed from the v1 spec, not from the model.
- v1 edge facets reduce to **`binds` + `propagates` + `acyclic`-on-`refines`**. The
  `acyclic` constraint is *not* part of `fingerprint`; it rests on the satisfaction-
  recursion entailment (`satisfaction-role ⟹ acyclic`), independent of any commitment.
  "v1 `strong`" is therefore exactly `binds` + `propagates`.
**Rationale.** In v1, nothing consumes a content-derived global root that the FSM's
signature does not already cover:
- *Seal the scope* and *fix the verdict input* are both delivered by a signature over
  the canonical bundle bytes — a signature over the contents commits to the contents.
- *Version-pin / third-party recompute / selective opening* are composability and
  disclosure jobs, and v1 has none of them.
This is the disclosure lesson one level deeper: a trusted signer substitutes for a
recomputable commitment (as the notified-body signature substituted for an inclusion
proof in the DEC-012 analysis). In v1 the FSM **is** the authority, so authority-
attested global integrity is the correct model; a signer-independent, recomputable
root earns its place only when a verifier will not rely on the producer's signature —
i.e. cross-org composability. `edgeHash` stays because it solves the original "binders
go stale" problem locally and no signature replaces it. `acyclic`-on-`refines` stays
because satisfaction is unsound on a cyclic spine (the clingo two-answer-set result),
independent of the commitment layer.
 
**Consequences.**
1. `knowledge_graph_design_summary_v4.1.md` §7 — **remove** the design-root / Merkle
   section from the v1 spec, marked *deferred to Phase C* (this replaces DEC-012
   consequence 3, which had re-spec'd §7 to `flat-sealed`). Revisit the Merkle-related
   v1 invariants (AC-007 determinism scope, AC-013 "Merkle over strong edges", AC-016
   "root recomputable from nodeManifest") — drop or mark deferred.
2. `seg_definition_language.md` — `fingerprint` retained as a model capability, noted
   outside the v1 slice (applied).
3. `seg_paper_seed.md` — reframe "three cryptographic commitments": **two in the
   self-hosting core (`nodeHash`, `edgeHash`) + a third (the design root) that earns
   its place only at composition scale** (sharpens DEC-012 consequence 4).
4. Entailment lattice — the v1 lattice carries only `binds`, `propagates`, and
   `acyclic` (satisfaction-role); `fingerprint` and its `deep ⟹ acyclic` arrow are
   absent from v1 entirely (consistent with DEC-012's dormancy ruling).
**Honest limitation / dependency.**
- This rests on the v1 sealed proof actually carrying an **FSM signature over the
  canonical bundle bytes**, so that "the signature commits to the contents" holds. If
  the v1 seal is not yet defined as such a signature (cf. the affirmation anchor,
  DEC-006), that must be pinned down — it is now the *sole* global-integrity mechanism
  in v1, so its definition is load-bearing.
- Phase C reintroduces the global commitment (`flat-sealed` default, `flat-openable`
  for disclosure) per DEC-012; this entry defers it, does not delete it.
---
 
## DEC-014 — v1 keeps a `flat-sealed` design root as its seal; supersedes the "remove the global layer" half of DEC-013
 
**Status:** Accepted (supersedes DEC-013's removal-of-the-global-commitment clause and
its consequence 1; leaves intact DEC-013's deferral of the *configurable* `fingerprint`
facet and DEC-012's retirement of `deep`)
 
**Decision.**
- v1 **retains a global design commitment**: a `flat-sealed` design root computed
  directly over the fixed design set + metadata —
  ```
  designRoot = SHA256( canonicalJSON(metadata)
                       ‖ sorted(nodeHash(n) for n in design nodes)
                       ‖ sorted(edge-tuple for design edges) )
  ```
  No recursive per-node aggregation. This is v1's seal, snapshot fingerprint, and the
  auditor's recompute target.
- The `nodeManifest` stores per-node `nodeHash` only; the per-node `merkleHash` field
  is dropped (no aggregation to store).
- v1 has **no per-edge `fingerprint` facet** and **no signature**. The root is computed
  over the hardcoded design set (`refines`/`verifies`/`implements` + their nodes); v1
  edges carry only `binds` + `propagates` (+ `acyclic`-on-`refines`). The configurable
  `fingerprint` facet, `flat-openable`, and `deep` remain Phase-C (DEC-012, DEC-013).
- Whether to add an FSM signature over the root is a separate, additive future
  decision; not taken here.
**Rationale.**
- The seal check that prompted this found v1 has **no signature**: the global integrity
  mechanism *is* the root (§7.3, "the cryptographic fingerprint of this proof") plus the
  repo-G commit under the Authorised Committer List (§8.3); the affirmation anchor
  (DEC-006) is per-edge provenance, not a global seal. DEC-013 assumed a signature and
  proposed removing the root on that basis — an over-reach. Removing the root with no
  signature would leave v1 with no cryptographic global integrity and no recompute
  target.
- The complexity DEC-012/DEC-013 rightly objected to is the *deep per-node aggregation*
  (§7.2), not the root. A `flat-sealed` root is strictly simpler to implement (one
  canonical sort + one hash; no recursion, no acyclicity precondition) and preserves the
  seal and the verify-by-recompute workflow.
- "v1 edges are only bind+propagate" is preserved: the configurable `fingerprint` facet
  defers, while the root is computed over the hardcoded design set, so no v1 edge carries
  a fingerprint setting.
**Consequences.**
1. `knowledge_graph_design_summary_v4.1.md` §7 — re-spec §7.2 from deep transitive-
   closure aggregation to the `flat-sealed` design-root formula above; §7.3 root folds
   node/edge hashes directly rather than top-level per-node merkleHashes; drop per-node
   `merkleHash` from §2.6 and the `nodeManifest`. (Restores DEC-013 consequence 1 to a
   *re-spec*, not a removal.) Re-word AC-013 ("Merkle over strong edges" → "flat-sealed
   root over the design set"); AC-007 (determinism) and AC-016 (root recomputable from
   `nodeManifest`) still hold.
2. `seg_paper_seed.md` — the global recomputable commitment in the self-hosting core is
   the `flat-sealed` design root (not `deep`, not "two-mode"); the `flat-openable`/
   disclosure tier earns its place only at composition scale (DEC-012). [sharpens
   DEC-013 consequence 3]
3. `seg_definition_language.md` — the DEC-013 note ("v1 integrity is `edgeHash` + the
   FSM signature over the sealed bundle") is **inaccurate on the signature point** and
   is corrected to: v1 integrity is `edgeHash` (local) + the `flat-sealed` design root
   (global); the configurable `fingerprint` facet defers to Phase C.
**Honest note.**
- v1's seal remains governance-plus-fingerprint (root + Authorised Committer List + git),
  not a cryptographic signature. Adequate for self-hosting where the FSM controls repo G,
  but it is the natural place a future signature decision would land — flagged, not
  resolved.
---

## DEC-015 — `residual` is the product's authored `A_up`; a broken/incomplete reliance is `unsatisfied`, not residual

**Status:** Accepted (re-sources the residual definition in `seg_composability_cbd` §8–§9; supersedes the earlier "complement of `discharged` among the product's `relies-on` targets" definition)

**Decision.**
- The **residual** of a proof is the set of the product's *own authored* conditions of use — `assumes` edges issued by a *local (non-referenced)* guarantee — published as the proof's `A_up`. Derived from the graph, never stored, recomputes under drift.
- A **broken or incomplete reliance is `unsatisfied`, never a residual.** A `relies_on` edge is a commitment to discharge the refinement locally (seal verifies, the upstream implementation is linked, and every *sealed* `assumes` condition of the relied-on guarantee is discharged). A failed commitment is a defect of this product; exporting it as a published condition of use would invert the safety-manual semantics.
- The verdict layer reports three proof-scope states over the **in-scope (non-referenced) product** requirements: **total** (a non-empty scope with no gap and nothing published as `A_up`), **conditional** (no gap, but `A_up` published), **unsatisfied** (some in-scope gap). `unsatisfied` dominates `conditional` — a published `A_up` can never mask a genuine gap.

**Rationale.**
- The residual and an unmet reliance are categorically different: the former is a deliberately-authored, downstream-facing condition; the latter is an internal failure. Collapsing them (the old "complement of `discharged`") would let a broken import be re-badged as a conditional proof and handed onward — the opposite of what a safety manual is for.

**Consequences.**
1. `residual(C) :- assumes(G, C), not referenced(G)` (authored, local). The incomplete-reliance case is folded into `unsatisfied` via the mode-2 failure clauses (`not reliance_seal_ok`, `not reliance_uses_ok`, and the sealed-condition poison rule).
2. Proof-scope rollup made concrete: `product/1`, `proof_unsatisfied`, `proof_has_residual`, `proof_total` (guarded by a non-empty-scope `has_product`, so an empty/all-referenced graph is not vacuously "total"), `proof_conditional`. Realised in `seg_example_v1_plus_composition.dsl` and exercised in `seg_demo_clingo_partial_discharge.py` (5/5) and `seg_demo_clingo_composition_v2.py` (9/9).
3. `seg_composability_cbd` §8 residual definition and §9 three-state framing updated (v6); the §9 positive-`discharged` stratification sketch is left as illustrative pending a separate reconciliation to the composition grammar's `unsatisfied`-recursion idiom.

**Honest note.**
- Under the composition grammar's positive-recursion `unsatisfied` idiom a reliance cycle is a benign positive loop, so the single-answer-set determinism guardrail stays *silent* on it. Well-foundedness therefore rests on the explicit `acyclic` facet (a structural closure check), not on the verdict engine's determinism — a demotion of the guardrail's role relative to the earlier positive-`discharged` sketch.
---

## DEC-016 — SHACL/Datalog responsibility boundary; test-outcome completeness is a verdict-layer check

**Status:** Accepted

**Decision.**
- **SHACL** is responsible for *structural soundness only*: each edge that exists is well-typed (an allowed source/target node-type pair and direction, with its required edge fields/hash/state) and each node is well-formed (intrinsic fields, hash structure). SHACL does **not** enforce mandatory edge *presence* on a node.
- The **Datalog verdict layer**, operating on a structurally-sound graph, is responsible for detecting the *missing information that precludes a positive verdict* — including absent or incomplete coverage. (Precedent: the DEC-001 orphan leaf is a verdict-layer gap, not a SHACL rejection.)
- Therefore "a Test Outcome is valid audit evidence only if it carries **both** a `confirms` and a `witnesses` edge" is a Datalog check — `valid_outcome(O) :- confirms(O, _), witnesses(O, _)`, gating `spec_ok` — **not** a SHACL constraint.
- An invalid (incomplete) outcome is **discarded** — treated as absent — mirroring the projection-time discard of stale outcomes. A valid PASS alongside an invalid non-PASS therefore yields `satisfied`.

**Rationale.**
- Consistency: no other node type carries a SHACL mandatory-edge-presence constraint; the test-outcome co-presence rule would be the sole exception. (Verified against the SHACL projection: its `sh:minCount` constraints govern the *fields of an edge that exists* — `from`/`to`/`edgeHash`/`state` — never "a node must own edge X.")
- Precedent: DEC-001 already locates "missing required coverage" (the orphan leaf) at the verdict layer.
- Placement, not capability: SHACL *can* express co-presence (`sh:minCount` over the inverse path); this is a deliberate boundary choice, not a workaround.
- Occam: discard-invalid reuses the existing staleness-discard disposition rather than introducing a second handling path for untrustworthy outcomes.

**Consequences.**
1. `valid_outcome(O) :- active_edge(_, confirms, O, _), active_edge(_, witnesses, O, _)` enters the base rule-set; mode-A `spec_ok`/`spec_fails` are gated on it.
2. Paired (not a separate decision) with the faithful realisation of the **DEC-001 universal** for mode A: a spec is ok iff it has ≥1 *valid* confirming outcome and *no* valid confirming outcome is an unwaived non-PASS — replacing the earlier existential `spec_ok` and adding `excuses`-based waiver handling. DEC-001 already states "every confirming outcome is PASS or validly waived."
3. Fixtures must supply a `witnesses` edge on each test outcome; the v1 partial-discharge fixture's `toa` lacked one and is flagged by the new gate.
4. Realised and exercised in `seg_demo_clingo_partial_discharge_v2.py` (10/10): the five carried-over three-state scenarios plus 6–7 (DEC-001 universal + waiver), 8 (incomplete outcome), 9–10 (enforce-if-present, both directions). This module supersedes `seg_demo_clingo_partial_discharge_v1.py`, which is discarded.
5. SHACL still type-checks the `confirms` (TO→TS) and `witnesses` (TO→Impl) edges that do exist; outcome *freshness* (`repo_b_sha` staleness) remains a projection-time filter.

**Honest note.**
- An outcome carrying both edges but *no* `outcome` field reads as passing (no FAIL to detect). That is node well-formedness — a SHACL responsibility under this very decision — so it is correctly outside the verdict layer, but it is a standing assumption the rule-set rests on (a SHACL shape requiring the `outcome` field closes it).
- These base-verdict corrections (consequence 2) are reflected in the v2 demo and this log, but **not yet** in the design summary's verdict section (`knowledge_graph_design_summary`, still v5.1 and otherwise stale); that reconciliation is a separate, larger pass.

---

## DEC-017 — Re-type the imported upstream guarantee as a `Guarantee` node; reliance edge becomes `covers` (Guarantee → Requirement)

**Status:** Accepted (refines the DEC-010 / DEC-015 composition modeling; supersedes the `relies_on(R, G_up)`-into-`Requirement` form in the v7 demos, fixture, and `seg_composability_cbd` §8–§9)

**Decision.**
- **Move 1 — typing.** The imported upstream guarantee `G_up` is re-typed from `Requirement` to a new node type **`Guarantee`**. The satisfaction recursion (`leaf` / `unsatisfied` / `satisfied` / `product`, all headed by `node(R, "Requirement")`) no longer ranges over it, so the spurious `unsatisfied(g_up)` the scope filter previously masked is eliminated at the source — the type system now enforces what the `product`/`referenced` split did by hand.
- **Move 2 — direction.** The reliance edge is flipped from `relies_on(R, G_up)` (R → G_up, outward) to **`covers(G_up, R)`** (Guarantee → Requirement). Every discharge edge — `refines`, `verifies`, `implements`, `reviews`, and now `covers` — points *from the contributor into the requirement it discharges*. The upstream guarantee thus reads as a third discharge kind, but reliance keeps its four conditions explicit as its own mode (refinement affirmation = `covers` active; seal verifies; impl-uses-impl; every sealed `assumes` condition discharged) — it is **not** flattened into a bare witness.
- **Naming.** `Guarantee` is the CBD term for `G_up` (Benveniste et al. 2018, §2; already listed as a `seg_composability_cbd` §12 glossary delta), chosen over the ungrounded `claim`. `covers` is grounded in the doc's own §8 affirmation phrasing ("`G_up` covers the downstream need"). Intra-project `refines` (decomposition, child → parent) is unchanged and kept lexically distinct from the CBD-refinement `⊑` that `covers` encodes, per the §2 two-lattices warning. The concept predicate `reliance/1` is renamed `covered/1` for surface↔predicate symmetry with the `covers` edge.

**Rationale.**
- Removes a latent footgun: any future rule reading `unsatisfied/1` without the `product` guard would have picked up the masked junk atom.
- Directional symmetry across all discharge edges aids explainability and matches CBD §4 (`C_up ⊑ C_slot` — the upstream contract refines the slot R carries).
- Rules are work-in-progress; consistency in the authoritative demo is worth re-keying four working clauses (decided this session).

**Consequences.**
1. **Typing / EDB.** `node(g_up, "Guarantee")`; new edge `covers` (domain `Guarantee`, range `Requirement`); `relies_on` retired. Upstream `assumes` now has a `Guarantee` source, so `assumes` domain widens to `Requirement | Guarantee` (local authored-assumes keep their `Requirement` source); `referenced_under` anchors a `Guarantee` under a manifest.
2. **Verdict bodies — four clauses re-keyed** `relies_on, R, G` → `covers, G, R`, with the concept predicate renamed: `covered/1` (was `reliance/1`), `reliance_seal_ok/1`, `reliance_uses_ok/1`, and the sealed-condition poison rule. `residual`, the `referenced`/`product` split, `discharged_otherwise`, and the three-state rollup are unchanged in body; verdict output is identical. (The two `reliance_*_ok` helpers retain their stem — they name the check *on a reliance*; a sweep to `covered_*_ok` is a trivial follow-on if full stem-symmetry is later wanted.) A *fifth*, structural clause also re-keys — see 2a.
2a. **Structural acyclic-facet check — a fifth clause re-keys (finding from the validation demo).** The `acyclic`-facet enforcement (the `{refines, relies_on, assumes}` acyclic union; the composition demo's `STRUCT` block) re-keys its reliance clause to **preserve the dependency orientation**: `struct_edge(R, G) :- covers(G, R)` (was `struct_edge(F, To) :- relies_on(F, To)`), keeping the dependency graph byte-identical so cycle detection is provably unchanged. The joint-acyclicity invariant becomes `{refines, covers, assumes}` with `covers` read in the dependant→dependee (`R → G`) orientation, **not** its surface direction. A naive union over surface directions puts `covers` and `assumes` in parallel (both `G → R`), collapses a reliance cycle, and lets it go undetected. Validated: `seg_demo_clingo_covers_invariance_v1.py`, scenario `S-NAIVE` (silent miss) vs `S-NEWok` (byte-identical detection).
3. **DEC-015 preserved.** `residual(C) :- assumes(G, C), not referenced(G)` still fires only for local (non-referenced) authored guarantees; a broken/incomplete `covers` reliance stays `unsatisfied`, never residual.
4. **Tests.** Existing 10/10 (`seg_demo_clingo_partial_discharge`) + 9/9 (`seg_demo_clingo_composition`) must hold under the flipped+renamed rules; scenario 4 ("g_up unsatisfied yet excluded") is rewritten to assert `not unsatisfied(g_up)` and `not product(g_up)` — there is no longer an atom to filter. **Gate built and run before any doc edit:** `seg_demo_clingo_covers_invariance_v1.py` runs both demos' full scenario sets side-by-side (old vs new) and confirms **19/19 verdict-invariant** — byte-identical after stripping the vanishing `unsatisfied(<guarantee>)` atom — plus the three-way `STRUCT` check behind 2a. Baselines 10/10 + 9/9 were confirmed immediately beforehand.
5. **Propagation (each citing DEC-017).** The concrete composition vocabulary is **instance-level — it lives in the example** `seg_example_v1_plus_composition.dsl`: register `Guarantee`, replace `relies_on` with `covers`, widen `assumes` to `Requirement | Guarantee`, re-key the rules (`covered/1`, `covers, G, R`). The **generic DSL spec** `seg_definition_language` does **not** register composition vocab — composition is an extension at the concrete-instance level, not part of the grammar-formation model that the spec describes; its sole DEC-017 touch is the §6 joint-acyclicity invariant, restated as `{refines, covers, assumes}` with `covers` read `R → G` (the canonical home of the 2a orientation). Both clingo demos-of-record re-key (and the composition demo's `STRUCT` block takes the 2a fix). `seg_composability_cbd` §8–§9 reflect the typing/edge change, and §8 well-foundedness + the DEC-015 honest-note acyclic-union phrasing gain the orientation caveat. `seg_glossary` folds `Guarantee`, `covers` and records the `relies_on`→`covers` and `reliance`→`covered` renames. Prior art: KAOS.
6. **Prior art.** KAOS added as the decomposition precedent for `refines` — the AND-refinement satisfaction parallel (Dardenne, van Lamsweerde & Fickas, "Goal-directed Requirements Acquisition," *Science of Computer Programming* 20:3–50, 1993). Flagged as a **conceptual parallel, not a confirmed lineage**: SEG's `refines` may equally trace to the general requirements-decomposition tradition (EARS, sphinx-needs) rather than KAOS specifically.

**Honest note.**
- This is a re-wire of tested-and-passing rules with **no intended change to any three-state verdict**; the demo exists to prove behavioral invariance, not to add behavior. If a verdict shifts, the re-wire is wrong, not the spec.
- `assumes` domain widening to `Requirement | Guarantee` and the new `covers` / `Guarantee` shapes are SHACL changes (DEC-016 boundary) — flag at schema time.
---

## DEC-018 — `obligation` is the node-level state for an open condition-of-use, distinct from the structural `residual`

**Status:** Accepted (complements DEC-015; a node-level partition *under* the proof-level three states, changing neither)

**Decision.**
- Introduce **`obligation/1`** as the node-level verdict state for a requirement that is an open, published condition of use: `obligation(R) :- residual(R), not unsatisfied(R)`. It is layered on top of — **not** a rename of — the *structural* `residual/1` (`assumes` from a non-referenced guarantee, DEC-015 c1), which is retained unchanged.
- Tighten the discharged bucket to exclude it: `satisfied(R) :- node(R, requirement), not unsatisfied(R), not obligation(R)`.
- The node-level partition over requirements is now three mutually-exclusive states — **satisfied** (discharged), **obligation** (open published condition), **unsatisfied** (gap) — with precedence **unsatisfied > obligation > satisfied**: a failing test is a gap regardless of how the node was published.

**Rationale.**
- `satisfied` was overloaded. Once the DEC-015 `residual`→`discharged_otherwise` fold suppresses the leaf-incompleteness rule (so a published assumption keeps the proof *conditional*, not *failed*), the catch-all `satisfied :- not unsatisfied` swept the obligation into `satisfied` — an open obligation read as a local achievement. The fold's purpose is correct and is preserved; only the surface label was wrong.
- `residual` (structural: "published here") and `obligation` (state: "this node is an open obligation") only coincide today. Keeping them distinct refuses to collapse two concepts the composition layer will pull apart: an inherited, re-published condition is *referenced* (so not a `residual`) yet must still read as an `obligation`. (Forward link: the undischarged-re-publish case, GAPS G9.)
- "obligation" was ratified this session for the node-level state; it aligns with the standard "proof obligation" usage and the CBD reading of `A_up` as an obligation the integrator discharges. Not asserted as a specific citation.

**Consequences.**
1. `obligation/1` enters the rule-set; `satisfied/1` gains the `not obligation(R)` guard. Both are reported-only — **no rule body reads `satisfied` or `obligation`** (verified by inspection: `satisfied` occurs only as a head and in `#show`) — so `unsatisfied`, `residual`, `product`, and the DEC-015 `proof_*` rollup are byte-identical and the proof verdict cannot change.
2. The DEC-015 proof-scope states (`proof_total` / `proof_conditional` / `proof_unsatisfied`) are unchanged and unaffected; DEC-018 is a node-level partition *under* them, not a second proof verdict.
3. **Gate built and run before this entry.** `seg_demo_clingo_obligation_v1.py` runs the old vs new rule-sets side-by-side on the producer fixture and both consumer scenarios of the SEG↔SPDX round-trip prototype: **3/3 verdict-invariant**, and satisfied / obligation / unsatisfied confirmed mutually exclusive. The full round-trip (producer → SHACL-valid SPDX FuSa BOM → consumer) re-runs clean on the applied rule-set.
4. **Diagnostic payoff.** In the undischarged-re-publish scenario the partition separates the locally re-published condition (correctly `obligation`) from the inherited-and-undischarged condition (a gap / `unsatisfied`), making G9's required fix legible: a discharge-by-re-publish link that converts an inherited gap into a *forwarded* obligation. Design only; not implemented here.

**Honest note.**
- No intended change to any verdict — the demo exists to prove invariance, mirroring DEC-017's discipline. If a `proof_*` shifts, the change is wrong, not the spec.
- This entry was validated in the SEG↔SPDX round-trip prototype rule-set (`seg_ruleset.py`, lifted verbatim from `seg_demo_clingo_partial_discharge_v3.py`), **not yet** in the project's demos-of-record (`seg_demo_clingo_partial_discharge`, `seg_demo_clingo_composition`) or `seg_composability_cbd` §9. Folding `obligation` into those, and into `seg_glossary`, is a separate propagation pass.
---

## DEC-019 — Per-component contract vector; `A_i` is the obligation down-closure; an authored-but-locally-handled assumption is a structural error

**Status:** Accepted (builds on DEC-018; realizes the committed members for the DEC-012 `flat-openable` sub-mode). **Corrected in place** from an earlier leaf-keyed phrasing — see the correction note; no propagation had occurred.

**Decision.**
- **Contract vector.** A producer seals one proof over a flat vector of per-component contracts `C_i = (G_i, {A_i1 … A_ik})`. Each `G_i` is a **top-level requirement** — a `refines`-root that is `satisfied`: not the child of any `refines` edge (`guarantee(R) :- node(R, requirement), satisfied(R), not has_parent(R)`). Intra-project refinement — the subtree *below* `G_i` — is **internal and private**, never exported. The committed member at slot *i* is the atomic `(G_i, A_i)` bundle (the "option 1" granularity; design-graph-member granularity "option 2" is left open and may coexist later).
- **`A_i` = obligation down-closure.** `A_i` is the set of `obligation`s assumed anywhere in `G_i`'s subtree: `A_i = { C : obligation(C), assumes(N, C), N ∈ descendant-or-self(G_i) over refines }`. A shared obligation assumed under two different roots appears in both contracts' `A_i` — assumptions **double-count per contract**, which is accepted (selective downstream opening pairs each `G_i` with its own copy).
- **Forbid authored-but-not-forwarded.** A node simultaneously *authored as an assumption* (a `residual`: `assumes` from a non-referenced guarantee) **and** *locally handled* (target of `reviews` / `covers` / `verifies` / `implements`) is a **graph-level structural error**, flagged by `struct_err_assumes_not_forwarded/1` — a structural facet alongside `acyclic`, **not** a verdict state. Authoring an `assumes` edge asserts the condition is *forwarded* to the integrator; discharging it locally as well contradicts that, and would leak a handled node into `A_i` (since `residual` is purely structural and would still read as `obligation`).

**Rationale.**
- **Public/private boundary.** Intra-project refinement is an internal design detail, not part of the cross-organization contract. Only the top-level requirement — the advertised capability — is public; the decomposition that discharges it stays sealed inside the proof. Keying on the `refines`-root makes the exported contract exactly the public claim.
- **The down-closure is then forced.** The public guarantee depends on every obligation anywhere in the (hidden) decomposition that realizes it, so all of them must surface as the contract's conditions — hence the subtree down-closure rather than a single node's assumes.
- The forbid keeps `A_i = obligation down-closure` sound *as stated* — no need to special-case "subtract local discharge" inside the closure — by making the offending shape illegal at the structural layer instead.

**Consequences.**
1. New derivations (composition/closure layer, not the verdict rollup): `has_parent/1`, `guarantee/1` (a `satisfied` `refines`-root), `desc/2` (descendant-or-self over `refines`), `guards/2` (the `A_i` down-closure), and the structural facet `struct_err_assumes_not_forwarded/1`. The verdict rollup (`proof_*`) is untouched.
2. The contract vector `{C_i}` is the **member set** committed by the DEC-012 `flat-openable` Merkle/vector commitment; the committed unit per slot is the atomic `(G_i, A_i)` bundle. Selective downstream opening reveals a chosen `C_i` with its paired `A_i` — the integrity the consumer's verifier checks.
3. **Gate built and run before this entry.** `seg_demo_clingo_contract_vector_v1.py` on the producer's two-subsystem graph yields `C[p_sys] = (p_sys, {p_entropy, p_rng_a, p_mem})` and `C[p_sys_2] = (p_sys_2, {p_sha256_a, p_sha512_a, p_mem})` — `p_mem` double-counted across the two roots — with no structural error; a violating variant (a subtree that both authors and reviews a condition) fires `struct_err_assumes_not_forwarded`.

**Honest note.**
- Placement of the forbid in clingo (not SHACL) follows the DEC-016 boundary: the "non-referenced guarantee" condition is a global graph property, awkward for a node-local SHACL shape; the acyclic facet is the precedent for a structural-integrity check living outside SHACL.
- Edge case left open (Layer B): a `refines`-root discharged purely by `covers` — a *re-exported* upstream guarantee — is `satisfied` and would qualify as a `G_i`. Whether a re-exported guarantee should itself be a sealed contract is unsettled.
- Realized in the SEG↔SPDX round-trip prototype only; folding `guarantee` / `desc` / `guards` / the facet into the demos-of-record, `seg_composability_cbd`, and `seg_glossary` is a separate propagation pass (carried with the pending DEC-018 propagation).

**Correction note (terminology).**
- This entry originally keyed contracts on the project's `leaf/1` — a requirement with no *incoming* `refines` (the most-refined node, e.g. `p_rng`) — with an *up-closure*. That transcribed "leaf" in the wrong sense. The intended key is the `refines`-**root**: no *outgoing* `refines` (the public top-level requirement, e.g. `p_sys`), with the *down-closure*. Corrected in place because the leaf-keyed form was a transcription error, not a ratified prior choice, and nothing durable had cited it. The `leaf` (no incoming `refines`) vs `refines`-root (no outgoing `refines`) distinction should be stated explicitly in `seg_glossary`.
---

## DEC-020 — SPDX representation and flat-openable commitment for the contract vector

**Status:** Accepted (realizes DEC-019's contract vector as an SPDX FuSa artifact, activates the DEC-012 `flat-openable` sub-mode, and consumes DEC-017 `Guarantee`/`covers` on import)

**Decision.**
- **Per-contract `Bom`.** Each contract `C_i = (G_i, {A_ij})` projects to a Core `Bom`: `G_i` → a `Requirement` (the Bom's `rootElement`); each `A_ij` → a FuSa `Assumption` (lossy, G3) carried as `element`; a reified `assumes` Relationship `G_i → A_ij`. The `Bom` carries a content `Hash` (sha256 over the canonical `(G_i, {A_ij})` bundle) — the committed member. Root-keyed per DEC-019: parent requirements and the internal `refines` tree are NOT exported (sealed inside the proof).
- **Commitment = sha256 Merkle tree (DEC-012 `flat-openable`).** The `SpdxDocument` carries the Merkle ROOT over the sorted member hashes via `verifiedUsing`. The tree and the O(log n) inclusion proofs are tooling-side (`seg_commitment.py`); SPDX carries only hash values. Opening proofs for a disclosed subset travel in an `openings.json` sidecar — SPDX has no inclusion-proof carrier.
- **Import = verify-then-reconstruct.** A consumer opens a chosen subset and, per contract, recomputes the member hash from the opened bundle and checks its inclusion proof against the root *before* use; a bundle missing an assumption fails (hash mismatch). Verified contracts reconstruct downstream: `G_i` → a `Guarantee` node (DEC-017) `referenced_under` a `seal_ok` `Manifest`; each `A_ij` → a SEG `requirement` condition referenced under the same `Manifest` (G3 hint), with an `assumes` edge from **each** importing guarantee. **Shared conditions dedupe** to one node (one `assumes` per importer) so a single discharge satisfies every contract that inherited it.
- **Verdict unchanged.** Import runs the DEC-018/019 engine; the roll-up is recomputed downstream, never carried in the BOM.

**Rationale.**
- A `Bom` is the natural addressable, hashable member: one IRI = one contract, opened atomically with its `rootElement`/`element`.
- Keeping the Merkle tree tooling-side respects the SPDX boundary (DEC-016): SPDX models integrity *hashes*, not proof systems, yet the document still commits to the whole vector via one root.
- Reconstructing a shared condition as one deduped node matches DEC-019's accepted double-counting: the seal double-counts content per member, but stable identity collapses it on import, so the integrator discharges it once.

**Consequences.**
1. `spdx_export.py` emits one `Bom` per contract + the Merkle root; `seg_commitment.py` provides `member_hash`/`root`/`prove`/`verify`; `consumer.py` does verify-then-reconstruct + the downstream verdict.
2. **Gate run before this entry.** `seg_commitment` self-test (open/verify; tamper → reject); `spdx_export` → 2 `Bom`s and the BOM CONFORMS against the FuSa SHACL; `consumer.py`: verification gate holds (dropping `p_mem` rejected), scenario A `total`, B `unsatisfied`, C `total` with `p_mem` discharged once for both contracts.
3. **G9 confirmed open.** An undischarged inherited condition stays a gap (scenario B → `unsatisfied`), not a forwarded obligation; the discharge-by-re-publish link remains Layer-B work.

**Honest note.**
- The `openings.json` sidecar is outside SPDX; a real exchange needs an agreed inclusion-proof carrier or a profile extension (GAPS G10).
- `seal_ok` on the imported `Manifest` is idealized; authenticity/signing remains stubbed (G6).
- Realized in the round-trip prototype only; not yet in the demos-of-record or `seg_composability_cbd`. Propagation pending (with DEC-018/019).
---

## DEC-021 — Witness-side `environment` + `surrogate_for`/`ran_on`; test-time surrogacy is not a discharge

**Status:** Accepted (extends the DEC-016 witness model; resolves the scope of the DEC-019 author-and-not-forwarded forbid)

**Decision.**
- **New node type `environment`** — the assume-guarantee dual of `implementation`: the entity that *satisfies an assumption* (E ⊨ A), as `implementation` is the entity that discharges a guarantee. Grounded in CBD/A-G — assumptions are the constraints a component's designer places on the environments in which it may be used (Benveniste et al. 2018), and an environment of a contract is exactly a component satisfying its assumptions. Generalized from `testenvironment` so any surrogate (not only a test platform) is an `environment` element standing in for an assumed property — no "test" subtype needed.
- **`surrogate_for`** (`environment → assumption`): a witness-side stand-in used to *produce evidence* — e.g. QEMU as a surrogate for an assumed compliant HAL. A descriptive coinage: the literature has an environment *satisfying* assumptions (E ⊨ A) but no term for a *test-time* surrogate, so `surrogate_for` is deliberately weaker than satisfaction.
- **`ran_on`** (`testoutcome → environment`): provenance — which environment produced the outcome.
- **Boundary.** `environment`, `surrogate_for`, and `ran_on` live in the **witness sub-graph**. They are verdict-inert (no verdict / closure / acyclicity rule reads them) and **not exported** — compressed into the seal the upstream authority signs (non-cryptographic for now). The deployment assumption itself (the compliant HAL) is authored via `assumes` and flows into `A_i` like any condition of use.
- **DEC-019 scope.** `surrogate_for` is **not** a discharge: it is not in the `handled` set (`reviews`/`covers`/`verifies`/`implements`), so a node both *authored* (`assumes`) and *surrogate-tested* does **not** trip `struct_err_assumes_not_forwarded`. Test-time surrogacy and deployment-time discharge are distinct relations; the forbid correctly stays silent on surrogacy.

**Rationale.**
- `environment` is the textbook A/G term; adopting it completes SEG's dual structure (implementation/guarantee ; environment/assumption) and is citable, unlike a coined name.
- Keeping surrogacy out of the contract honors the DEC-019 public/private boundary: *how* the evidence was produced (the surrogate platform) is internal; only the forwarded assumption is public.
- Modeling the surrogate as a non-discharge resolves the conflict flagged while wiring #3: the producer legitimately forwards "compliant HAL" to the integrator *and* satisfies it with a stand-in for evidence only — two relations DEC-019's blanket forbid had conflated.

**Consequences.**
1. The producer witness sub-graph gains `environment` / `surrogate_for` / `ran_on`; `spdx_export.py` ignores them (emits only requirements/assumptions/Boms). Verified: the HAL assumption `p_hal` appears in the BOM (in `C[p_sys]`) while `p_qemu` / `surrogate_for` / `ran_on` are absent; the BOM still CONFORMS.
2. The renderer (`seg_graphviz.py`) gains the `environment` shape and the two edge styles.
3. **Gate run before this entry.** Producer: `C[p_sys]` is now `{p_entropy, p_rng_a, p_mem, p_hal}` with `struct_errors` empty; export CONFORMS with `p_hal` present and the witness environment absent; the DEC-018 and DEC-019 gates remain green.

**Honest note.**
- Whether the surrogate is *faithful* — representativeness, "is QEMU representative of a compliant HAL?" — is **not** modeled. That is a witness-validity / tool-qualification concern (ISO 26262-8, DO-330), deferred (GAPS G11). We record the surrogate, not its adequacy.
- `environment` is adopted from the literature; `surrogate_for` and `ran_on` are descriptive coinages of this project.
- Realized in the round-trip prototype only; propagation to the demos-of-record / `seg_composability_cbd` / `seg_glossary` is pending (with DEC-018/019/020).

---

## DEC-022 — `forward` re-publishes an inherited undischarged condition as a forwarded `condition_of_use`: affirmation-gated, verdict-conditional, re-exported through `covers` (resolves G9)

**Status:** Accepted (resolves GAPS G9; builds on DEC-010/015/017/018/019; two clingo gates run before this entry)

**Decision.**
- New relation **`forward`** (edge: relying requirement `R` → inherited condition `C`) re-publishes an inherited, undischarged condition as a forwarded condition of use. Deliberateness rides on an **affirmation, not the bare edge**: `forward_ok(R,C) :- active_edge(_,forward,R,C), affirmed_forward(R,C)` — the reliance shape (`covers` is inert without `seal_ok`). Derived `forwarded(C) :- forward_ok(_,C)`.
- A forwarded condition stops being a local gap: `discharged_otherwise(C) :- forwarded(C)` (joins the existing `residual` member), suppressing the leaf-incompleteness rules so `unsatisfied(C)` never fires and the sealed-condition poison rule never triggers for it.
- It reads as an open condition at node level: `obligation(C) :- forwarded(C), not unsatisfied(C)` (DEC-018: a re-published condition is *referenced* — so not a `residual` — yet must read as an `obligation`). Reported-only; no rule body reads it.
- Proof rollup generalizes from residual-only to a published-condition union: `condition_of_use(C) :- residual(C)` / `:- forwarded(C)`; `proof_has_condition_of_use` replaces `proof_has_residual` in `proof_total` / `proof_conditional`. A proof with a forwarded remainder and no genuine gap is `proof_conditional`.
- **Export (re-publish the remainder).** The DEC-019 down-closure gains one additive clause reaching through `covers`, gated on `forwarded`: `guards(R,C) :- desc(R,N), active_edge(_,covers,GUP,N), edge(_,assumes,GUP,C), forwarded(C)`. The re-exported `A_i` carries exactly the forwarded remainder; a locally *discharged* inherited condition is excluded.

**Invariants preserved (cannot launder a gap).**
- DEC-015 dominance: a genuine in-scope gap still yields `proof_unsatisfied` even with a forwarded condition present.
- A silent drop (no `forward` edge) or an *unaffirmed* `forward` edge stays `unsatisfied` — re-publish is opt-in and affirmation-backed.
- Verdict- and closure-invariant on any forward-free graph.

**Rationale.**
- Supplies the discharge-by-re-publish link DEC-018 flagged for G9, realizing DEC-015's re-publish intent (incompletely-discharged proof → conditional + forward the remainder, not fail outright).
- Affirmation-gating keeps re-publish a deliberate, logged act consistent with SEG's content-bound affirmations; it cannot mask a real gap.
- The export clause reaches through `covers` because the forwarded condition is inherited from the relied-on guarantee, not authored in the integrator's own `refines` tree; gating on `forwarded` keeps the re-exported set exactly the remainder.
- Occam: reuses `discharged_otherwise` and `obligation`; one new union predicate; one additive `guards` clause; no existing verdict shifts.

**Consequences.**
1. `seg_ruleset` gains `forward_ok/2`, `forwarded/1`, the two reuse clauses, and the `condition_of_use/1`-keyed rollup replacing `proof_has_residual`. New EDB: the `forward` edge and `affirmed_forward/2`.
2. `seg_composition` gains the one additive `guards` clause reaching through `covers`.
3. **Gates run before this entry.** `seg_demo_clingo_forward_v1.py` (5/5 + invariance: S1 reproduces G9; S2 affirmed → conditional + obligation; S3 drop and S4 unaffirmed stay gaps; S5 dominance) and `seg_demo_clingo_forward_export_v1.py` (3/3 + invariance: OLD closure drops the remainder; NEW re-exports exactly the forwarded set, excludes the discharged one).
4. SHACL (DEC-016 boundary): the new `forward` edge type, the `affirmed_forward` affirmation, and the domain widening are schema-time flags, not SHACL-enforced presence.

**Honest note.**
- **`condition_of_use` is a project-chosen readable label** for the published-`A_up` set {`residual` ∪ `forwarded`}; it is **not** a verbatim normative term. The standards say "assumption(s) of use" (ISO 26262 SEooC assumptions; SPDX FuSa models the A-side as `Assumption` / `assumptionStatement`). Chosen for outside-reader legibility over the `proof_has_residual` overreach, eyes open.
- `affirmed_forward` is an idealized affirmation fact in the gates (parallel to `seal_ok`), not the content-bound two-sided affirmation anchor; wiring it to the real anchor is pending.
- Realized in the two gates only; propagation to `seg_ruleset.py` / the round-trip prototype, the demos-of-record (`seg_demo_clingo_partial_discharge`, `seg_demo_clingo_composition`), `seg_composability_cbd` §9, and `seg_glossary` (record `forward` / `forwarded` / `forward_ok` / `condition_of_use`) is a separate pass (carried with the pending DEC-018/019/020/021 propagation).
- The export clause covers a single `covers`-hop; whether a *re-exported* guarantee (the DEC-019 open edge case) needs its own treatment is still open.
- `forward` / `forwarded` / `forward_ok` are project vocabulary ratified this session; no literature predicate exists for "forwarding an undischarged assumption" (the A/G concept is the composite's residual / weakest assumption — no relational verb).

---

## DEC-023 — Compliant-item-supplier discharge: an inherited assumption discharged by an affirmed `covers` onto a supplier's guarantee; admissibility gated by a document-root compatibility (version-pin) check

**Status:** Accepted (names the first Layer-B actor role; builds on DEC-010/017/020/022; one clingo+verifier gate run before this entry)

**Decision.**
- **Role (named from literature).** The **compliant-item supplier** (IEC 61508-4 *compliant item*; IEC 61508-2 Annex D *Safety Manual for Compliant Items*) publishes a compliant item `M′` whose SPDX safety BOM *is* its compliant-item safety manual — an ordinary DEC-020 contract BOM: guarantee `G_M′` plus `M′`'s own conditions of use as `condition_of_use` / Assumption elements. The consuming counterpart is the **integrator** (EU CRA Annex II). `environment` is **not** reused for this actor — it stays the sealed witness node (DEC-021).
- **Discharge — no new verdict rule.** The integrator discharges an inherited assumption `C` (e.g. `p_hal`) by an affirmed `covers(G_M′, C)` reliance on the supplier's guarantee. On the current engine: `covered(C)` → `discharged_otherwise(C)` → `C` not `unsatisfied` → the sealed-condition poison rule never fires. It is the existing reliance (`covers` + `seal_ok` + impl-uses) applied to an *inherited* assumption rather than a downstream-authored requirement. `M′`'s own conditions of use import as new inherited conditions to discharge-or-forward (the chain continues a hop).
- **Admissibility — document-root compatibility check (new, verifier-side).** The integrator presents two SPDX documents (upstream `M`, supplier `M′`). `M′`'s document pins the exact upstream it was validated against via `SpdxDocument.import` → `ExternalMap(externalSpdxId = ⟨M doc IRI⟩, verifiedUsing = Hash(⟨M Merkle root⟩))`. The integrator admits `M′`'s discharge **only if** that pin equals the upstream document the integrator itself imports — equality on both IRI and root (document-root granularity). This is a **diamond co-reference / version-pin consistency** check, extending DEC-010's version-pin to a shared dependency. Mismatch → reject.
- **The check is load-bearing and lives at the verifier.** A pre-reconstruction step, the sibling of the Merkle inclusion check (`consumer.py` `verify_contract`). The Datalog layer is blind to version skew — wiring an incompatible `M′` anyway reads a spurious `proof_total`.

**Rationale.**
- IEC 61508's *compliant item* + *compliant-item safety manual* map exactly onto `M′` and its BOM; the element's claimed capability holds only when applied per the safety-manual instructions — i.e. its conditions of use. Role and artifact are citable, not coined.
- Occam: the discharge reuses the existing `covers` reliance; the only new machinery is the verifier-side pin check.
- Document-root granularity suffices: the Merkle root commits the whole upstream vector, so one root equality pins the entire referenced document (DEC-020).
- Placing the check at the verifier (not clingo) follows the DEC-016 boundary and the inclusion-proof precedent: cross-document identity is a tooling-side integrity check, not a graph property.

**Consequences.**
1. No change to `seg_ruleset` / the verdict engine.
2. The integrator's import gains an admit/reject document-root compatibility check before wiring `covers(G_M′, C)`; the integrator's published document must carry an `import` / `ExternalMap` pin to the upstream document (provenance of the discharge), though the verdict is recomputed, not carried.
3. **Gate run before this entry.** `seg_demo_clingo_compliant_item_v1.py` (3/3): S1 `M` alone forwards `p_hal` → conditional; S2 `M`+`M′` matching pins → admitted, `covers(g_m_hal, p_hal)` → total; S3 mismatched pins → rejected, with the bypass case showing a spurious `total` (the check is load-bearing).
4. SPDX (DEC-016 boundary): `import` / `ExternalMap` / `verifiedUsing` is stock SPDX 3.0 Core — no profile extension for the reference (contrast the inclusion-proof carrier, G10). Emission/parse in the prototype is a separate pass.

**Honest note.**
- Realized in the model-level gate only; the document-root pin is an abstract string-equality check, **not** emitted/parsed as real SPDX `import` / `ExternalMap`. The SPDX round-trip (needs the `spec-parser` SHACL path) is pending.
- The pin proves *same document* (IRI + root), not that `M′` truly validated against `M` — that is the supplier's affirmed claim inside its seal (same boundary as surrogate faithfulness, G11) — and it is identity, not semantic equivalence (a rebuilt-but-equivalent `M` with a different root is rejected: the strict, safe choice).
- Generalizes from this single diamond to lattice consistency in a longer chain; only the diamond is exercised here.
- The second Layer-B actor role (middleware re-publishing residuals via `forward`) is not covered here.
- *compliant-item supplier* / *integrator* / *compliant-item safety manual* enter project vocabulary this session (IEC 61508 / EU CRA grounded); folding them into `seg_glossary` is part of the pending propagation pass.

## DEC-024 — `conformsTo`: a producer-side declaration that a guarantee satisfies an upstream assumption; verdict-inert, resolved to `covers` on import (closes GAPS G12)

**Status:** Accepted (term ratified; one clingo gate run before this entry; builds on DEC-017/020/022/023)

**Decision.**
- **The gap (G12).** A supplier's BOM declared its contract `C = (m_hal, {m_clk, m_pwr})` but recorded NOTHING about which upstream assumption `m_hal` is offered to satisfy. The integrator could not derive the reliance edge from data — `consumer.py` hard-coded `covers(g_m_hal, p_hal)` from a literal (`HAL = "p_hal"`); `supplier_bom.jsonld` mentioned `p_hal` zero times.
- **The relation (grounded, not coined).** `conformsTo(G, A)` — verbatim SPDX Core `RelationshipType`: "The `from` Element conforms to each `to` Assumption or Specification." The matched partner of `assumes` (which `M` already applies to `p_hal`); the FuSa `Assumption` class is exactly what `p_hal` is. The producer declares that guarantee node `G` is offered to satisfy an external upstream Assumption identified by IRI.
- **Verdict-inert in the producer.** `conformsTo` appears in NO verdict rule body; its target is an external IRI kept out of the producer's verdict node-set (never renders red, never a product, never poisons). The supplier's verdict and contract vector are unchanged. This is the light alternative to importing-and-locally-discharging the upstream assumption (rejected as tail-chasing).
- **Resolved to `covers` on import.** Importing `M` (resolving the assumption IRI under the sealed manifest) and `M'` (reading its `conformsTo` declarations), the integrator MATCHES each `conformsTo` target IRI against an imported assumption's IRI and MINTS `covers(g_M', A)` — legitimate now because `g_M'` is referenced under the sealed manifest, so DEC-017's reliance/seal checks apply. The hard-coded literal is removed.

**Rationale.**
- SEG is the source of truth, SPDX the projection; the projection must not carry a relation the source lacks. The targeting belongs in the SEG model as one more typed edge — not as compound internal structure of `G` (Occam: one `G` can target several assumptions via several edges; no edge attributes are needed yet, and `G` stays a meaningful claim independent of whom it serves).
- `conformsTo` is the pre-import form of `covers`: a declaration made where reliance/seal cannot yet apply (the guarantee is still local), resolved to the verdict-bearing edge once the guarantee is imported and sealed. A *local* `covers` would misfire (`covered` without sealed reliance → `unsatisfied`), which is why the declaration is a distinct, inert relation.
- The term is grounded verbatim in SPDX Core; CBD/AGREE carry the concept (a guarantee discharging an upstream assumption) but not as a single keyword, so the name leans on SPDX.

**Consequences.**
1. No change to `seg_ruleset` / the verdict engine; no change to `guarantee/1` (the earlier guarantee/1 refinement is shelved — it was solving a problem created by the rejected local-discharge model).
2. `spdx_export.py` gains a `conforms_to` param emitting `conformsTo` Relationships; the supplier declares `conformsTo(m_hal, ⟨M⟩#p_hal)`, resolved from M's published assumptions.
3. `consumer.py` reads `conformsTo` from M', matches target IRIs against M's imported assumption IRIs, and mints `covers` (read-match-mint); the `HAL` literal is removed.
4. **Gate run before this entry.** `seg_demo_clingo_conformsto_v1.py` (3/3): A `conformsTo` is verdict-inert (rules reference it 0 times; supplier vector unchanged); B a matched target mints `covers` → total; C an unmatched target mints nothing → the inherited assumption stays undischarged → not total (forward-or-fail, DEC-022).

**Honest note.**
- Matching is by assumption IRI; it relies on stable per-assumption IRIs, which the BOM already provides (each assumption is a FuSa `Assumption` element with its own `spdxId`).
- `conformsTo` asserts intent ("offered to satisfy"), not proof; the actual discharge still requires the integrator to adopt `M'` and honor its conditions of use, and the document-root compatibility check (DEC-023) still gates admissibility.
- `conformsTo` enters project vocabulary this session (SPDX Core grounded); folding it into `seg_glossary` is part of the pending propagation pass.

## DEC-025 — Entity/role vocabulary: {manufacturer, assessor, item provider} × {supplier, integrator, verifier}; `auditor` dropped; verification is universal self-verification

**Status:** Accepted (vocabulary only — no verdict-rule change, no gate required; supersedes the informal "product maker", "auditor", and "compliant-item supplier"-as-entity labels)

**Decision.**
- **Two axes.** A party has a stable *entity* (who it is) and performs one or more *roles* (what it is doing). The prior label "compliant-item supplier" conflated the two; it is dissolved.
- **Entities.**
  - **manufacturer** (was "product maker") — an integrator that is never simultaneously a supplier; terminal in the supply chain; emits a safety case + implementation but **no Safety BOM**.
  - **item provider** — always a supplier, optionally also an integrator; emits a safety case + implementation, and (in the supplier role) a Safety BOM bound to that safety case. Two forms exist — supplier-only (leaf, e.g. upstream `M`) and supplier+integrator (mid-chain, e.g. the IEC 61508 silicon vendor `M'`) — and are deliberately **left unnamed** (see Rationale).
  - **assessor** (was "auditor") — verifier only; performs no supply, integration, or implementation; the only entity *defined* by verification. Its defining output is a *certificate* (mechanism specified in a forthcoming entry, not here).
- **Roles.**
  - **supplier** — emits a Safety BOM cryptographically bound to its safety case. Criterion: a party is a supplier **iff** it emits a Safety BOM.
  - **integrator** — imports a Safety BOM + the supplier's implementation and composes the imported contracts into its own evidence graph + implementation.
  - **verifier** — establishes a verdict by *recomputation*. Verification is a **universal self-verification** obligation: every party verifies what it publishes or imports, and an integrator's check of an import anticipates the assessor's later check (same check, different agent). Only the assessor is *defined* by this role.
- **Entity->role mapping.** manufacturer -> {integrator, self-verifier}, never supplier; assessor -> {verifier} exclusively; item provider -> {supplier} or {supplier, integrator}, with self-verification a universal obligation.
- **`auditor` dropped.** It has no referent in SEG: in IEC 61508/61511 an auditor checks process/procedure conformance (the functional-safety management system), which SEG does not model; SEG computes the technical verdict — whether a contract is *achieved* — which is the **assessor's** question. A role whose activity SEG does not represent is a term without a job.

**Rationale.**
- The entity/role split dissolves the identity-vs-activity conflation in "compliant-item supplier"; the IEC 61508 compliance level is an attribute of the *item* and its safety manual (and of the assessor's certificate), not of the entity name, so "item provider" is standard-agnostic by design.
- **Grounding (not coined).** "compliant item", "supplier", and "integrator" are IEC 61508-4 vocabulary (a compliant item is a reusable element a supplier documents via a safety manual so integrators can integrate it). The assessor/auditor split follows the standard's distinction between functional-safety *assessment* (judges whether safety was achieved) and *audit* (checks whether procedures were followed). "safety case" is the established evidence-artifact term; "manufacturer" replaces the colloquial coinage "product maker".
- **Occam.** The two item-provider forms are not named because nothing reads such a name — role-composition plus the `forward` operation (DEC-022) already express the difference; a noun would have no recurring job. "manufacturer" earns a name only because "terminal integrator that emits no BOM" is an externally-recognised category (the end-product maker), whereas "supplier that also integrates" is a finer internal distinction.

**Consequences.**
1. No change to `seg_ruleset` / the verdict engine; vocabulary only, no gate.
2. Apply-step (separate): fold the entity/role vocabulary into `seg_glossary`; update briefs/summaries and renderer labels that used "product maker", "auditor", or "compliant-item supplier" as an entity.
3. The assessor's certificate and the BOM<->safety-case binding it signs are fixed in a forthcoming entry; this one fixes only the vocabulary.
4. Informs the still-open supplier-side imported-assumption node-type decision — resolve it alongside the explicit guarantee/requirement typing entry.

**Honest note.**
- "verifier" collides with the W3C Verifiable-Credentials sense (a relying party that *trusts* an issuer's claim after an authenticity check); SEG's verifier *recomputes* rather than relies. The glossary should note both senses. The W3C VC taxonomy was considered this session and explicitly **not** adopted.
- The assessor/auditor and compliant-item grounding was read this session from secondary functional-safety commentary; the primary IEC 61508/61511 text is paywalled and was not quoted verbatim.

## DEC-026 — Assessor certificate = a signature over the pair `(hash(case), BOM)`; the safety case and the Safety BOM are distinct documents, the case published or withheld at the item provider's discretion

**Status:** Accepted as design (model only — not yet implemented; no assessor/signature path exists in code today; a realization + demonstration is a later apply-step; builds on DEC-012/020 commitment and DEC-025 roles)

**Decision.**
- **Two documents.** The *safety case* (the full evidence graph: requirements, refinement, verification, outcomes, implementation nodes) and the *Safety BOM* (the surfacing contract vector — root guarantee + the down-closure of its assumptions, `guards/2` — under the DEC-020 flat-openable commitment) are distinct artifacts. The BOM is a lossy, much smaller projection of the case; the case keeps the per-node assumptions and refinement tree the BOM folds away.
- **The certificate.** The assessor's defining output (DEC-025) is a *certificate*: a digital signature over the **pair `(hash(case), BOM)`**. Before signing, the assessor — sole holder of the full safety case — uses SEG to confirm the BOM is *derivable from* the case (re-derive the contract vector and the verdict from the evidence graph) and *bound to* it. Signing the pair makes "the BOM is the certified derivation of the case with this digest" a checkable relationship, not a private claim: the signature cannot be re-paired with a case the assessor never inspected.
- **Publication.** The Safety BOM + signature are always published. The safety case is published **or withheld** at the item provider's discretion. When published, the full derivation becomes independently recomputable (re-derive the BOM, recompute the verdict) and checkable against the signed `hash(case)`.
- **Division of labor.** The assessor (sole holder of the evidence graph) vouches for *derivation/entailment* by signing — a trust-transferred attestation. An integrator holding only the BOM + signature *trusts* that attestation for entailment but *recomputes composition* itself from the contracts. Trust where you must; recompute where you can.
- **Authenticity is out of SEG's scope.** The integrator confirms the signature against the assessor's public key in a public keystore / transparency log (e.g. sigstore). Key identity/PKI is orthogonal — SEG provides the *integrity binding*, not the identity root.

**Rationale.**
- The two-document split makes the trust/recompute boundary explicit and tunable per disclosure: BOM-only leans on the assessor's signature; BOM + published case removes the need to trust the derivation at all.
- Signing the *pair* rather than the BOM alone is the Occam-minimal way to make derivation-from-the-case certified: a bare signature already prevents re-use on a *different* BOM (different bytes fail); the `hash(case)` closes the residual "same contracts, different evidence" gap for one hash field.
- **SEG's contribution vs the signature's.** Non-transferability to a different BOM is the signature's, not SEG's. SEG's distinctive integrity role is **selective opening** (DEC-012/020): the assessor signs the commitment root once; the provider may reveal contracts piecewise, each verifiable against the signed root; and the member hash binds a guarantee to its full assumption set, so no party can open a guarantee while dropping an assumption.
- "safety case" and "certificate" are established functional-safety terms (the assessor's SIL certificate attests achievement); the construction coins nothing.

**Consequences.**
1. No verdict-engine change; design/model only, no gate.
2. New artifact required (later apply-step): a portable, recomputable serialization of the safety case (today the graph has only `to_facts()` + image renders; no round-trippable document exists). Showing the case "is serializable" = emit -> reload -> recompute verdict + re-derive BOM -> matches the published BOM.
3. The BOM's signed payload is extended to carry / be paired with `hash(case)`. The implementation content-ref the integrator extracts from the BOM (git-sha1 stand-in) is fixed in a forthcoming entry and is what makes a withheld case still yield a usable, pinned implementation.
4. SPDX representation: the signature maps naturally to a `verifiedUsing` Hash/signature on the BOM document; representing the *full safety case* in SPDX is a separate open question (FuSa `RequirementVerification`/`EvidenceRelationship`/`Assumption`/`EvaluationResult` + SupplyChain `TestAction`/`TestProcess` are candidate classes, but the edge semantics and a few node types are unverified).

**Honest note.**
- Not implemented: there is no assessor, signature, keystore, or case-digest in the code today (verified this session). This entry fixes the design; a realization + a demonstration gate come later.
- The certificate attests the assessor's *judgement* that the BOM faithfully derives from the inspected evidence; it does not mechanize the truth of leaf guarantees — SEG treats guarantee/assumption text as opaque, so leaf entailment remains the assessor's human judgement.
- A withheld case means the integrator cannot recompute entailment and must rely on the signature; only publication restores full independent recomputability.
- Blockchain was considered for the keystore and judged unnecessary over a transparency log; recorded to avoid revisiting.

## DEC-027 — Explicit SEG node typing in the BOM: guarantees marked `seg:type=guarantee` (read + asserted against `rootElement` on import); supplier-side `conformsTo`-target reference typed `assumption`

**Status:** Accepted (gate run before this entry; export/import change, proven verdict-invariant; resolves the carried supplier-side node-type fork; builds on DEC-017/024/025)

**Decision.**
- **Guarantee marker.** On export the guarantee element (the contract `Bom`'s `rootElement`, an SPDX Core `Requirement`) carries `comment: "seg:type=guarantee"`, mirroring the `seg:type=requirement` already on FuSa `Assumption` members. On import the SEG node type is **read** from this marker and **asserted** consistent with structural position (`rootElement` => guarantee; Assumption member => requirement); a missing or contradictory marker is a parse error. This replaces inferring guarantee-ness purely from `rootElement` position.
- **String now, Extension later.** The marker is carried in the Core `comment` string for now; promotion to a typed SPDX `Extension`/property is deferred (parsing a type out of `comment` is the acknowledged interim smell).
- **Supplier-side reference (`up_phal`) typed `assumption`** — resolves the carried fork (option 1 of three). The node representing the upstream assumption a supplier `conformsTo` is typed `assumption`: verdict-inert by construction (the ruleset ranges only over `node(R, requirement)`), needing no engine change and no `to_facts` special-case. `assumption` is added to the documented node-type set in `seg_graph.py`.
- **Why option 1 over 2/3.** The supplier-side `up_phal` is a reference a guarantee is *offered against* and never discharged; the integrator's imported assumption is a `requirement` it *does* discharge. Different roles => different types is correct, not a divergence. Option 2 (`requirement`) renders the undischarged reference red and needs a gated engine tweak; option 3 (presentation-only) adds a lowering special-case. Option 1 is the only one inert with neither.

**Rationale.**
- Makes the SEG type that governs the verdict (guarantee excluded from the requirement recursion; assumption inert) explicit in the data rather than reconstructed by convention; the `g_`-prefix house rule and `rootElement`-position inference are no longer the sole carriers of guarantee-ness.
- Symmetric with the existing assumption marker; coins nothing (`seg:type` already in use; `assumption`/`guarantee` are existing SEG node types).
- Occam: option 1 reuses the engine's existing requirement-only quantification for inertness; the marker is one comment field plus a read+assert — no new relation or rule.

**Consequences.**
1. `spdx_export.py`: guarantee element emits `comment: "seg:type=guarantee"`.
2. `consumer.py`: `parse_vector_bom` reads `seg:type` (new `_seg_type` helper) and asserts `rootElement`=>guarantee, members=>requirement.
3. `seg_graph.py`: `assumption` added to the node-type enum comment; `up_phal` ratified as `assumption` (no code change — already so in `supplier.py`).
4. **Gate run before this entry.** Pipeline regenerated; verdicts invariant (producer `conditional`; supplier `conditional`, `C[m_hal]={m_clk,m_pwr}`; integrator A total / B unsatisfied (G9) / C total / D total / E rejected). All three BOMs CONFORM under federated SHACL. Six gates green (obligation 3/3, contract_vector, forward 5/5, forward_export 3/3, compliant_item 3/3, conformsto 3/3). Negative check: `parse_vector_bom` raises on a wrong or missing guarantee marker (assertion bites, not vacuous).

**Honest note.**
- No verdict-engine change; a projection/import change proven verdict-invariant, so no new clingo gate was added — the round-trip assert + negative check + the existing six gates are the verification.
- The `comment`-string marker is interim; the `Extension` promotion — and the open question of whether a FuSa class (`EvaluationResult`/`RequirementVerification`) could host the guarantee natively and retire the SEG-private tag — is deferred.
- `seg:type` records the SEG *reconstruction* type. An Assumption member carries `seg:type=requirement` because the integrator discharges it as a requirement; the supplier-side `up_phal` is `assumption` because it is never discharged. Same upstream assumption, two SEG types by role — intended, not a contradiction.

## DEC-028 — Implementation pin: each contract member binds the set of implementations in the guarantee's subtree by content-ref (sha1 stand-in), projected as `software_File`; swapping an implementation breaks the seal

**Status:** Accepted (gate run before this entry; commitment change — member hashes / roots / document-root pins all move; proven verdict-invariant; builds on DEC-012/020 commitment, DEC-019 contract vector, DEC-026 certificate, DEC-027 typing)

**Decision.**
- **The pin.** Each implementation node carries a `sha1` content-ref (a stand-in over its body label; real content-addressing — a git blob/commit sha — replaces it later). For a contract whose guarantee is `G`, the pin set `I` is every implementation reachable in `G`'s refinement subtree: `impl_member(R,I) :- desc(R,N), edge(_,implements,I,N), node(I,implementation)`. The pin is a **set** (e.g. `p_sys_2` => {`p_im256`,`p_im512`}), not a single file.
- **Bound into the member.** `member_hash` payload gains `"I": sorted([id, sha1])` beside `G` and `A`. Opening a contract now yields `(G, A, I)`; a swapped or dropped implementation changes the member hash and fails its inclusion proof against the signed root — the "can't drop an assumption" property extended to "can't swap the implementation."
- **Projected as `software_File`.** Each pinned implementation is emitted as an SPDX `software_File` carrying a `verifiedUsing` sha1 Hash and the impl id as `name`, added to the contract `Bom`'s `element`; the integrator extracts the pin by filtering software-type elements. The `sha1` lives on the SEG node (source of truth) and is projected, never invented at export (DEC-024 principle).
- **Integrator scope.** The integrator extracts the pin from the BOM but does not yet reconstruct implementation nodes in its own graph — the pin is verdict-irrelevant on the integrator side (it relies via `covers`), so reconstruction is deferred.

**Rationale.**
- Without the pin, the BOM committed to the contract vector only; the assessor's signature (DEC-026) could be honoured against a *different* implementation behind the same contracts. Binding the content-ref closes that residual "same contracts, different code" gap and hands the integrator the exact content-addressed pointer it imports.
- Set semantics fall out of the model: a guarantee discharges its whole subtree, so its pin is every implementation under it. Reusing `desc` (the existing down-closure) keeps a single source of truth.
- `software_File` + `verifiedUsing` Hash is the SPDX Software-profile idiom; coins nothing. `sha1` is an explicit stand-in.

**Consequences.**
1. `seg_graph.py`: `impl_sha1(body)` stand-in helper; implementation nodes carry a `sha1` field.
2. `producer.py`/`supplier.py`: `p_impl`,`p_im256`,`p_im512`,`m_impl` carry `sha1`; `consumer.py`'s scenario-C own impl (`d_im2`) likewise.
3. `seg_composition.py`: `impl_member/2` closure; `contract_vector` returns `I` per contract.
4. `seg_commitment.py`: `member_hash` binds `I`.
5. `spdx_export.py`: emit `software_File` per pin, include in `member_iris` and in the member hash.
6. `consumer.py`: `parse_vector_bom` extracts `I` from `software_File` elements; `verify_contract` recomputes with `I`.
7. **Gate run before this entry.** Pipeline regenerated — member hashes / roots / document-root pins all move. Verdicts invariant (producer `conditional`; supplier `conditional`, `C[m_hal]={m_clk,m_pwr}`; integrator A total / B unsatisfied (G9) / C total / D total / E rejected). All three BOMs CONFORM under federated SHACL (`software_File` + `sha1` HashAlgorithm accepted). Six gates green (obligation 3/3, contract_vector, forward 5/5, forward_export 3/3, compliant_item 3/3, conformsto 3/3). Negative check: swapping a pinned impl `sha1` => member-hash mismatch => seal fails.

**Honest note.**
- `sha1` is a stand-in over the body label, not a real artifact hash; real content-addressing (git blob/commit sha, `downloadLocation`/`purl`) is deferred (the "detail worked out later" agreement). `sha1` as a HashAlgorithm is interim — a real pin would likely use sha256/gitoid.
- The pin binds *which* implementation, not that it *satisfies* the guarantee — entailment remains the assessor's judgement (DEC-026).
- The integrator does not yet wire the pinned implementation into its own `uses`/graph; only extraction + seal verification are implemented.
- Document roots changed versus all prior bundles; any externally recorded pins from earlier snapshots are stale by construction.
