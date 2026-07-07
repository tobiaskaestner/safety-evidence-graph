# SEG ↔ TSF — The Duality and the Two Lineages

**What this is.** The conceptual synthesis from the TSF revisit (session 2026-07-06),
captured verbatim from the discussion that produced it. Status: **hypothesis, pre-spike**
— the mechanical-overlap half is docs-read only (WP-7 Q1–Q7 test it); the embedding
asymmetry is analysis (WP-7 Q8). Companion documents: `seg_tool_landscape.md` WP-7
(registration + probe seeds), `seg_tool_comparison.md` (the tool spectra this does
*not* fit into), `seg_paper_seed.md` §1a (the ratified identity this extends).

**The claim being elaborated:** *TSF is an argument graph with artifacts at the
fringe; SEG is an artifact graph with the argument at the fringe (encoded in edge
types + verdict rules). They are near-duals of each other.*

---

## 1. The two ontologies, stated precisely

**In TSF, the reified objects are propositions.** A node is a Statement — a truth-apt
sentence. The graph's edges are inferential support ("A logically implies B"; child
necessary-but-insufficient for parent). So the *interior* of a TSF graph is pure
language: expectations at the roots, hand-authored inference steps (Assertions) in
the middle. The world — code, tests, results, documents — is not in the graph at all.
It touches the graph only at the leaves, through hashed References from Premises to
artifacts. The boundary between graph and world is the premise-to-artifact reference;
that is the fringe.

**In SEG, the reified objects are artifacts.** A node is a content-anchored thing — a
requirement's byte span, an implementation span, a test spec, a test outcome. Node
identity *is* content (the hash). The edges are typed relations between artifacts:
`covers`, `refines`, `verifies`. So the interior of a SEG graph is pure world-model.
Where is the argument? It exists, but nowhere as nodes. It is split across three
intensional places: each **edge type** is an atomic claim *schema* (an edge instance
asserts one proposition — "this test verifies that requirement" — without ever
writing the sentence down); each **affirmation** is a human judgement of that
proposition, bound to the exact content state it was judged against; and the
**verdict rules** are the inference steps — universally quantified, applied by the
engine, never materialized.

The duality in one line: **TSF stores the argument as data and points at the world;
SEG stores the world as data and expresses the argument as a program.** Equivalently:
TSF's propositions are extensional and its artifacts intensional (behind pointers);
SEG's artifacts are extensional and its propositions intensional (behind schemas and
rules).

## 2. Why "dual" is doing real work

The correspondence is tighter than a metaphor — each structural role has a
counterpart:

| TSF | SEG |
|---|---|
| Premise + hashed Reference (the fringe) | *every node* — content binding is universal, not leaf-only |
| Assertion (hand-authored intermediate step) | derived predicate in the verdict program — exists only during solving |
| Link, human-reviewed ("humans decide whether Links are valid") | verdict rule — mechanical, with a determinism guardrail |
| leaf score assigned by SME | edge affirmation by the FSM |
| Trustability Score (arithmetic over the stored tree) | verdict (LFP of the ruleset over the committed facts) |

Two consequences fall out of this table — both previously listed as independent
findings in the WP-7 registration:

**First, record-vs-recompute is not a design choice layered on top — it is forced by
the ontology.** If the argument is *data* (TSF), it is an artifact like any other,
and of course it ships: the resolved graph carries pre-computed scores because the
proof tree is a document, and documents travel. If the argument is a *computation*
(SEG), it cannot ship — only its inputs can — so the consumer necessarily re-runs it.
The sharpest contrast found at the composition layer (TSF's traveling scores vs.
SEG's verdict-never-travels, DEC-017 / GAPS G5) is the duality projected onto
exchange.

**Second, the placement of human judgement flips.** TSF puts humans *inside* the
argument: they author the inference steps, review the links, and score the leaves —
which is why aggregation must be a heuristic (calibrated confidence,
mean-propagation) and why the declared link semantics (implication) and the score
semantics (arithmetic mean) can drift apart with nobody forced to notice. SEG
confines humans to the *ground layer* — affirming atomic, content-bound claims — and
makes everything above that layer reproducible machine inference. That is precisely
what lets a SEG verdict be a proof (a pure function of committed content) while a
TSF score is an assessment. Same human, dual position.

## 3. Why only "near"

Three honest qualifiers.

1. **The duality is not an involution: embedding is asymmetric.** TSF's statements
   are markdown files — content, hashable, DEC-003-compatible — so SEG can reify them
   as nodes and host the whole framework (WP-7 Q8, the instance-of-meta-model
   hypothesis). The reverse fails structurally: TSF has no typed artifact nodes and
   no programmable inference to host SEG in.
2. **The fringe treatments differ in strength, not just position.** TSF hashes at the
   fringe only; SEG's content binding is uniform — even the argument's own ruleset is
   committed content, so "argument drift" and "artifact drift" are the same mechanism
   in SEG.
3. **Each pole can say something the other cannot — and the duality predicts which.**
   TSF natively expresses soft, judgement-laden claims ("the design is adequately
   documented" as a scored statement) that have no natural home as a typed edge
   between artifacts; SEG natively expresses content-exact, recomputable claims that
   TSF can only approximate with an SME's number.

## 4. The two lineages — and why the mechanics converged

TSF's pole is the classical assurance-case lineage — Toulmin, GSN/CAE/SACM,
claims-argument-evidence — already in the borrowed-substrate list (paper seed §5).
TSF is, essentially, *a hash-disciplined, scored GSN*. SEG's pole is the traceability
lineage — Gotel & Finkelstein, and the five tools spiked in WP-1…WP-5 — upgraded with
logic and commitment. So the two frameworks are the two historical lineages each
reaching toward what the other has: the argument tradition acquiring content
discipline (dotstop's hashes, suspect-until-review), the artifact tradition acquiring
argument semantics (SEG's verdict layer).

**That is why dotstop's mechanics look so uncannily like SEG's while everything above
them differs: the poles converge at the mechanics — hashing, suspicion, review —
because that is the shared boundary layer both lineages need. The divergence is in
what each pole reifies above it.** It also retro-explains RTEMS (WP-6): a pure
artifact-lineage project reinvented the same mechanics and, having no argument pole
at all, stopped there.

**Elaborated (2026-07-06):** the full history of both lineages — waypoints,
each lineage's self-documented pathologies, the Toulmin-role table realized at both
poles (rebuttal row = the mechanics convergence; warrant row = the divergence), and
the honesty flag on argument-generation kin (Rushby ETB, Denney & Pai AdvoCATE, the
closest prior art to Q8's TSF-report-as-projection) — now lives in
`seg_prior_art.md`, "The two lineages" section. That section owns the history; this
note owns the structural argument.

## 5. Downstream use

If this framing survives the spike (WP-7 Q1–Q7 test the mechanical overlap; Q8 tests
the embedding asymmetry), it is a candidate organizing idea for **Paper 2's
related-work section**: the design space is not just facets on the tool side — it has
two poles, and SEG's claim is to sit at the artifact pole with a *sound* bridge to
the argument pole, while TSF sits at the argument pole with a *mechanical* bridge
back. For **Paper 1** it supplies one sentence: the field's argument pole and
artifact pole have independently converged on SEG's mechanics while each lacking the
other's semantics.

Not yet folded anywhere: pending the WP-7 spike, this document is the only home of
the duality/lineage claim; do not cite it from the papers until the probe results are
in.

---

## 6. Addendum (same session) — formalization attempt: not a duality, a universal object

Prompted by the question whether the "duality" admits a categorical formulation
(co-/contravariant functor). Outcome: **the duality label should stay in scare
quotes** — the formal home is provenance semirings, not category theory — and the
formalization *strengthens* the practical story. Status: analysis, carries the same
pre-spike caveat as the rest of this document.

### 6.1 Why it is not a contravariant duality

Candidate categories: **Seg** with objects `(D, P)` — finite structure (artifact
graph) + stratified program (verdict ruleset) — and **Arg** with objects finite
labeled statement-DAGs (TSF graphs). There is a natural **covariant** functor
`G : Seg → Arg`: unfold `(D, P)` into its derivation DAG (derived atoms ↦ statements,
rule applications ↦ links, EDB facts ↦ premises, goals ↦ expectations); instance
homomorphisms transport derivations (naturality of the immediate-consequence
operator). The §3 embedding asymmetry becomes precise here: `G`'s essential image is
only the *uniform* DAGs — unfoldings of finitely many rule schemas — while a
hand-authored TSF graph is an arbitrary finite argument. Recovering a generator from
an arbitrary argument is theory induction, which is not functorial; so `G` has no
adjoint on all of **Arg**. Embedding-like functor with a characterizable image: yes.
Duality: no.

Genuine contravariance exists but is *internal to SEG*: the rules-vs-instances
Galois connection (strengthen the ruleset ⇒ fewer passing graphs; enlarge the graph
class ⇒ fewer common valid rules) — the classical Th/Mod polarity. SEG's definition
language is a theory presentation; artifact graphs are its models. Paper-2 formal
positioning material, but not the TSF↔SEG relation.

### 6.2 The provenance triangle (the correct picture)

In the provenance-semiring framework (Green, Karvounarakis & Tannen, PODS 2007 —
**positive** Datalog; see §6.5), the provenance of a derived atom is a polynomial in
`ℕ[X]`, one indeterminate per ground fact, and:

1. **the polynomial's expression DAG is exactly a TSF-shaped argument graph**
   (derived atoms = statements, monomials = alternative supporting arguments,
   factors = premises);
2. **the polynomial is universal**: every concrete semantics is a semiring
   homomorphism out of it. Boolean evaluation = derivability (SEG's verdict shape);
   evaluation in `(ℝ, +, ×)` with edge weights = weighted path sums — and TSF's
   mean-propagation is precisely this with edge weight `1/outdegree` (graphalyzer's
   `s(v) = c(v)(r(v) + Σ w·s(u))` unfolds on a DAG to a weighted sum over
   root-to-leaf paths).

So: not two poles with a functor between them, but a **triangle with a universal
object at the apex** — `(D, P)` *generates* the provenance polynomial; verdict and
score are two *evaluations* of it in different semirings. SEG keeps the generator
and evaluates without materializing the polynomial; TSF hand-authors (an
approximation of) the polynomial's expression DAG and evaluates it numerically,
without ever possessing a generator. §1–§2's duality talk was the two projections of
this triangle.

### 6.3 Three §2 observations upgraded to lemmas-or-better

- **Record-vs-recompute, derived not asserted:** a polynomial is data and can ship —
  but shipping forfeits the warrant that it *is* the polynomial of `(D, P)`; only
  regeneration from the committed generator restores it. DEC-017's
  "verdict-never-travels" falls out of the algebra.
- **The TSF semantics mismatch, made precise:** TSF declares links as implication
  (Boolean semiring) but scores in the real weighted semiring; the only homomorphism
  connecting the two is the **support map** (score > 0 ⟺ Boolean-derivable, positive
  weights). The score *refines* derivability; its magnitude carries no
  implication-compatible meaning — "a change of semiring with no mediating
  homomorphism beyond support."
- **The verdict is the shadow of the score:** the same support homomorphism read
  constructively — any TSF-style score assignment collapses to a SEG-style verdict,
  never conversely. §1's layering, exact.

### 6.4 The dividend (what is cheap on which side)

- **Cheap on the unfolded/TSF side:** sensitivity and prioritization ("which leaf
  most improves the root" = polynomial derivative on the expression DAG);
  explanation (why-provenance). This is the one thing TSF's methodology is genuinely
  good at ("identify where effort should focus next").
- **Cheap on the generator/SEG side:** universality (one ruleset, every instance),
  re-verification (recompute the LFP), drift as a fact-level event, compression
  (program ≪ its unfolding).
- **Engineering consequence:** the argument view is a **derived, write-only
  projection** — exactly the shape the projection-core ADR licenses. SEG can *emit*
  a TSF-shaped argument graph (derivation DAG + chosen semiring evaluation) as
  another projection target beside SHACL and SPDX. This upgrades WP-7 Q8 from "can
  SEG host TSF's model" to "**can SEG generate a TSF trustable report from a verdict
  run**" — integration-by-projection, the ratified role-2 identity
  (`seg_paper_seed.md` §1a).

### 6.5 Obstructions (record as Paper-2 open questions, do not gloss)

1. The `ℕ[X]` universality theorem is for **positive** Datalog; SEG's rulesets are
   **stratified with negation** — provenance under negation needs extended
   structures (semirings with monus, dual-indeterminate polynomials), an unfinished
   corner of the literature.
2. SEG's three-state rollup (total/conditional/unsatisfied) needs a value structure
   beyond Boolean — plausibly a three-element semiring-like structure; unproven.
3. *(added 2026-07-07, from §6.8)* **Aggregation outgrows plain `ℕ[X]`**: TSF's
   mean uses counting and division, and aggregation provenance needs the
   semimodule extension (Amsterdamer–Deutch–Tannen, PODS 2011). Mild: on a DAG
   with per-edge weights it degenerates to the weighted linear polynomial, so
   nothing claimed here breaks — but a formal citation of the triangle's score
   edge needs ADT 2011 alongside GKT 2007.

If either fails, the triangle survives informally but loses theorem status. The
methodological residue of the physics analogies survives in exactly one form:
**generate and verify on the program side; unfold and explain on the argument
side.**

### 6.6 Spike results (2026-07-07, WP-7 T1–T8 — the hypothesis status upgrades)

- **The score-calculus edge of the triangle is demonstrated**: TSF's entire
  verdict layer (mean propagation + suspect-gate + unscored-is-zero) reproduced
  as ~10 stratified clingo rules with exact numeric parity
  (`research/spikes/tsf/t8_clingo_score.lp`; 73333/53333 vs trudag's
  0.73333/0.53333 on the same fixture states). The suspect-gate rule composes the
  two channels exactly as §6.3's support-homomorphism reading predicted.
- **The mechanics convergence (§4) is now probe-verified**, with the divergence
  sharper than predicted: TSF's affirmation is an *anonymous* content stamp
  (T3), its trust number sits *outside* the affirmation boundary (T5 — the
  score is never affirmed), and its record-side commitment travels *unverified*
  (T6/T7: a real recomputable root that nothing checks). Each is the §2 table's
  corresponding row, radicalized.
- **The §6.4 dividend ships as product**: `export --sensitivity` — sensitivity
  analysis on the unfolded side, exactly the "cheap on the expression DAG"
  prediction.
- **Bonus for §15-of-the-design-summary**: TSF independently implements the old
  hypothesis (integrity gates trust scoring) — an unreviewed statement
  contributes zero. Routed to the FSM (cross-worktree).
- Still open: the §6.5 obstructions (the T8 program is stratified with only
  default negation on `reviewed` — the negation obstruction is untouched); and
  the embedding asymmetry was only exercised in the direction that works (the
  fixture is uniform by construction — no hand-authored non-uniform TSF graph
  was probed to watch the reverse direction fail).

### 6.8 The polynomial, constructed and justified (2026-07-07)

What §6.2 asserts abstractly, built from the ground up — and why "polynomial" is
forced, not chosen. (Pedagogically the best route into the triangle; candidate
opening for Paper 2's formal section.)

**The construction.** Tag every ground base fact with its own indeterminate
(`affirmed(e12) ↦ x₁`, `outcome(t7, passed) ↦ x₂`, …); derived atoms earn their
annotations by two rules: *within one rule instance, multiply* (joint use);
*across alternative derivations, add*. A derived atom's annotation is then an
element of `ℕ[X]`, and every syntactic feature means something:

- each **monomial** = one derivation: the multiset of base facts one proof
  jointly consumes;
- an **exponent** = the same fact used twice within one proof;
- a **coefficient** k = k structurally distinct proofs over the same leaf
  multiset;
- the polynomial = **the proof forest, summed**: Σ over proof trees of Π over
  leaves; its expression DAG (with sharing) is the argument structure of §6.2.

For a physicist: a partition-function-like generating object — formal sum over
configurations (proofs) of products of local weights (leaf indeterminates);
every concrete semantics is an observable, i.e. an evaluation.

**Worked on the T8 fixture (score reading).** Mean-propagation is a weighted
sum with edge weights 1/outdegree, so the root polynomial is degree one:

> T(EXP-SCHED) = ⅔·x_impl + ⅓·x_test

(⅔ because PREM-IMPL reaches the root along two paths). Evaluating at
x_impl = 0.8, x_test = 0.6 gives 0.7333 — trudag's exact output. The
double-counting observed empirically in T5a is now a **coefficient**: a static
syntactic property, readable before any evaluation.

**Why a polynomial — freeness.** `ℕ[X]` is the *free commutative semiring* on
X. Universal property (GKT 2007): for any commutative semiring K and valuation
ν : X → K there is a **unique** homomorphism `ℕ[X] → K` extending ν, commuting
with query semantics. Compute the polynomial once; every semantics is a
specialization: Booleans → derivability (verdict shape); weighted reals → TSF's
score; ℕ → proof counting; Viterbi → best-case confidence; tropical → cheapest
evidence path; support → why-provenance ("which affirmed facts does this rest
on"). Initial-object statement: all semantics factor through `ℕ[X]` uniquely.

**Why exactly the semiring laws — squeezed from both sides:**
- *From above (soundness):* the raw proof forest (free term algebra) is too
  fine — it distinguishes what the positive fragment provably cannot (body
  order, interleavings). Quotient by exactly the query-equivalence laws
  (associativity, commutativity, distributivity, units) and `ℕ[X]` is what
  remains: **the proof forest in its coarsest semantically sound normal form**.
- *From below (completeness):* any further law loses a target. Idempotence
  (x + x = x) kills counting and probability — two proofs ARE more than one.
  Additive inverses would mean evidence can *cancel* — false in the positive
  fragment (and exactly what negation breaks; §6.5.1 is real, not
  bookkeeping). Semiring, no inverses, no idempotence: precisely the laws
  every target shares, not one more. Forced, the way a free group is forced.

**Two precision gains for SEG/TSF:**
1. **Structure/judgement separation.** The polynomial is fixed by graph
   topology + ruleset; the *valuation* carries the judgement. The T5b suspect
   gate is purely a valuation event (ν(x_test): 0.6 ↦ 0; same polynomial;
   0.5333) — so §6.7's factorization is exact **at the leaves**
   (ν(xᵢ) = Bᵢ·Rᵢ), then propagated linearly; the node-level phrasing is the
   loose version. SEG's machinery respects the split exactly: the commitment
   (edgeHash, sealed root) pins the *polynomial*; affirmation/evidence state
   feeds the *valuation*. Two orthogonal change axes.
2. **TSF's calculus is the degree-1 fragment.** Mean-propagation never
   multiplies two facts — every monomial is linear; the calculus is linear
   algebra (weighted path sums; (I−W)⁻¹). Hence trudag's cheap
   `--sensitivity`: for a linear polynomial ∂T/∂xᵢ is a *constant* (the
   path-weight sum — ⅔ for x_impl above), independent of all other leaves.
   SEG verdict rules are genuinely polynomial: a `covers` discharge requiring
   an affirmed edge AND a passing outcome AND a fresh source hash is a
   degree-3 monomial; alternative discharge routes add monomials — so
   sensitivities have interaction terms, and why-provenance (monomial
   support) is non-trivially informative: the list an assessor wants.

**Caveat routed to §6.5.3:** the mean's counting/division is an *aggregate*;
aggregation provenance needs the semimodule extension (ADT 2011). Degenerates
gracefully here; cite it alongside GKT 2007 whenever the score edge is
formalized.

**Runnable companion (2026-07-08):**
`research/prototypes/demos/seg_demo_provenance_polynomial.py` — this section's
construction executed and self-checked on a minimal SEG verdict (two discharge
legs + roll-up + the redundancy rule audit): the polynomial built symbolically
over ℕ[X], then evaluated as Boolean verdict, proof count, Viterbi confidence,
and drift-gated valuation. All §6.8 claims assert-guarded.
- ~~The Rushby/AdvoCATE kin check~~ **resolved 2026-07-07, sharpened by the
  ETB-2024 read** (all four primaries read; outcome in `seg_prior_art.md`,
  two-lineages honesty flag): generation-as-such is occupied (Basir/Denney/
  Fischer 2009, AdvoCATE, ETB), and ETB-2024 additionally occupies *mechanical*
  liveness-under-change (hash-identified evidence + change-impact incremental
  re-derivation — rtemsspec's move on the argument side). The surviving claim
  is the **assurance-state half**: the projection knows what a human vouched
  for and what that vouching no longer covers, and carries a recomputable seal.
  Two bonuses for this note: Rushby's `good_doc` is an identified
  affirmation-as-axiom gating derivation — the B factor of §6.7 with an
  independent 2010 pedigree, minus content binding; and **ETB's Datalog is the
  positive fragment (2014 and 2024 alike)**, so the suspect-gate
  (`not reviewed(X)`) is outside its language — the §6.7 factorization needs
  exactly the stratified step the kin does not have.

### 6.7 The factorization observation (2026-07-07, from T5 — beyond what was predicted)

§6.3 predicted a one-way collapse: the support homomorphism makes the verdict
the *shadow* of the score. T5 found something stronger about TSF's actual
evaluation: the suspect-gate means it is **not** a pure real-semiring path sum —
it computes, in effect,

> **T(s) = B(s) · R(s)**

the product of a **Boolean integrity factor** B (is the statement review-clean?
unreviewed ⇒ 0) with the **weighted-real mean recurrence** R. The two channels
(§6.6 "radicalized" bullet) are composed by *multiplication*, with the Boolean
factor exactly where the design summary's §15 hypothesis put it: "a clean
integrity state is necessary but not sufficient for a high trust score" **is**
this factorization — B can zero the product; B alone never raises it. What was
a 2026-era hypothesis about how SEG's layers should relate turns out to be a
structural fact about how a scored-argument system composes its integrity
channel with its confidence channel; in triangle terms, TSF's evaluation
semiring is the *product* of the Boolean one with the weighted-real one, and
the support homomorphism of §6.3 is recovered as projection onto the first
factor. (Verified concretely: the T8 ruleset realizes B as one gate rule;
dropping `reviewed(prem_test)` reproduces trudag's 0.53333 exactly.)

Two consequences worth carrying forward:
- **For the §15 update (FSM's edit):** the better statement is not "hypothesis
  confirmed" but "hypothesis is a factorization law, independently implemented
  by TSF" — with the one-directionality sharpening (B gates R; R is invisible
  to B, and in TSF the R-inputs are not even content-bound, §6.6).
- **For SEG (Paper 2 candidate question):** SEG's own verdict is pure B — the
  three-state rollup lives entirely in the integrity/logic factor. If a SEG
  definition ever wants a quantitative confidence layer (the §6.5 value-
  structure question), the factorized form says where it goes: a second factor
  *under* the same gate, never a replacement for it — and the R-inputs must be
  committed content, fixing TSF's unbound-score defect by construction.

Citation stub to harden before use: Green, Karvounarakis, Tannen, "Provenance
Semirings", PODS 2007 (verify pages/DOI; survey follow-ups for the negation/monus
line before citing them).
