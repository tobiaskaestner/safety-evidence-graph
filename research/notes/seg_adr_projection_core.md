# ADR — The Projection-Core Architecture (the "prism" stance)
 
**Status:** Accepted (architecture stance). Suggested decision-log entry: DEC-011,
cross-referencing this document. Supersedes the implicit assumption that SEG must
adopt a single canonical graph data model.
 
**Context docs:** `seg_prior_art.md`, `seg_reconciliation.md`, `seg_glossary.md`.
**Evidence (runnable):** `seg_demo_shacl_projection.py`, `seg_demo_datalog_projection.py`.
 
---
 
## 1. Context
 
The reconciliation work showed SEG is an integration of five well-charted layers
(typed graphs, SHACL-style shapes, recursive-fixpoint satisfaction, Merkle/
accumulator commitments, assurance-case argumentation) plus two seams. To maximise
reuse of existing engines, SEG would naturally adopt those engines' data models —
but the engines disagree: SHACL is RDF-bound, the property-graph tooling speaks
LPG, SACM is an OMG/MOF model, in-toto/DSSE is JSON attestations. No single model
serves all layers.
 
Two facts forced the decision:
 
1. **SEG's core store is nobody's native model.** It holds *only* identities,
   types, hashes, and computed link-states — never content. It is integrity-shaped,
   not RDF- or LPG-shaped.
2. **SEG edges are unusually payload-bearing** (each carries an `edgeHash`, a
   link-state, affirmation metadata). RDF triples cannot hold edge attributes
   (forcing reification); LPG holds them natively but lacks a mature shape language.
Crowning any one model canonical contorts the core and marries SEG to one
ecosystem's compromises.
 
## 2. Decision
 
Keep the core **integrity-shaped** and treat every external model as a
**projection**: a pure, deterministic, one-directional function from the core to
the shape a given layer's engine consumes.
 
- Structure / well-formedness → project to **RDF**, validate with **SHACL**.
- Verdicts (satisfaction, suspicion) → project to **Datalog facts**, evaluate with
  a stratified engine (Soufflé / Nemo).
- Signed proof → project to **in-toto / DSSE**, sign via **Sigstore** *(deferred —
  see §7)*.
- Auditor interchange → project to **SACM**.
The set of projectors is the system's "prism": one source, dispersed lawfully into
per-layer views.
 
## 3. The two invariants
 
These are the load-bearing rules; the stance is sound only while both hold.
 
1. **Projections are write-only (one-directional).** A projection is derived
   output, like a compiled object file: regenerated from the core on demand, never
   hand-edited, never parsed back into the core. Drift between stores requires *two*
   independently authored stores; here only the core is ever authored. Round-tripping
   is the one prohibited operation.
2. **Each layer consumes the core's *computed verdicts*, never recomputes the
   core's job.** The integrity core owns "did the bytes change" (a hash
   recomputation, surfaced as a link-`state`). A downstream layer consumes that
   `state` as a given and produces *its own* derived facts; it must not be handed
   content/hashes and asked to recompute drift. This keeps each layer inside its
   tractable fragment (e.g. stratified Datalog).
## 4. Framing: from prism to multi-camera
 
The prism analogy is right about the essentials — one source, lawful dispersion,
nothing invented, one-directional (you don't push light back into a prism). Keep it
as the intuition (and likely in the paper).
 
It is **wrong about one thing: partition.** A prism sends each wavelength to exactly
one exit; SEG projections *overlap deliberately*. The same core datum (e.g. an
edge's `state`) is dispersed to multiple layers at once — SHACL shape-checks it as a
valid enum *and* Datalog reasons over its value. The accurate image is **several
cameras with different filters photographing one scene**: each filter reveals an
aspect, the scene is the single source, the photos are derived and read-only — but
the cameras share the same photons freely. Do not enforce disjointness between
projections; overlap is correct and necessary.
 
## 5. Evidence (two runnable demos)
 
**A. SHACL projection — `seg_demo_shacl_projection.py`.** A core fragment
(identities/types/hashes/states) is projected to RDF; payload-bearing edges are
reified (edge-as-node with `from`/`to` + `edgeHash` + `state`); real pySHACL 0.31
validates it. The well-formed fragment conforms; a malformed one (a `verifies` edge
originating from a Requirement instead of a TestSpecification) fails with a precise,
engine-generated diagnostic. This is exactly the endpoint-typing check an early
hand-rolled checker did — now performed by a standardised engine with zero
validation code written, only shapes. (Shapes themselves are projectable from the
graph-type definition, so structure-checking becomes configuration, not code.)
 
**B. Datalog projection — `seg_demo_datalog_projection.py`.** The same style of
core is projected to ground facts; stratified satisfaction + suspicion rules run to
fixpoint. (A small self-contained stratified evaluator stands in for Soufflé, which
is a C++ binary unavailable in the demo sandbox; the demo evidences the *projection
stance*, not engine performance.) Result: with all edges active, all requirements
are satisfied and none tainted; when the core recomputes one edge as `suspect`, the
verdict splits correctly — the affected leaf leaves the satisfied set, and taint
propagates *up the refines DAG* to the scope root (transitive suspicion), while the
independent sibling and its evidence stay clean.
 
What B proves about the invariants: the Datalog layer reads `state` (the same datum
SHACL read — the overlap) and emits *new* derived facts (`sat`, `tainted`) that go
**to the user, not back into the core**. Invariant 1 holds. And the suspicion *seed*
lived in the projection boundary: Datalog never computed drift, it consumed the
core's already-computed `state`. Invariant 2 holds, and is what keeps the rules in
the stratified fragment.
 
**C. Verdict layer on real clingo — `seg_demo_clingo_verdict.py`.** The same core
is projected to ASP facts and the satisfaction + suspicion rules run unchanged on
clingo 5.8 (Potassco), with a **determinism guardrail**: a SEG verdict must be a
*single* answer set. Findings: (i) on the acyclic fragment, both the all-active and
the one-suspect cases return *exactly one* answer set, reproducing the earlier
verdicts — so clingo is a sound prototype substitute for Soufflé, with the rules
unchanged across engines (the projection-agnostic-evaluator property). (ii) When a
`refines` cycle is injected (violating the acyclic facet), clingo returns *two*
answer sets and the guardrail trips ("verdict undefined"). This is the executable
form of the long-standing claim that satisfaction is well-defined only over an
acyclic refines graph: on a cycle the universal "all children satisfied" becomes an
even negation loop with multiple stable models. The acyclic facet therefore has a
*third, runnable* justification (alongside the recursive `merkleHash` aggregation
and the recursive satisfaction predicate), and the entailment-lattice edge
`satisfaction-role ⟹ acyclic` is now a reproduced result, not a claim.
 
**Engine recommendation (prototype).** Build the verdict layer on **clingo**
(pip-installable, embeddable Python API, rules run as-is). Ship the
**single-answer-set guardrail** (`len(models) == 1`) as a standing invariant: it
converts "did we leave the tractable fragment?" from a subtle semantic worry into a
hard, fail-loud check on every evaluation. Keep the acyclic facet enforced upstream
(SHACL or a structural check) so the guardrail catches bugs, not routine operation.
If Zephyr-scale grounding becomes a memory issue, the projection lets clingo be
swapped for Soufflé/Nemo with the rules largely intact.
 
## 6. Consequences
 
**Positive.**
- The core never marries an external model; each layer gets the view it likes best.
- Structure-checking and verdicts become orchestration over mature engines (SHACL,
  Datalog) rather than bespoke code — small implementation surface.
- Single source of truth: if both data *and* shapes/rules are projected from the
  core + graph-type definition, nothing downstream is independently authored, so
  nothing downstream can drift from the source.
- Clean soundness split: core computes facts; projections re-express them; engines
  check/reason over them; no layer encroaches on another's job.
**Negative / cost.**
- One projector per consumer must be written and maintained.
- Reification makes the RDF projection verbose (mechanical, but bulky).
**Residual risk (and its containment).**
- The only way a projection can be *wrong* is a bug in a projector function. This is
  a deterministic, testable unit — property-test each projector (core fact ⇒
  expected projected fact). It is a far smaller and more tractable risk surface than
  a second hand-maintained store.
## 7. Alternatives considered
 
- **RDF as canonical model.** Unlocks SHACL directly, but contorts payload-bearing
  edges (reify everywhere) and imposes RDF identity semantics on the core. Rejected
  as the *canonical* model; retained as a *projection target*.
- **LPG as canonical model.** Fits edges and identity naturally, but there is no
  mature, standardised shape/constraint language for LPG — would mean reimplementing
  the structural layer or betting on young tooling. Rejected as canonical.
- **Projection-core (chosen).** Neither model is canonical; the integrity-shaped
  core is, and RDF/LPG/Datalog/SACM/DSSE are projections.
## 8. Deferred / open
 
- **Signed external projection (in-toto / DSSE / Sigstore).** The one consumer not
  yet pressure-tested: whether a *signed, externally verified* projection stays
  write-only when a foreign party must verify it independently. Judged tractable;
  to be handled when composability (DEC-010) is built. Connects to the known
  in-toto actor-authentication gap (recompute-the-Merkle vs also-require-a-signature).
- **Global stable identifiers (IRI-style).** RESOLVED — the core assigns each node
  an IRI; the *namespace* is a per-graph definition parameter, the *local part* is
  data minted at extraction. Identity is stable and is NOT a `hash_field` (content
  drifts; identity does not). Projectors carry the IRI through rather than minting
  their own. Unblocks DEC-010 scope-match. (Decided after this ADR; recorded here.)
- **Glossary additions.** `projection`, `projector`, `projection-core`,
  `write-only projection`; and from §10: `identity field`, `committed content`,
  `tracked field`, `verdict reproducibility`, `static invariant`, `field routing`.
## 9. Relationship to existing decisions
 
- Realises the cheap-seam interfaces (AC-003 input adapters, AC-014 interface
  adapters) as the projector set.
- The stratified-Datalog verdict layer is DEC-007; this ADR fixes *where* it sits
  (a projection consumer) and *what it may read* (computed `state`, not content).
- Composability (DEC-010) inherits the signed-projection deferral in §7.
## 10. Extension — the definition is also a projection (schema-level)
 
The stance applies one level up. The graph-type **definition** is itself projected
(transpiled) to three back-ends — SHACL (structure), stratified Datalog (verdicts),
and core/commitment config (hashing, drift, fingerprint membership). Same discipline,
same payoff: a single authored source means the structural and verdict layers
*cannot disagree* about what a valid graph is (the consistency guarantee), and sealing
the *generated artifacts* rather than the DSL source keeps the transpiler **out of the
trusted base** — a verifier runs stock pySHACL + clingo over readable artifacts and
never needs the transpiler. Full grammar, field model, facet model, and routing in
`seg_definition_language.md`.
 
Two cross-cutting results from that work belong on the record here:
 
**Verdict reproducibility (sealed, not live).** A sealed verdict (`satisfied`, …) is a
*pure function of committed content + sealed evidence*, so any verifier recomputes the
same verdict from the proof alone. This forces a third node-field category beyond
identity and committed content: **`tracked`** fields (e.g. ADR `status`) are carried
and queryable but are outside the commitment and **must not** be upstream of any sealed
verdict. If a workflow value must gate a sealed verdict, it is *promoted* to committed
content (its changes then count as drift) — never read while still tracked.
 
**A family of static invariants is the real trusted core.** SEG's soundness reduces to
a handful of *static, fail-loud* checks over the definition + ruleset, decidable before
anything runs: (1) field-routing totality & exclusivity; (2) acyclicity of the *union*
of `fingerprint:deep` edge types; (3) verdict purity — no sealed verdict reads a
`tracked`-derived relation; (4) verdict determinism — exactly one answer set on
well-formed input (clingo guardrail). These are the same kind of artifact recurring,
and together they, not the engines, constitute what must be trusted. Worth foregrounding
in the paper.