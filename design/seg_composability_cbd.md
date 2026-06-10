# SEG — Composability via Contract-Based Design (DEC-010)
 
**Status:** Working draft, for ratification. The CBD vocabulary and the
refinement-against-a-slot model are proposed as the formal backbone of DEC-010;
the *mechanization* choices in §7–§8 (especially the decidability stance) are
flagged as decisions still open. Supersedes the informal "valid iff assumptions ⊆
proven scope" phrasing, which §3 shows was a fuzzy gesture at contract refinement.
 
**Related:** `seg_prior_art.md` (the assume-guarantee seam), `seg_paper_seed.md`
(contribution 3), `seg_adr_projection_core.md §8` (signed external projection —
the deferred actor-authentication corner), `seg_definition_language.md` (edge model).
**Illustrations:** `seg_composition_v1.svg` (two-org overview),
`seg_composition_v2.svg` (the import as two obligations),
`seg_composition_requirements.svg` (**primary** — the two-space set view in the
requirement lattice), `seg_composition_settheoretic.svg` (the same in behaviour-set
/ trace form — formal grounding).
**Demos:** `seg_demo_clingo_partial_discharge.py` (residual + the three verdicts,
single-level import), `seg_demo_clingo_transitive.py` (A→B→C reliance chain,
two-hop staleness propagation, reliance-cycle guardrail).
 
---
 
## 1. Stance in one line
 
A cross-project import is **contract refinement**. The producing project proves,
once and sealed, that its component *satisfies* its contract; every consuming
project then performs only a cheap, evidence-free *refinement* check against the
contract it advertised. Composition scales because satisfaction is amortized into
a reusable proof and importers never re-verify it.
 
## 2. Vocabulary (standard CBD)
 
Taken from contract-based design (Benveniste et al.); we adopt the terms verbatim
rather than coin our own.
 
A **behavior** is an execution trace over the relevant variables/ports; the
universe of behaviors is `B`. A **contract** `C = (A, G)` is a pair of behavior
sets: the **assumptions** `A ⊆ B` (the environments the component admits) and the
**guarantees** `G ⊆ B` (what it promises). An **implementation** (component)
`M ⊆ B` **satisfies** `C`, written `M ⊨ C`, iff `M ∩ A ⊆ G` — within the assumed
environment, every behavior of the component is guaranteed. An **environment**
`E ⊆ B` is **compatible** with `C` iff `E ⊆ A`.
 
**Refinement (dominance).** `C ⊑ C′` ("C refines C′"; C is the stronger, more
committed contract) iff
 
> `A ⊇ A′`  and  `G ⊆ G′`.
 
In words: **demand less of the environment, promise more to clients.** The two
halves move in opposite directions — this is the duality the set diagram draws.
Refinement is exactly substitutability: `C ⊑ C′` implies every implementation of
`C` implements `C′`, and every environment compatible with `C′` is compatible with
`C`. So a component honoring `C` is safe to drop wherever `C′` was expected.
 
**Saturated form (caveat).** The refinement condition above is exact only when
guarantees are in *saturated* form `G ∪ ¬A` (a behavior outside the assumptions is
vacuously acceptable). Over the naive `G`, `G ⊆ G′` is a sound but conservative
check (it can reject a genuinely valid import). For SEG's likely property language
(bounds, flags, enums) the two usually coincide; §7 records this as an open
mechanization point, not a free choice.
 
**Behaviours vs requirements (framing caveat).** A **behaviour** (trace) is one
complete run of the system — a single observation of the watched variables over
time; the *meaning* of `A` or `G` is the **set of all runs that conform to it**.
CBD's `⊆` is therefore over behaviour sets, and is **contravariant to requirement
strength**: a stronger guarantee admits *fewer* runs, so it is the *smaller* set.
Practitioners reason in the dual *requirement* lattice (more constraints = larger),
where the identical facts read with the inclusions flipped — `need ⊆ provided`
(`G_slot ⊆ G_up`) and `demanded ⊆ committed` (`A_up ⊆ A_slot`). The **primary**
diagram (`seg_composition_requirements.svg`) uses the requirement lattice; the trace
form (`seg_composition_settheoretic.svg`) is the formal grounding. Always state which
lattice is in force before drawing, or the audience will silently invert it — this is
the single most common point of confusion when CBD meets a requirements-trained room.
 
## 3. The two SEG roles: component contract and slot
 
There are exactly two contracts at an import boundary.
 
- **`C_up = (A_up, G_up)`** — the *upstream component contract*. The producing
  project's sealed proof witnesses `M_up ⊨ C_up`: the real artifact, under its
  assumptions, delivers its guarantees.
- **`C_slot = (A_slot, G_slot)`** — the *dependency slot*, i.e. the **required
  contract** the downstream design authors for the hole it intends to fill,
  *before and independently of* any concrete upstream. In component-model terms
  this is a required-interface / port contract.
  - `G_slot` = what downstream needs the filler to guarantee.
  - `A_slot` = the environment downstream commits to providing the filler.
"Slot" is informal shorthand; the doc-of-record term is **dependency's required
contract**. Bridge to the diagram labels (which were intuition-first, so the roles
cross over):
 
| CBD role (this doc) | Diagram label | RTOS example |
|---|---|---|
| `G_slot` (slot guarantee) | `A_down` | "needs dispatch ≤ 100µs" |
| `A_slot` (slot assumption) | `E_down` | "app runs single-core, short ISRs" |
| `G_up` (component guarantee) | `G_up` | "dispatch ≤ 50µs (verified)" |
| `A_up` (component assumption) | `A_up` | "single-core, short ISRs, tick ≤ 1kHz" |
 
## 4. The import check
 
The import from upstream into the slot is sound iff the concrete component contract
refines the abstract slot:
 
> `C_up ⊑ C_slot`  ⟺  `A_up ⊇ A_slot`  and  `G_up ⊆ G_slot`.
 
This is the formal statement, over behaviour sets (the trace lattice); the
requirement-lattice reading flips the inclusions to `G_slot ⊆ G_up` and
`A_up ⊆ A_slot` (same facts — see §2 caveat). The two halves are the two pictures in
the set diagrams (`seg_composition_requirements.svg`, primary;
`seg_composition_settheoretic.svg`, trace grounding):
 
- **Guarantee side**, `G_up ⊆ G_slot`: upstream guarantees at least what downstream
  needs. (`≤ 50µs` ⊆ `≤ 100µs`.) The *latency space*; upstream is the inner set in
  the trace view (the outer set in the requirement view).
- **Assumption side**, `A_up ⊇ A_slot` (equivalently `A_slot ⊆ A_up`): downstream's
  committed usage stays inside what upstream assumes. The *usage space*; upstream is
  the outer set in the trace view (the inner set in the requirement view).
This resolves the long-open "does `dependsOn` encode refinement or a discharge
check?": **refinement at the top, two discharge inclusions underneath.**
 
## 5. Why the split matters: satisfaction vs refinement
 
The model cleanly separates two activities SEG had been conflating.
 
**Satisfaction** — *an implementation meets its contract* (`M_up ⊨ C_up`). The
expensive half: the full design+evidence graph, the test outcomes, the merkle
commitment. Done once by the producer and sealed into the proof.
 
**Refinement** — *one contract substitutes for another* (`C_up ⊑ C_slot`). The
cheap half: a structural comparison of advertised `A`/`G` boundaries only, with no
evidence and no re-verification.
 
The consumer trusts the sealed proof for `M_up ⊨ C_up` and performs only the
refinement check. The costly verification is amortized across every importer —
which is the entire reason the proof object earns its keep, and the precise sense
in which SEG's contribution 3 (composition of sealed proofs) is more than OFT/Doorstop
can do: they have no contract and no proof, so no substitutability calculus.
 
## 6. Algebraic structure: composition, conjunction, quotient (why behaviours)
 
Composability *works* — and CBD insists on behaviour sets rather than requirement
text — because contracts form an **algebra** whose operations are Boolean set
operations on the behaviour sets. For contracts in saturated form (`¬A ⊆ G`; saturate
by `G ↦ G ∪ ¬A`), over a common alphabet:
 
| Operation | Definition | Reads as |
|---|---|---|
| refinement `C₁ ⪯ C₂` | `A₁ ⊇ A₂` and `G₁ ⊆ G₂` | substitutability: `C₁` may replace `C₂` |
| composition `C₁ ∥ C₂` | `( (A₁∩A₂) ∪ ¬(G₁∩G₂),  G₁∩G₂ )` | run both together; each partner's guarantee discharges part of the other's assumption |
| conjunction `C₁ ∧ C₂` | `( A₁∪A₂,  G₁∩G₂ )` | one artifact, two viewpoints (latency ∧ safety); any implementation satisfies both (the meet) |
| quotient `C / C₁` | largest `C₂` with `C₁ ∥ C₂ ⪯ C` | the **missing component**: what the remaining piece must satisfy |
 
**Why behaviours, not requirements.** Every operation above is `∩`, `∪`, `¬` on
behaviour sets — *defined* operations precisely because the domain (sets of traces) is a
Boolean algebra closed under them. A *requirement* is syntax; it has no intersection or
complement until given a behaviour-set denotation, at which point you are back in the
behaviour algebra. The algebra therefore does not come from requirements; it comes from
the denotation, and the requirement view (the practitioner lattice of §2) inherits it
only through the syntax⊣semantics Galois connection. This is the formal content of the
"behaviours carry structure, requirements don't" split: the requirement lattice is the
*presentation*, the behaviour algebra is the *justification*.
 
**The load-bearing law: refinement is a congruence for composition.** Because `∥` is
built from monotone set operations and `⪯` *is* set inclusion, refinement is preserved
by composition. The monograph states it two-sided and adds compatibility preservation:
 
> if `C₁` is compatible with `C₂`, and `C₁′ ⪯ C₁` and `C₂′ ⪯ C₂`, then `C₁′` is
> compatible with `C₂′` and `C₁′ ∥ C₂′ ⪯ C₁ ∥ C₂`.
 
(Our one-sided `C₁ ⪯ C₁′ ⟹ C₁ ∥ C₂ ⪯ C₁′ ∥ C₂` is the special case `C₂′ = C₂`.) For
A/G contracts `∥` is moreover **associative and commutative** (the monograph's Axiom 4
holds — full associativity, not merely the meta-theory's weaker sub-associativity). This
is what licenses **independent development** — formalized as conditions (2.2)–(2.3):
each supplier refines its own contract in isolation, integration yields an implementation
of the composed contract, and the composite refines the top-level contract `C`. It is
the formal backbone of §1 and §5 — the precise reason a downstream import can trust a
sealed upstream proof and check only refinement. The compatibility-preservation clause
also matters to SEG: a drift that breaks *compatibility* (not just refinement) is a
distinct failure mode worth surfacing.
 
**Composition + quotient = the SEG composition problem.** Assembling pre-existing
artifacts to discharge a product contract is exactly: compose what you have
(`C₁ ∥ … ∥ Cₙ`) and ask whether the result refines the product contract `C_prod`. The
slot of §3 is the quotient `C_slot = C_prod / (C₁ ∥ … ∥ Cₙ)` — the contract the missing
artifact must satisfy. In IEC 61508 terms this *is* the safety argument: the reasoning
that the product's design is safe is the demonstration that the composed component
contracts refine the product safety contract, each component's satisfaction discharged by
its (sealed) evidence and its safety manual supplying its assumptions. (Terminology
note: "safety case" is the *colloquial* name used in secondary functional-safety
literature for the reasoning that a product is safe; it is **not** a defined term of
IEC 61508 itself — IEC 61508 speaks of functional safety assessment and required
documentation. "Safety case" is a genuine/defined deliverable in EN 50129 and the
GSN/SACM assurance-case literature.)
 
*Sources (verified against the 2018 monograph, primary text):* saturation, eq (5.6)
`G = G ∪ ¬A`; refinement, conjunction, parallel composition, Definition 5.4 (with
composition `(A,G)` per eq (5.7) — confirmed verbatim); congruence + compatibility
preservation, the monotonicity result in §2.1; associativity, Summary of Results 1
(Axiom 4); quotient as the adjoint/residuation of `∥`, §4.5 / Property 7
(`C ⪯ C₁/C₂ ⟺ C ∥ C₂ ⪯ C₁`). The closed-form A/G quotient expression is *not* in this
monograph (it uses the adjoint definition); the closed form is the separate Incer et al.
contribution — cite that only if the closed form is actually needed.
 
**Model scope (what `B` is, and what it isn't).** The algebra above is *prefix-
independent*: it is powerset Boolean algebra over whatever the behaviour universe
`B` is, and holds for any `B`. But the *physical reading* depends on `B`'s structure,
and two things must not be conflated:
- The **demo's `B`** (`seg_demo_contract_algebra.py`) is a set of *flat abstract
  outcomes* — triples like `(single, short, M)` summarising a whole run by a few
  end-of-run observations. These have no internal time order, so there is **nothing
  to take a prefix of**, and the demo cannot express genuinely temporal properties.
- The monograph's Section-4 machinery (prefixes, prefix-closure, receptiveness, the
  Moore-interface / input-output **port partition**) belongs to a richer `B` of
  *timed traces*. That structure is what would let SEG state real RTOS guarantees
  ("the highest-priority ready task is *eventually* dispatched within 50µs", "never
  deadlocks") — liveness/safety properties that a flat `B` cannot even represent.
  It is also the formal home of the demo's known limitation: with no port partition,
  a shared coordinate (e.g. `isr`) appears on both the assumption and guarantee
  sides, which is why composed assumptions in the demo carry saturation artifacts.
This bears directly on §7: if SEG's real `B` is timed traces, the property language
stops being free `∩/∪/¬` and needs temporal-logic / automata machinery, sharpening
the decidability problem — another argument on the *human-affirmed refinement* side.
## 7. Decidability of the refinement check (RESOLVED: human-affirmed)
 
SEG does not store behavior sets; it stores `A`/`G` as *properties* (a latency
bound, a set of config flags). So `⊆`/`⊇` become **entailments between
properties**, and the refinement check is only as tractable as the property
language. In general it is undecidable. Two options:
 
1. **Restrict the contract property language** to a decidable/trivial fragment
   (numeric bounds, enums, boolean flags) so refinement is *computed* — a verdict
   predicate of the same family as `satisfied`, hence reproducible and sealable.
2. **Treat refinement as a human affirmation.** The integrator asserts the refinement
   (having read the safety manual), and the assertion is bound by `edgeHash` over both
   endpoints' content exactly like any other affirmation. Drift re-suspects it.
**Resolved: option (2)** — refinement is a human affirmation, with (1) retained only as
an optional accelerator for the mechanizable fragment. The mechanization in §8 is built
on this: affirmation = the act of activating a discharge edge. Rationale: it reuses the
affirmation + drift machinery wholesale, sidesteps undecidability, and *matches IEC 61508
reality* — a human integrator reads the safety manual and judges conformance; the
standard does not imagine this as automatic. It is the exact analog of the satisfaction
layer's "stay in the stratified fragment" stance: the hard general problem is avoided by
construction, not solved. (The decision is reinforced by the timed-trace argument in §6:
if the real `B` is timed traces, even *stating* the entailment needs temporal-logic
machinery, so computing it is the wrong default.)
 
## 8. Mechanization in SEG: the discharge rule-set
 
The mechanization is a single, type-uniform notion of **discharge**, governed by the
verdict rule-set and always realized as an **active edge**.
 
**Affirmation means exactly one thing (edge activation).** To *affirm* an edge is the
human, semantic-level act of asserting that its endpoints genuinely relate —
flipping the edge from `pending` to `active`, bound to the endpoint content hashes,
drift-sensitive. Affirmation carries no payload of its own; it is the *act*, not a
*thing*. (Earlier drafts let "affirmation" also mean "a justification with rationale";
that conflation is dropped. Rationale is content — see *Witness* below — not a flavour
of affirmation.)
 
**Discharge invariant.** A node is *discharged* iff the relevant edge is **affirmed
active**. This single invariant is what makes staleness uniform: any drift in either
endpoint's content re-suspects the edge, re-opening the discharge, regardless of which
discharge rule applied.
 
**Node types.** Requirements are one type — a *product requirement* and a
*condition-of-use requirement* are both just `Requirement`; their role differs only in
how they arrived (authored vs imposed via an import). A **Witness** is the genus of
things that can discharge a requirement by observation/authorship, with two species:
`TestOutcome` (observed evidence, existing) and **`DesignReview`** (a human-authored
witness — a review/analysis with a body, NEW). Upstream nodes relied upon are embedded
**by reference** (IRI + content hash, attested by the manifest), not copied; they sit
in the downstream *design* subgraph. The upstream **sealed manifest** (evidence side)
witnesses `M_up ⊨ C_up`.
 
**The manifest node (hybrid form, decided).** The sealed manifest is a first-class
**`Manifest` node** on the evidence side, owning the *shared, recomputed* facts: the
upstream **component identity** (stable IRI), version, sealed digest / proof URI, and
`seal_ok` (recompute + authenticity). A `relies-on` edge owns only the *reliance-specific*
facts — which `G_up` it leans on and the single refinement affirmation — and **references**
the `Manifest` node for its verification backing. Why a node, not an edge property: the
manifest is *shared* (many reliances, one component); it is the *witness* for the
seal-verification fact, so it belongs with the other witnesses as a node; and a re-seal
changes one node's content hash, re-suspecting every reliance pointing at it in one place
(rather than N edge-copies that could fall out of lockstep). The mode-2
**impl-uses-impl** clause anchors here: the `Manifest` node *is* the downstream graph's
representative of the single upstream implementation actually linked.
 
**Version consistency (well-formedness, validation layer).** A downstream build links at
most one implementation per upstream component, so the rule is: **at most one `Manifest`
per upstream-component-identity, and every reliance resolving to that component references
it.** This is a static structural check (group reliances by component identity; assert a
single manifest) — *validation* layer, not verdict — and it is the graph-level encoding
of the physical invariant that only one upstream implementation can exist. A graph cannot
rely on v1.4.2 for half its requirements and v1.5 for the rest. (Join key: the component's
stable IRI, distinct from version. Assumes upstream exposes that identity in the manifest
— a safety manual is *for* a named compliant item — confirm at schema time.)
 
**The discharge rule (two modes, every requirement).** A `Requirement R` is discharged
iff its discharge edge is affirmed active AND one of:
 
- **Mode 1 — witness.** Active edge from a `Witness` (a `TestOutcome` and/or a
  `DesignReview`), hash-bound to the tested/reviewed content. Applies to *any*
  requirement, product or condition-of-use alike. (Most conditions of use are not
  auto-verifiable, so in practice they are discharged by a `DesignReview` whose edge is
  affirmed — the review *is* the discharge, not an annotation on top of one.)
- **Mode 2 — reliance.** Active `relies-on` edge to an upstream `Requirement` (the
  guarantee `G_up`), additionally requiring: (i) the integrator **affirms the
  refinement** — the *single* human judgment here, "`G_up` covers the downstream need",
  which only they can make; (ii) **for every condition `C` such that `G_up assumes C`**
  (the upstream-authored `assumes` edges, which are *under the seal*): `C` is itself
  discharged (recursion into this rule); (iii) the downstream **implementation uses the
  upstream implementation** the seal is about; (iv) the upstream **manifest seal
  verifies** (recomputed Merkle + authenticity).
**Completeness is sealed, not affirmed.** The `assumes` edges from `G_up` to its
conditions live in the *upstream* graph, so the set of conditions is closed **by the
manifest**. The integrator does not enumerate conditions and so cannot under-capture
them; they *traverse* a sealed set. Want the cake, bring every ingredient on the sealed
list — miss one, no verdict. This removes the completeness affirmation entirely: mode 2
carries exactly **one** human act (the refinement affirmation), and condition coverage
becomes a graph-reachability fact, computed and seal-backed. The `assumes` edges are
sealed structure (like `refines`); they are not affirmed.
 
Caveat on what the seal guarantees: completeness means "all conditions the supplier
*declared*." If the safety manual itself omits a real condition, no downstream traversal
can detect it — that is a soundness gap in upstream's `C_up`, the *provider's* burden,
surfaced (if at all) by the **auditor** reviewing the upstream evidence graph. The seal
guarantees you honoured every declared assumption, not that the declared assumptions are
sufficient.
 
Product requirements are not special: a product requirement may be discharged by a
witness (mode 1) just as well as by reliance (mode 2). The slot is now implicit — it is
whatever a specific `relies-on` affirmation asserts `G_up` covers — rather than a
separately authored node.
 
**The manifest is the firewall.** A consumer never recurses below the seal. The sealed
manifest already accounts for everything inside upstream (its sub-dependencies, internal
refinement, test outcomes); downstream embeds only the *direct* slice it relies on and
trusts the seal beneath. The congruence law (§6) is the formal license that this
firewalling is sound. This is what keeps reliance tractable and the design/evidence
split intact: *design* = requirements (incl. referenced upstream nodes) + structural
edges; *evidence* = witnesses + the imported manifest; reliance is a new edge type, not
a graph merge.
 
**Well-foundedness.** Discharge must bottom out in witnesses; no requirement may
transitively discharge itself through a reliance/refines cycle. This is the same
stratification DEC-001 already demands of the verdict — reliance edges join the
dependency graph that must stay acyclic.
 
**Suspicion = staleness, one mechanism.** Drift sources — upstream re-seals; downstream
changes; the safety manual (`A_up`) is revised; a referenced node's content changes; a
reviewed artifact changes under a `DesignReview` — all re-suspect the relevant active
edge and propagate up the `refines` DAG like any internal drift. Cross-project reliance
reuses the suspicion machinery wholesale; it adds no new state.
 
**Partial discharge: the residual and the conditional verdict.** Discharge is binary
per requirement, but a *proof* over a set of relied-on requirements need not be
all-or-nothing. Define the **residual** as the relied-on requirements the product
depends on that no valid discharge reaches — derived (the complement of `discharged`
among the product's `relies-on` targets), never stored, so it recomputes under drift.
Empty residual ⇒ a **total** proof; non-empty residual ⇒ a **conditional** proof
`M ⊨ (A = residual, G = discharged)`. This is not a weakening: it is
`C_up = (A_up, G_up)` of §3 with the residual *as* the published `A_up` — a compliant
item shipped with a safety manual whose conditions of use are precisely the
undischarged requirements (§10). The next importer composes against that residual via
mode 2. The verdict layer therefore reports three states — **satisfied (total)** /
**conditional (residual published)** / **unsatisfied** — the conditional state being
the composability-level surfacing of partial-vs-total scope (DEC-002) and the
verdict-layer image of the quotient (§6).
 
This is orthogonal to mode-2 completeness above: "miss one, no verdict" still governs
*using* a single upstream reliance (every sealed `assumes` condition of the guarantee
you lean on must be discharged). The residual concerns the product's *own* relied-on
requirements, not the conditions internal to a reliance it invokes — a conditional
proof never relaxes a reliance's completeness.
 
*Demonstrated:* `seg_demo_clingo_partial_discharge.py` computes the residual and the
three verdicts on a single-level import (partial → complete → stale);
`seg_demo_clingo_transitive.py` chains reliance A→B→C, shows staleness propagating two
hops, and trips the determinism guardrail on a reliance cycle (the well-foundedness
condition above, made to fail).
 
## 9. Conservative-extension invariant
 
The composition layer must be a **conservative extension** of the base model: a project
that imports nothing must be unable to tell SEG-with-composition from SEG-without — same
well-formedness, same verdicts, no new obligations, no changed outcomes. Stated as a
checkable invariant with two halves.
 
**(i) Syntactic — strictly additive grammar.** Every base production is present
unchanged; the new constructs (`DesignReview`, referenced-upstream `Requirement`,
`assumes`, `relies-on`, `manifest`) are new optional productions reachable only through
themselves. No existing node type gains a now-required field. The base grammar is a
literal sub-grammar. Checkable by schema diff: assert the base schema's productions are
an unchanged subset.
 
**(ii) Semantic — guard-clause discipline.** Every added verdict clause is **guarded by
a new-type literal** in its body, so it is inert on any graph free of import constructs.
Sketched (Datalog-style; base clauses unchanged, added clauses marked NEW):
 
```
% --- base rule-set (unchanged) ---
discharged(R) :- requirement(R), witness(W), discharges(W,R), active(W,R).   % mode 1
satisfied(R)  :- discharged(R).
satisfied(R)  :- requirement(R), all C with refines(C,R): satisfied(C).      % refinement DAG
 
% --- added by composition (each guarded by a NEW-type literal) ---
witness(W)    :- design_review(W).                      % NEW: extends the witness genus
discharged(R) :- relies_on(R,Gup), active(R,Gup),        % NEW: mode 2, guarded by relies_on
                 manifest(M), seal_verifies(M), impl_uses(R,Gup),
                 all C with assumes(Gup,C): satisfied(C).
residual(R)   :- relies_on(R,_), not discharged(R).      % NEW: relied-on but undischarged → published A_up
```
 
On an import-free graph there are no `design_review`, `relies_on`, `manifest`, or
`assumes` facts, so every NEW clause has an unsatisfiable body and contributes nothing
(including `residual`, which is guarded by `relies_on`); the derivable
`discharged`/`satisfied` set is *identical* to the base rule-set's. That is
conservativity by construction, not by testing — and it composes with the DEC-001
stratification (the added `relies_on`/`assumes` literals merely join the dependency graph
that must stay acyclic; the one new negation, `residual` over `discharged`, is terminal —
nothing derives `discharged` from `residual` — so it adds a stratum, not a cycle).
 
**The three-state verdict (§8) on this sketch.** `satisfied/1` keeps its meaning —
*total* discharge. The added `residual/1` carries the published assumption set `A_up`. A
proof is then **total** iff its root is satisfied with empty residual; **conditional**
iff its only remaining gaps are residuals (relied-on requirements awaiting external
discharge, publishable as `A_up`); **unsatisfied** iff a gap is *not* a residual (e.g. a
failing or absent witness, or a reliance whose seal/affirmation fails). The exact
stratified rollup that separates conditional from unsatisfied at proof scope is the
runnable encoding in the two header demos; the sketch derives `residual` and leaves the
proof-scope rollup to them.
 
**Empirical backstop.** Run the existing import-free fixtures under the augmented
rule-set and assert byte-identical verdicts to the pre-extension baseline. The
guard-clause argument is the proof; the fixtures catch a mistake in the guards.
 
This is the precise statement of "ignore all of this if you don't import," and a clean
reviewer-facing property: *the composition layer is a conservative extension of the base
assurance model.*
 
## 10. IEC 61508 mapping (the safety-track story)
 
The contract structure is not a metaphor here; it is the standard's own machinery.
 
- `M_up ⊨ C_up` = the producer's **compliance**: the element delivers its safety
  claim under its conditions of use. SEG's sealed design+evidence graph *is* the
  certified evidence for this.
- `A_up` = the **Safety Manual for Compliant Items** (IEC 61508-2 Annex D; for
  software, IEC 61508-3 Annex D): the conditions of use / integration constraints /
  run-time-environment assumptions the producer documents.
- `A_up ⊇ A_slot` (refinement's assumption side) = the **integration obligations**:
  the integrator must keep the system inside the safety manual. An SEG import that
  omits this is, literally, an integration performed without honoring the safety
  manual.
- `G_up ⊆ G_slot` = the certified safety claim covers what the integrator's
  higher-level safety function requires.
Framing for OSS Summit Safety: SEG makes the safety manual *machine-checkable and
drift-tracked* — the conditions of use become a committed contract, and a change on
either side that violates them is flagged automatically rather than discovered in a
late audit.
 
## 11. Decided / open
 
**Decided (this model):**
- A cross-project import is contract refinement `C_up ⊑ C_slot`; reliance encodes it.
- Producer seals satisfaction (`M_up ⊨ C_up`); consumer checks refinement only, and
  the manifest seal is the firewall — consumers never recurse below it.
- **Refinement is human-affirmed, not computed** (§7 resolved): affirmation = the act of
  activating a discharge edge at the semantic level. Computed checks remain an optional
  accelerator for mechanizable property fragments.
- **One discharge rule, two modes, every requirement** (§8): mode 1 = a `Witness`
  (`TestOutcome` and/or `DesignReview`); mode 2 = reliance on an upstream requirement
  with its conditions-of-use discharged, impl-uses-impl, and seal verified.
- New node type `DesignReview` (a `Witness` alongside `TestOutcome`); upstream nodes are
  embedded **by reference**, not copied; conditions of use are ordinary `Requirement`s.
- **Completeness is sealed, not affirmed** (§8): conditions are reached via upstream's
  sealed `assumes` edges, so mode 2 carries exactly one human act (the refinement
  affirmation); coverage is a graph-reachability fact. The seal guarantees declared
  conditions are honoured, not that they are sufficient (provider's burden, auditor's
  review).
- **Conservative-extension invariant** (§9): the composition layer is strictly additive
  (grammar) and guard-clause-gated (verdict), so import-free graphs validate and get
  identical verdicts. Checked by schema diff + import-free regression fixtures.
- **Manifest is a node, hybrid form** (§8): a `Manifest` node owns shared recomputed
  facts (component identity, version, digest, `seal_ok`); the `relies-on` edge owns the
  reliance-specific facts + the refinement affirmation and references it. Version
  consistency — at most one manifest per upstream-component-identity — is a static
  validation rule encoding "one upstream implementation only".
- Discharge ⟺ affirmed-active edge ⇒ uniform staleness; well-foundedness via the
  existing DEC-001 stratification.
- **Partial discharge yields a *conditional* proof** (§8): a non-empty residual is
  published as the proof's `A_up` (its safety manual / conditions of use); the verdict
  layer reports satisfied (total) / conditional / unsatisfied. Orthogonal to mode-2
  completeness. Demonstrated by the two clingo demos in the header.
**Open (need ratification):**
- Saturated vs naive guarantees wherever a check *is* mechanized (§2 caveat).
- Surface naming of the new edges (`relies-on`, `assumes`) — `assumes` chosen here (the
  CBD word); confirm it reads for a safety audience vs "conditions of use".
- Confirm upstream exposes a stable **component identity** in the manifest (the join key
  the version-consistency rule groups by), distinct from version.
- Signed external projection / actor-authentication for trusting a *foreign* proof
  (`seg_adr_projection_core.md §8`, thread 5) — recompute-the-merkle vs require-a-
  signature; necessity of the signature depends on whether the proof digest is pinned
  out-of-band or discovered dynamically.
## 12. Glossary deltas (fold into `seg_glossary.md`)
 
`contract (A, G)`, `assumption`, `guarantee`, `satisfaction (M ⊨ C)`, `compatible
environment`, `refinement / dominance (C ⊑ C′)`, `saturated form`, `dependency's
required contract` (informal: *slot*), `conditions of use / safety manual`,
`cross-graph staleness`. New from §8: `discharge` (a node is discharged iff its edge is
affirmed active), `affirmation` (the human act of activating an edge at the semantic
level — *not* a content-bearing object), `witness` (genus; discharges a requirement by
observation/authorship), `TestOutcome` and `DesignReview` (the two witness species),
`condition-of-use requirement` (an ordinary `Requirement` imposed via an import),
`embed-by-reference` (referenced upstream node: IRI + content hash, attested by the
manifest), `manifest-as-firewall` (consumers verify the seal and never recurse below
it). Note the suspicion-cluster terms (`drift`, `suspect`, `suspicion propagation`) are
reused unchanged — composition adds no new state.
 
Also fold the verified IEC 61508 mapping (per the direct check): the **safety manual**
(IEC 61508-2/-3 Annex D) is the human-readable form of `C_up` — its safety-functions
section (incl. the SIL/SC and failure-rate claims) is `G_up`; its conditions-of-use /
limitations section (Annex D.2.1 c) is `A_up`, recorded downstream as
condition-of-use requirements. Industry precedent: vendors already render conditions of
use as integrator requirements (e.g. ST's "Application-level Safety Requirements").
Confirm Annex D's normative status against the standard text before asserting it.
 
## 13. References (hardened)
 
- Benveniste, A., Caillaud, B., Nickovic, D., Passerone, R., Raclet, J.-B.,
  Reinkemeier, P., Sangiovanni-Vincentelli, A., Damm, W., Henzinger, T. A.,
  Larsen, K. G. "Contracts for System Design." *Foundations and Trends in
  Electronic Design Automation* 12(2–3):124–400, 2018. DOI 10.1561/1000000053.
  (Earlier: INRIA Research Report RR-8147, 2012.) — the contract algebra adopted here.
  **Verified against the primary text** (§6 loci: eq (5.6), Definition 5.4, eq (5.7),
  §4.5 / Property 7, Summary of Results 1).
- Misra, J., Chandy, K. M. "Proofs of Networks of Processes." *IEEE Transactions on
  Software Engineering* SE-7(4):417–426, 1981. — assume-guarantee origin (commonly
  cited "Chandy & Misra"; actual author order Misra, Chandy).
- Jones, C. B. "Tentative Steps Toward a Development Method for Interfering
  Programs." *ACM TOPLAS* 5(4):596–619, 1983. DOI 10.1145/69575.69577. —
  rely-guarantee origin.
- IEC 61508-2, Annex D, and IEC 61508-3, Annex D: "Safety Manual for Compliant
  Items." — the conditions-of-use artifact `A_up` maps to.
- arXiv:2402.12804, "Modular Assurance of Complex Systems Using Contract-Based
  Design Principles." — CBD-to-assurance seam. **UNVERIFIED:** confirm authors/venue
  before the paper leans on it.