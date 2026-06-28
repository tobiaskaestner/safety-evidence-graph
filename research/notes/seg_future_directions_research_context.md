# SEG — Research Context for Post-v1 Directions

**Purpose.** A self-contained starting point for three separate research
discussions — the **graph DSL / meta-model**, **repo generalization**, and
**composability**. v1 itself (the fixed, self-hosting build) is settled and is *not*
the subject here. Each direction below is recorded as an accepted *direction* in the
decision log (DEC-007, DEC-009, DEC-010) with a binding cheap-seam constraint for
v1; what remains is the actual design research, captured here as open questions.

This doc is deliberately enough to brief someone cold. For depth, the full set is:
the SEG design summary, `seg_decision_log.md`, `seg_architecture_constraints.md`.

---

## 1. The v1 baseline (what is being generalized)

SEG (the **SEG Toolbox**) binds safety requirements, tests, and code into a
hash-anchored graph and produces an integrity proof over it. In v1 everything below
is **fixed**:

- **Node types (5):** Requirement, TestSpecification, Implementation, TestOutcome,
  Waiver. **Edge types (7):** refines, verifies, implements (strong); confirms,
  witnesses, excuses (sink); calls (reserved). "Strong" edges propagate suspicion
  and participate in the Merkle computation; sinks do not.
- **Content→hash binding.** Every node has a content hash computed over **raw source
  byte spans** (a parser only *locates* the span; its output never feeds the hash).
  A strong edge stores `edgeHash` over both endpoints' hashes *at affirmation*; if
  either end's content changes, the edge goes **suspect** until a human re-affirms.
  The graph stores **only hashes**, never content.
- **Satisfaction (DEC-001).** A recursive predicate over the `refines` DAG: a leaf
  requirement is satisfied by ≥1 active verifies + ≥1 active implements + passing/
  waived outcomes; a non-leaf by all children satisfied (+ enforce-if-present on any
  direct edges). Transitive suspicion is derived and auto-clears (DEC-005).
- **Proof = two halves.** A **design** half (a Merkle root over the strong-edge
  design graph) + an **evidence** half (passing tests pinned to the source commit
  they ran against). Guarded by commit / proof / release gates. A proof is a
  *mechanical attestation* of integrity for a scope; *trust* (is the scope complete?)
  is a human judgment, and the tool reports partial-vs-total top-level scope
  (DEC-002).
- **Repos (4).** A=requirements, B=impl+testspec, C=test outcomes, G=graph store.
  Staleness binds a TestOutcome to repo B's HEAD (the code it ran against).

## 2. The unifying principle (applies to all three directions)

- **Fixed integrity core, configurable bindings.** The integrity mechanics —
  content→hash binding, suspicion propagation along strong edges, Merkle over strong
  edges, link-state semantics — stay fixed and universal. What generalizes is the
  *vocabulary and bindings* the mechanics operate over. Making the mechanics
  themselves configurable would dissolve SEG into a generic rules engine.
- **Configurable knobs are trusted-base.** Anything that changes what a hash or a
  "satisfied"/valid verdict *means* (the graph-type definition, hash-field
  selection, satisfaction rules, repo topology, referenced external proofs) is
  security-relevant: it must be versioned, hashed, and **bound into the proof**, or
  two parties could compute different "valid" proofs of the same graph.
- **v1 seams make these plug-ins, not rewrites.** v1 isolates the variable parts
  behind interfaces (taxonomy provider AC-001, satisfaction evaluator AC-002, input
  adapters AC-003, interface adapters AC-014, repo-topology config AC-015,
  composition-enabling invariants AC-016) and ships the built-in safety model behind
  them. No v1 backlog impact.

---

## 3. Direction A — Graph DSL / meta-model (DEC-007)

**The idea.** Turn SEG from "the safety-evidence-graph tool" into a graph-integrity
engine parameterized by a **graph-type definition** that declares node types, edge
types (endpoint types, direction), the strong flag, the per-node *logical*
hash-field selection, and the satisfaction logic. The current 5/7 safety model
becomes the built-in definition.

**Decided / bounded.**
- Generalize vocabulary + satisfaction; keep integrity mechanics fixed.
- Hash-field layering: the definition picks the *logical* hash-field structure; the
  language binding maps each logical field to raw source byte spans (preserves the
  raw-byte / parser-as-locator discipline).
- **Satisfaction must be a decidable, auditable formalism — stratified Datalog —
  not a Turing-complete language.** Rules decide proof validity, so they must be
  terminating, deterministic, side-effect-free, and human-auditable. Recursion/
  transitive closure, stratified negation, and existence/universal conditions all
  fit Datalog; termination is guaranteed. A functional/Prolog/Pythonic-compiled
  option is rejected for the default path (an "unsafe" non-safety mode at most).

**Open research questions.**
- Definition format: declarative config (JSON/YAML), a profile over JSON Schema +
  SEG annotations, or a small custom DSL? How to express domain/range, direction,
  strong flag, hash-field selectors.
- Relation to the per-instance JSON Schemas: does the definition *generate* them,
  *reference* them, or both?
- Datalog integration: which dialect (stratified negation; aggregation or not)?
  embed an existing engine vs implement semi-naive evaluation? how do graph facts
  (nodes, edges, link-states, outcomes) map to relations and get fed in?
- TCB mechanics: canonical serialization of the definition + ruleset for hashing;
  how the proof references the definition/ruleset version.
- The boundary: where exactly does "vocabulary" end and "satisfaction" begin? Are
  gates also Datalog or fixed predicates? How does a configurable strong-flag
  interact with the fixed Merkle?
- Self-application: express the built-in safety-evidence graph type as the first
  definition (dogfood the meta-model on itself).
- Anchor formalisms / prior art: Datalog; SHACL/ShEx, GraphQL SDL, ontology
  languages (as comparison points for the declarative half).

## 4. Direction B — Repo generalization (DEC-009)

**The idea.** Make the repo topology user-configurable: how many repos, their names,
their roles, and which node types draw their source from which repo. This is the
*content-source/topology facet of the meta-model* (Direction A), not a separate
axis — "where a node type's source lives" is an attribute of the node type.

**Decided / bounded.**
- Fixed core: staleness/hashing/Merkle unchanged. Staleness generalizes *for free* —
  freshness binds to the HEAD of the repo holding the depended-on source, which falls
  out of the dependency chain (witnesses→implementation→source-repo). Configure the
  *mapping*, not the *semantics*.
- Already config today: `seg.yaml` maps repo names → physical paths/worktrees. Only
  the count/names/roles and the node-type→repo mapping are hardcoded.
- TCB: when configurable, the topology is proof-bound — `sourceRepo` enum →
  config-validated logical name; `EvidenceManifest`'s fixed four SHAs → a
  `{repo → SHA}` map; `snapshotId` hashes the configured set.

**Open research questions.**
- The repo "role" ontology: is {source-for-node-types, graph-store, artifact-store}
  complete? Can a repo hold multiple roles? Can one node type span repos?
- Layering: logical topology (roles, node-type→repo) likely belongs in the
  (TCB, proof-bound) graph-type definition; physical mapping (names→paths) stays in
  `seg.yaml` (not TCB). Confirm the split.
- Staleness for node types with no execution dependency — what binds their freshness?
- Canonicalizing a variable repo-SHA set for the `snapshotId` hash.
- Interaction with the single-repo-as-branches realization (physical mapping is
  already config; only the logical set generalizes).

## 5. Direction C — Composability / assume-guarantee proof (DEC-010)

**The idea.** A product proof can *rely on* another project's sealed proof instead of
re-proving an imported component (e.g. a product using the Zephyr RTOS relies on
Zephyr's RTOS proof). The product imports the requirement **boundary** it depends on
(pinned by hash) and references the dependency's proof as the discharging evidence.
This is **assume-guarantee composition**: the product *assumes* the imported
requirements hold; the referenced proof *guarantees* them; valid **iff the product's
assumptions ⊆ the scope that proof actually proved.**

**Decided / bounded.**
- New modeling: an *imported requirement* node (hash-pinned) + a `dependsOn` edge +
  an external-proof reference as evidence (not a Waiver — this is positive evidence
  from elsewhere). Extends DEC-001 satisfaction with a third discharge case
  (satisfied-by-external-proof); composes with Datalog satisfaction.
- The external proof is **referenced + fingerprinted** in the EvidenceManifest, not
  folded into the product's Merkle (preserves the design/evidence separation).
- Two non-negotiable soundness checks: **scope-match** (assumptions ⊆ proven scope —
  makes the DEC-002 scope signal load-bearing) and **version-pin** (imported
  requirements hash-pinned to the proved version; upgrades go stale until
  re-validated — cross-graph staleness).
- Trust stays verifiable: each proof is independently verifiable; a product proof can
  distinguish **discharged** from **undischarged** assumptions.
- **Hard prerequisite:** globally-unique, stable requirement IRIs — the deferred
  namespace genericity (v4 §14 / DEC-002) becomes mandatory here.

**Open research questions.**
- Exact boundary model: the imported-requirement node, the `dependsOn` edge, and the
  external-proof-reference evidence shape; how the imported hash is pinned and matched.
- Scope-match mechanics: expressing/verifying assumptions ⊆ proven-scope; behaviour
  when the dependency proof is partial; **transitive composition** (A relies on B
  relies on C) — does it chain soundly, and how deep does verification go?
- Version-pin / cross-graph staleness: detecting the imported proof is stale; what
  triggers re-validation.
- Trust chain + provenance: what the auditor verifies; what the EvidenceManifest's
  external-reference section records; do you trust a foreign proof because you
  recomputed its Merkle, or *also* because it is signed by an identity? (signing /
  identity of foreign proofs.)
- Identity/namespace: cross-project IRI uniqueness and stability; referencing foreign
  requirement IRIs; versioned namespaces.
- Conditional proofs: representing and reporting undischarged assumptions.
- Anchor formalisms / prior art: assume-guarantee reasoning, contract-based design,
  compositional verification — and how SEG's hash-pinned boundary maps onto them.

---

## 6. Cross-cutting: prerequisites and ordering

- **Dependency order.** Composability (C) depends on the meta-model (A), the
  namespace story, and a stable proof format. Repo generalization (B) is a facet of
  (A) and rides with it. So a rough roadmap is: **A (with B) → namespace → C.**
- **Namespace genericity** has graduated from "nice to have" to a **hard prerequisite
  for composability**. It is cheap to decide early and expensive to retrofit once
  IRIs are baked into committed graphs and proofs — the one item worth pulling
  forward in planning.
- **Out of scope for these three discussions:** the REST/interface direction
  (DEC-008) is an engineering concern, not research; it shares the
  engine-as-library seam (AC-014) but does not need its own research thread.

## 7. Pointers

- Decisions: `seg_decision_log.md` — DEC-001/002/005 (v1 satisfaction, scope/trust,
  suspicion), DEC-007 (meta-model + Datalog), DEC-009 (repo topology), DEC-010
  (composability).
- Constraints: `seg_architecture_constraints.md` — AC-001/002/003 (seams),
  AC-011/013/014/015/016 (future-proofing).
- Baseline design: the SEG design summary.
