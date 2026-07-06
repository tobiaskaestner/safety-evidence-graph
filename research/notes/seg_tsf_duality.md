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
