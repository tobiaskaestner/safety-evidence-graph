# SEG Decision Log

Binding design decisions for the Safety Evidence Graph (SEG) project. This is
the authoritative, citeable record. The language-agnostic / C-oriented design
of record is `knowledge_graph_design_summary_v4.md`; the concrete Python +
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
→ software requirements) triggers this on day one. Transitive closure is also
the only rule consistent with the §7.2 Merkle traversal, which already
aggregates a parent from its in-neighbours. Vacuous-truth, partial-scope, and
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
