# SEG — Prior-Art Reconciliation & Early Bibliography
 
**Purpose.** For each layer of SEG, name the canonical formalism, map SEG's
vocabulary onto it, and record what SEG deliberately does *differently* and why.
This converts "are we reinventing this?" into a documented design stance, and
seeds the bibliography for a paper. References are grouped by layer; a
consolidated BibTeX-ready list is at the end.
 
**One-line thesis for the paper.** SEG is a *cryptographically-committed,
drift-tracking assurance case with assume-guarantee composition*. No single prior
field covers the whole stack; the contribution is the integration, and the novel
seams are (i) binding a recursive-fixpoint validity predicate to a content-hash
commitment, and (ii) composing sealed proofs by assumption-scope containment.
 
---
 
## Layer 1 — Type graph / well-formedness
 
**Canonical formalism.** Typed (attributed) graphs in the algebraic
graph-transformation tradition. A *type graph* TG defines the set of valid
instance graphs as those admitting a typing morphism into TG; attributes make it
*attributed*; extra constraints (e.g. multiplicity/cardinality) sit alongside
typing.
 
**SEG mapping.** `graph-type definition` = type graph; the 5/7 built-in model =
the TG; `domain`/`range` = edge typing; the generic checker = typing-morphism
validation; `node type` attributes = attributed nodes; `constraint slot` = the
"extra constraints beyond typing" slot (cardinality bounds are a catalogued member
there).
 
**Deliberate divergence.** SEG does not use graph *rewriting* (productions/LHS→RHS)
at all — the graph is built by extraction, not derived by a grammar. SEG takes the
type-graph + constraints half and discards the transformation half. The
meta-model (DEC-007) is a TG generator, not a graph grammar.
 
**Leading references.** Ehrig, Ehrig, Prange, Taentzer, *Fundamentals of Algebraic
Graph Transformation* (2006); Rozenberg (ed.), *Handbook of Graph Grammars and
Computing by Graph Transformation*, Vol. 1 (1997); Ehrig & Taentzer on typed
attributed graphs.
 
## Layer 2 — Schema / shapes (the declarative half of the meta-model)
 
**Canonical formalism.** SHACL and ShEx — declarative shape languages for typed
graphs, where a *shape* constrains a node by properties of it and its neighbours.
Shapes were shown to be, in essence, a description logic ("SHACL: a description
logic in disguise"), which fixes their expressiveness and decidable fragments.
 
**SEG mapping.** A `graph-type definition`'s structural constraints = a shape
schema; "edge of type T must have domain/range X/Y" = a property shape;
node-level required-incident-edge constraints = SHACL `sh:property` /
`sh:minCount`. SEG's "vocabulary vs satisfaction" boundary ≈ SHACL's
"shapes (structure) vs targets+recursion (validity)".
 
**Deliberate divergence.** SHACL ranges over RDF triples and global IRIs; SEG
ranges over content-hashed nodes whose identity is a byte-span hash, not an IRI
(until the namespace work for composability). And SEG's shapes must be
*proof-bound* (hashed into the TCB) — SHACL schemas are not themselves
integrity-committed. Open question this resolves: the "what format is the
definition" debate has a known answer space here (SHACL profile vs custom DSL),
with a known expressiveness ceiling.
 
**Leading references.** Knublauch & Kontokostas, *SHACL* (W3C Recommendation,
2017); Prud'hommeaux, Labra Gayo, Solbrig, *ShEx* (2014); Bogaerts, Jakubowski,
Van den Bussche, "SHACL: A Description Logic in Disguise" (LPNMR 2022); their
"Expressiveness of SHACL Features" (ICDT 2022).
 
## Layer 3 — Recursive satisfaction / verdict (DEC-007 Datalog pin)
 
**Canonical formalism.** Recursive SHACL semantics + stratified Datalog. The
problem SEG hit — "what does a recursive validity predicate mean over a cyclic
reference graph?" — is exactly the recursive-SHACL problem. The literature gives
supported-model, stable-model, well-founded, and least-fixpoint semantics, with a
sharp result: **for stratified constraints, least-fixpoint = well-founded =
stable-model all coincide, and validation is tractable**, whereas with arbitrary
recursion validation is NP-hard even under stratified negation.
 
**SEG mapping.** `satisfaction` predicate = a SHACL shape's validity; `satisfaction
ruleset` = the recursive shape schema; `verdict` = the shape's per-node
true/violated assignment ("valid typing"); `suspicion propagation` = a second
recursive predicate (transitive closure) over the same graph; the "silently-wrong
*unsatisfied*" failure mode on a cycle = the known divergence between fixpoint
choices on non-stratified schemas.
 
**Deliberate divergence (and vindication).** DEC-007 pins satisfaction to
*stratified* Datalog. The literature shows this is precisely the fragment where
the hard semantic ambiguities vanish and the competing semantics agree — so the
pin is not a simplification but a selection of the tractable, well-defined island.
This is a citable justification, not a hand-wave.
 
**Why not OWL 2 RL specifically (the two walls).** A natural objection is to skip a
dedicated verdict engine and encode satisfaction as OWL 2 RL rules over the same
graph. SEG's stance: the two predicates it actually needs are inexpressible in
OWL 2 RL on *two independent grounds*, so the objection fails twice over.
**Wall 1 — closed-world negation.** The `unsatisfied`/`residual` predicate asserts
that *no* discharging evidence exists; under OWL's open-world assumption absence
cannot be concluded, and OWL 2 RL offers no negation-as-failure. **Wall 2 —
multi-variable joins with co-reference.** The universal-over-children satisfaction
check ("every child is covered by a guarantee that refines the *same* parent") is a
conjunctive join over several variables sharing a co-reference; OWL 2 RL's
forward-chaining rule fragment cannot state it. Stratified Datalog supplies both:
negation-as-failure across a stratum boundary (Wall 1) and unrestricted conjunctive
joins in a rule body (Wall 2). This argues against the OWL-RL alternative
*specifically*, not for any particular engine over another.
 
**Leading references.** Corman, Reutter, Savković, "Semantics and Validation of
Recursive SHACL" (ISWC 2018); Andreşel, Corman, Ortiz, Reutter, Savković, Šimkus,
"Stable Model Semantics for Recursive SHACL" (WWW 2020); Bogaerts & Jakubowski,
"Fixpoint Semantics for Recursive SHACL" (ICLP TC, EPTCS 2021); Abiteboul, Hull,
Vianu, *Foundations of Databases* (1995) (stratified Datalog); Van Gelder, Ross,
Schlipf, "The Well-Founded Semantics for General Logic Programs" (JACM 1991);
Gelfond & Lifschitz, "The Stable Model Semantics for Logic Programming" (1988)
(ASP foundation — clingo's semantics); Gebser, Kaufmann, Kaminski, Ostrowski,
Schaub, Schneider, "Potassco: The Potsdam Answer Set Solving Collection"
(AI Communications 2011) (clingo); Motik, Cuenca Grau, Horrocks, Wu, Fokoue, Lutz,
"OWL 2 Web Ontology Language Profiles" (W3C Recommendation, 2012) (the OWL 2 RL
fragment the "two walls" argument rules out).
 
## Layer 4 — Cryptographic commitment (nodeHash / edgeHash / merkleHash)
 
**Canonical formalism.** Authenticated data structures and commitment schemes.
Two distinct primitives map onto SEG's two fingerprint modes: a **Merkle tree /
Merkle-DAG** is a *position/structure-binding* commitment (order and topology
matter) — this is `deep`; a **cryptographic accumulator** is a *set* commitment
(order-blind) — this is `flat`. A Merkle tree is itself a vector commitment with
logarithmic openings; accumulators give constant-size membership proofs.
 
**SEG mapping.** `nodeHash` = content commitment over raw bytes; `edgeHash` =
a local 2-element commitment (one-hop); `merkleHash`/`design root` (deep) =
Merkle-DAG over the `deep-fingerprint subgraph`; a `flat` sub-root = a set
accumulator over its edges; "design root combines deep + flat sub-roots under a
canonical composition" = a commitment to a tuple of commitments. The generic
"make a structure emit integrity proofs" pattern is *authenticated data
structures, generically*.
 
**Deliberate divergence.** SEG hashes *raw source byte spans located by a parser*
(parser-as-locator), not a normalized/canonical data model — a discipline specific
to binding evidence to real source artifacts. And SEG separates the *local*
commitment (edgeHash, drift detection) from the *global* one (merkleHash,
fingerprint) and assigns them different jobs — most ADS work uses a single
authenticating structure. This is the seam where the field's mental model
(Merkle-DAG everywhere) actively misled us once; naming both primitives prevents
recurrence.
 
**Leading references.** Merkle, "A Digital Signature Based on a Conventional
Encryption Function" (CRYPTO 1987) (Merkle trees); Benaloh & de Mare, "One-Way
Accumulators" (EUROCRYPT 1993); Camenisch & Lysyanskaya, "Dynamic Accumulators"
(CRYPTO 2002); Catalano & Fiore, "Vector Commitments and Their Applications"
(PKC 2013); Miller, Hicks, Katz, Shi, "Authenticated Data Structures, Generically"
(POPL 2014); Merkle-DAG in practice: Benet, "IPFS — Content Addressed, Versioned,
P2P File System" (2014).
 
## Layer 5 — Assurance case / structured argumentation (the domain)
 
**Canonical formalism.** Assurance/safety cases: a top claim decomposed via
argument strategies into sub-claims, ultimately discharged by evidence.
Standardized as GSN (Goal Structuring Notation), CAE (Claims-Arguments-Evidence),
and the OMG SACM metamodel; the intellectual root is Toulmin's model of argument.
 
**SEG mapping.** Requirement = Goal/Claim; refines = decomposition Strategy;
TestSpecification/Implementation/TestOutcome = Solution/Evidence; Waiver + excuses
= Assumption / managed "weakener"; `satisfaction` = argument discharge;
`design graph` = the goal structure; `proof` scope = the case's top-claim
boundary. SEG is, structurally, a SACM assurance case.
 
**Deliberate divergence (the wedge).** The assurance-case field has the *argument
structure* but generally treats evidence as references and the case as a document;
it has no content-hash integrity layer, no automatic *drift/suspect* detection
when evidence changes, and no cryptographic proof of case integrity. SEG adds
exactly those. Framing: SEG = a *machine-checkable, cryptographically-committed
assurance case*. This is likely the paper's primary positioning, since the
audience (IEC 61508 / safety certification) lives here.
 
**Leading references.** Toulmin, *The Uses of Argument* (1958); Kelly,
*Arguing Safety — A Systematic Approach to Managing Safety Cases* (PhD, Univ. of
York, 1998); GSN Community Standard (Assurance Case Working Group, v3 2021/2023);
Bishop & Bloomfield, "A Methodology for Safety Case Development" (CAE, 1998);
OMG, *Structured Assurance Case Metamodel (SACM)* v2.x (2021).

**Lineage reading (2026-07-06).** This layer is one of *two* historical lineages
that converge on SEG's problem — see "The two lineages" section below, which
elaborates the history, places Eclipse TSF in this layer (a scored,
hash-disciplined GSN), and reconciles this layer's "SEG is structurally a SACM
assurance case" with the duality note's "SEG does not reify the argument": SEG
*generates* the case (a derived projection), it does not store one
(`seg_tsf_duality.md` §6).
 
## Seam — Composition / assume-guarantee (DEC-010)
 
**Canonical formalism.** Assume-guarantee / contract-based design. A contract is a
pair (A, G); a component implements (A, G) iff, in any environment satisfying A, it
delivers G. Composition/refinement of contracts is a mature algebra; the soundness
condition for replacing a subsystem by a contract is refinement (composite
guarantees preserved under the subcontracts).
 
**SEG mapping.** Imported-requirement boundary = the assumptions A; the referenced
foreign proof = the guarantee G with its discharging evidence; "valid iff product
assumptions ⊆ proven scope" = contract refinement (the composition refines the
top-level requirement); `dependsOn` edge = the contract link; transitive
composition (A relies on B relies on C) = contract chaining. The integrity/identity
half — trusting a foreign proof — maps onto software-supply-chain attestation
(in-toto): hash each artifact, bind operations by policy, and (the open part)
authenticate the *actor*, which in-toto itself flags as not solved by hashing
alone.
 
**Deliberate divergence.** Contract theory reasons over behaviors/specifications;
SEG's "contract" is a hash-pinned requirement boundary plus a recomputable Merkle
proof — a *cryptographically verifiable* assume-guarantee link, with cross-graph
*staleness* (version-pin) as a first-class concern that classical AG theory does
not model. The "recompute the Merkle vs also require a signature" question is the
same actor-authentication gap in-toto documents.

**The authority half now has a ready-made logic (Cyberlogic — read 2026-07-07,
RuessShankar2023Cyberlogic).** Intuitionistic FOL with an attestation modality:
`c : K ▷ φ` — a certificate c (signature over φ or its hash) *realizes* principal
K's attestation of φ; attestation never implies validity; **trust exists only as
an explicit, scoped axiom `k ▷ φ ⇒ φ`**; delegation, revocation, and timed
attestation are definable; distributed proof search assembles tree-like,
poly-time-checkable certificates. Three consequences for SEG: (1) **DEC-026's
assessor certificate gets a semantics for free** — "signature over (hash(case),
BOM)" is literally `c : Assessor ▷ φ(hash(case), BOM)`; anchor it there instead
of inventing one. (2) **The DEC-017 thesis has a crisp logical form**: a SEG
consumer *never* adopts the trust axiom `K ▷ verdict(x) ⇒ verdict(x)` — roll-up
verdicts are recomputed, not trusted — while affirmations of ground facts may be
adopted under scoped axioms gated by the seal check (DEC-023/024's resolution
discipline, stated logically). (3) The **staleness axes are complementary**:
cyberlogic's revocation/timed attestation handle *authority* going stale; SEG's
drift handles *content* going stale; neither subsumes the other. What cyberlogic
does NOT have (checked): artifact graphs, content drift, suspicion, verdict
semantics over evidence, assurance-case structure — it is the trust/PKI logic
layer, complementary the way SPDX is on the schema side. Watch: the ETB
implementation now "supports Cyberlogic-like attestations based on IPFS"
(authority + content addressing converging from the other side); and CyberGSN
(BeyeneCarlan2021, unread stub) already couples this logic to safety-case
notation.
 
**Leading references.** Benveniste, Caillaud, Nickovic, Passerone, Raclet,
Reinkemeier, Sangiovanni-Vincentelli, Damm, Henzinger, Larsen, "Contracts for
System Design" (Foundations and Trends in EDA, 2018); Meyer, "Applying Design by
Contract" (IEEE Computer, 1992); Jones, rely-guarantee (1983); Torres-Arias,
Afzali, Kuppusamy, Curtmola, Cappos, "in-toto: Providing Farm-to-Table Guarantees
for Bits and Bytes" (USENIX Security 2019); SLSA framework (2021).
 
## Closest APPLIED prior art — lightweight VCS-based requirements traceability
 
**The tools that occupy SEG's exact niche** (open-source safety projects: RTEMS,
Space ROS). Unlike the formalism layers above, these are deployed tools SEG must beat,
not theory it builds on — they are the related-work baseline *and* the evaluation
target.
 
**What they do.** *Doorstop:* a DAG of typed YAML items; a SHA-256 fingerprint over the
*normative* fields only; review "stamps" that flag an item when a linked item changes.
*OpenFastTrace (OFT):* specification items with artifact-type-in-ID (`req~`/`dsn~`/`impl~`);
shallow + deep (whole-chain) coverage; revision-pinned coverage tags that break the chain
on an upstream revision bump; a stateless tracer (recomputes every run).
 
**The overlap (must NOT be claimed as novel).** Content fingerprinting with field
selection; affirmation/review stamps; break-on-change; and — because OFT's tracer is
stateless and whole-chain — transitive coverage failure with automatic clear-on-re-trace.
**Hands-on verified** (2026-07-04, Doorstop 3.1 / OFT 4.5.0; pre-registered spikes,
`seg_tool_landscape.md` WP-1/WP-2), with three sharpenings the delta list below relies
on: Doorstop's stamps are one-sided (parent-only) and its referenced source is never
content-bound (even the opt-in sha is review-time bookkeeping); OFT's whole-chain break
fires only on a manual revision bump (content edits pass silently) and it stores
nothing — no affirmation concept exists; and a test *outcome* is unrepresentable in
OFT's model (a `utest` item asserts existence, not a result) and has no Doorstop item
type either — the design/evidence split is absent in both tools.
 
**The SEG delta (the redrawn novelty).** (1) a *programmable* stratified-Datalog verdict
layer vs their *hardwired* coverage check; (2) a *global, recomputable* commitment over
the whole graph + a sealed proof object vs their *per-item / per-link* integrity; (3)
assume-guarantee *composition of sealed proofs* across projects — they have no proof
object; (4) a *graph-type definition that compiles to engines* vs their *conventions*.
 
**Leading references.** Browning & Adams, "Doorstop: Text-Based Requirements Management
Using Version Control" (2014); OpenFastTrace (itsallcode, open-source software; cite
repository + version); and the traceability lineage — Gotel & Finkelstein, "An Analysis
of the Requirements Traceability Problem" (RE 1994); CoEST / Cleland-Huang et al. on
traceability. The lineage's history and its convergence with the assurance-case
lineage are elaborated in "The two lineages" below.
 
---

## The two lineages — the field's history read through SEG/TSF (2026-07-06)

**What this is.** The historical synthesis behind `seg_tsf_duality.md` §4: SEG's
problem sits at the confluence of two research lineages with complementary
primitives and complementary pathologies. Companion: the duality note (why the
frameworks at the two poles are near-duals); this section owns the *history*.

### Lineage A — requirements traceability (the artifact lineage → SEG's pole)

Began as defense-procurement bookkeeping, not theory: US military software
standards of the 1970s–80s (DOD-STD-2167A and kin) required hand-maintained
traceability matrices as deliverables. **Gotel & Finkelstein 1994** is the founding
*analytic* paper — traceability defined as "the ability to describe and follow the
life of a requirement, in both a forwards and backwards direction": an ontology of
**artifacts and navigation**, in which a trace link takes you somewhere but asserts
nothing checkable. Their diagnosis — links decay, and nobody knows who vouched for
them — named the disease the tool lineage still has. Waypoints after: **Ramesh &
Jarke 2001** (reference meta-models, typed-link taxonomies — the ancestor of typed
edges and of sphinx-needs' link vocabulary); **CoEST** and the **Grand Challenges of
Traceability** (Cleland-Huang/Gotel/Zisman et al., 2012) — the field's own admission
that **trusted** and **ubiquitous** traceability are unsolved; and a fifteen-year
sub-community on automated trace *recovery* (IR/ML link guessing) — attacking the
*cost* of decay, not its semantics.

Under SEG's perspective: the five spiked tools, RTEMS, and dotstop's mechanical
layer are direct industrial descendants; the drift axis measured in
`seg_tool_comparison.md` §1 *is* Gotel & Finkelstein's decay problem, forty years
on, unsolved in four of five tools. SEG reads as this lineage taking its own grand
challenges literally: "trusted" → affirmation + commitment; decay → content-hash
drift; and — the step the lineage never took — links acquire truth conditions
(typed edges as claim schemas; verdict rules as their semantics).

### Lineage B — argumentation / assurance cases (the argument lineage → TSF's pole)

Philosophical root: **Toulmin 1958**, against reducing practical argument to
deductive syllogism — six roles (Claim, Data/Grounds, Warrant, Backing, Qualifier,
Rebuttal), with warrants field-dependent and defeasible: a human stands behind each
inference step. Operationalized under UK goal-based regulation (nuclear; offshore
oil after Piper Alpha 1988 / the Cullen report): the operator must *argue* safety
with evidence — the "safety case." Notations: **GSN** (Kelly & McDermid, York;
Kelly 1998), **CAE** (Adelard), unified in **OMG SACM**; **modular GSN** (away
goals, argument contracts between case modules) is the composition ancestor —
TSF's needs graph has a named GSN ancestor.

The lineage documented its own pathologies: **(a)** nothing checks the argument —
warrants are prose (TSF verbatim: "we cannot lint, test or otherwise automatically
verify the underlying logic"); **(b)** confirmation bias — Leveson's critique; the
**Haddon-Cave Nimrod Review (2009)** made it official after a fatal accident
(safety cases as compliance paperwork); **(c)** stale evidence — the case is a
document, the system moves, GSN/CAE/SACM don't notice; **(d)** quantified
confidence — a contested subfield (Bloomfield/Littlewood; SEI eliminative
induction — Goodenough/Weinstock/Klein; Denney/Pai/Habli confidence maps) with no
consensus on whether numbers propagate through argument structures. TSF's
calibrated-SME mean-propagation is a new entry in *that* debate; the semiring
critique (`seg_tsf_duality.md` §6.3) has two decades of precedent there.

### The crossing

Toulmin's six roles, realized at both poles:

| Toulmin role | TSF realizes it as | SEG realizes it as |
|---|---|---|
| Claim | Statement node | derived atom (never materialized) |
| Data | Premise + hashed Reference | EDB fact = content-anchored node |
| Warrant | Link — human-reviewed prose | Datalog rule — mechanical, committed |
| Backing | SME calibration/review | affirmation + ruleset under commitment |
| Qualifier | score ∈ [0,1] | three-state verdict |
| Rebuttal | suspect-on-change | suspect state / drift |

Two readings. The **rebuttal row is the convergence**: both poles mechanize
Toulmin's rebuttal as content drift — the hashing/suspect/review layer where
dotstop and SEG coincide, the artifact lineage's one exportable technology. The
**warrant row is the divergence**: TSF keeps the warrant human (faithful to
Toulmin; inheriting pathology (a)); SEG mechanizes it as a rule — which is what
lets the qualifier be a *verdict* instead of a subjective number, at the price of
covering only mechanizable warrants. Each pole's pathologies are repaired by the
other lineage's technology; each framework is one lineage's answer to the other's
open problems.

**Honesty flag — RESOLVED (primary-source read, 2026-07-07).** "Generate the
argument mechanically" is **occupied territory** — do not claim it: Basir/Denney/
Fischer derived safety cases from automatically constructed proofs (2009);
AdvoCATE auto-generates GSN fragments by pattern instantiation over hazard/
requirements tables and by translating AutoCert proof output, composing them
with manual argument (ASE-journal manuscript read in full); ETB represents the
assurance argument *as* the Datalog derivation of claims from evidence, with
replayability and identification of "the evidence artifacts such as files (and
file contents) used in the derivation" (VMCAI 2013 / semantics 2014, read).
**What the read establishes as the surviving delta** (each checked against the
sources): (a) **no content binding of evidence anywhere** — the 64-page AdvoCATE
manuscript has zero occurrences of hash/checksum/stale/fresh; its "evolution" is
a coarse-grained lifecycle vision; ETB identifies file contents for *replay*,
not for drift — "maintain the argument against changes to inputs" is stated as
desirable, not mechanized; (b) **no affirmation lifecycle** — Rushby's `good_doc`
predicate (SSS 2010, read) is the closest kin: an *identified* reviewer
judgement asserted as an axiom that gates derivation (structurally SEG's
affirmation and TSF's B factor!) — but it is not content-bound and nothing
retracts it when the documented artifact changes; **cite it when introducing
affirmation**; (c) **ETB Datalog is the positive fragment** ("we restrict
ourselves to the positive fragment") — suspect-gating needs default negation
(the WP-7 T8 program's `not reviewed(X)`), so SEG's stratified verdict layer is
strictly beyond ETB's language, not just its usage; (d) no commitment/seal, no
signature, no cross-organization recompute story in any of the three. So the
claimable form: **not** "we generate arguments" but "the argument view is one
lawful projection out of a content-committed, drift-tracked, affirmation-gated
graph — and stays live under change rather than being generated once."

**Watch item CLOSED (full read 2026-07-07) — with a sharpening.** The 2024 ETB
paper (Sorokin/Bouchekir/Beyene, fortiss + DENSO; AVP case study; ETB2 at
git.fortiss.org/etb2) goes further than expected: evidence artifacts are
"managed internally by ETB using a **hash identifier**" (content hashes visible
in their Fig. 6 output), and §3.6 has real **incremental maintenance** — a
"lightweight static dependency computation procedure" computes the impacted
sub-tree on updates, splitting *directly impacted* goals (always re-run) from
*indirectly impacted* ones (re-run only if a direct re-run changed an
artifact). So the "stays live under change" clause is **partially occupied in
its mechanical sense** — rtemsspec-style recompute-on-change, now on the
argument side. The delta list, re-checked against this paper: **no affirmation
or review state** (updates trigger re-runs; nothing is attested, nothing is
suspect; workflow validation "have to be done manually by the user", no
recorded state); **positive Datalog** throughout (goal conjunctions; no
negation — the B factor remains inexpressible); **no commitment/seal** over
the claims DB; distribution = multi-node evidence collection under mutual
trust (no cross-org semantics; no verdict-travel concern surfaces because
nodes simply trust claims); confidence argumentation explicitly future work.
**Final claim wording:** the argument view is a projection out of a
content-committed graph that stays live under change *with assurance-state
semantics* — the projection knows what a human vouched for, what that vouching
no longer covers (suspect), and carries a seal a third party recomputes.
Mechanical re-derivation alone is now prior art twice over (rtemsspec WP-6;
ETB-2024). New lead from their bibliography, stubbed below: Ruess & Shankar,
"Evidential transactions with cyberlogic" (2023) — authority/attestation
semantics ("K says P"); brushes the *exchange* story; unread.

---

## Consolidated bibliography (BibTeX-ready stubs — verify keys before paper)
 
- **Toulmin1958** — S. Toulmin, *The Uses of Argument*, Cambridge Univ. Press, 1958.
- **Merkle1987** — R. C. Merkle, "A Digital Signature Based on a Conventional
  Encryption Function," CRYPTO 1987, LNCS 293, pp. 369–378.
- **Meyer1992** — B. Meyer, "Applying Design by Contract," IEEE Computer, 1992.
- **BenalohDeMare1993** — J. Benaloh, M. de Mare, "One-Way Accumulators: A
  Decentralized Alternative to Digital Signatures," EUROCRYPT 1993.
- **GelfondLifschitz1988** — M. Gelfond, V. Lifschitz, "The Stable Model Semantics
  for Logic Programming," ICLP/SLP 1988. (ASP foundation; clingo's semantics)
- **VanGelder1991** — A. Van Gelder, K. Ross, J. Schlipf, "The Well-Founded
  Semantics for General Logic Programs," JACM 38(3), 1991.
- **AbiteboulHullVianu1995** — S. Abiteboul, R. Hull, V. Vianu, *Foundations of
  Databases*, Addison-Wesley, 1995.
- **Potassco2011** — M. Gebser, B. Kaufmann, R. Kaminski, M. Ostrowski, T. Schaub,
  M. Schneider, "Potassco: The Potsdam Answer Set Solving Collection,"
  AI Communications 24(2), 2011. (clingo)
- **GotelFinkelstein1994** — O. Gotel, A. Finkelstein, "An Analysis of the
  Requirements Traceability Problem," ICRE/RE 1994. (traceability lineage)
- **Browning2014Doorstop** — J. Browning, R. Adams, "Doorstop: Text-Based
  Requirements Management Using Version Control," 2014. (closest applied prior art)
- **OpenFastTrace** — itsallcode, "OpenFastTrace" requirement tracing suite
  (open-source software; cite repository + version). (closest applied prior art)
- **Rozenberg1997** — G. Rozenberg (ed.), *Handbook of Graph Grammars and Computing
  by Graph Transformation, Vol. 1*, World Scientific, 1997.
- **Kelly1998** — T. Kelly, *Arguing Safety: A Systematic Approach to Managing
  Safety Cases*, PhD thesis, University of York, 1998.
- **BishopBloomfield1998** — P. Bishop, R. Bloomfield, "A Methodology for Safety
  Case Development," Safety-Critical Systems Symposium, 1998. (CAE)
- **CamenischLysyanskaya2002** — J. Camenisch, A. Lysyanskaya, "Dynamic
  Accumulators and Application to Efficient Revocation of Anonymous Credentials,"
  CRYPTO 2002.
- **EhrigEtAl2006** — H. Ehrig, K. Ehrig, U. Prange, G. Taentzer, *Fundamentals of
  Algebraic Graph Transformation*, Springer, 2006.
- **CatalanoFiore2013** — D. Catalano, D. Fiore, "Vector Commitments and Their
  Applications," PKC 2013.
- **MillerHicksKatzShi2014** — A. Miller, M. Hicks, J. Katz, E. Shi, "Authenticated
  Data Structures, Generically," POPL 2014.
- **Benet2014** — J. Benet, "IPFS — Content Addressed, Versioned, P2P File System,"
  arXiv:1407.3561, 2014.
- **Knublauch2017SHACL** — H. Knublauch, D. Kontokostas, "Shapes Constraint
  Language (SHACL)," W3C Recommendation, 2017.
- **Motik2012OWL2Profiles** — B. Motik, B. Cuenca Grau, I. Horrocks, Z. Wu,
  A. Fokoue, C. Lutz, "OWL 2 Web Ontology Language Profiles (2nd ed.)," W3C
  Recommendation, 2012. (OWL 2 RL — the fragment the "two walls" argument rules out)
- **Benveniste2018Contracts** — A. Benveniste et al., "Contracts for System
  Design," Foundations and Trends in EDA, 12(2–3), 2018.
- **Corman2018RecursiveSHACL** — J. Corman, J. L. Reutter, O. Savković, "Semantics
  and Validation of Recursive SHACL," ISWC 2018, LNCS 11136, pp. 318–336.
- **TorresArias2019Intoto** — S. Torres-Arias et al., "in-toto: Providing
  Farm-to-Table Guarantees for Bits and Bytes," USENIX Security 2019.
- **Andresel2020StableSHACL** — M. Andreşel et al., "Stable Model Semantics for
  Recursive SHACL," The Web Conference (WWW) 2020, pp. 1570–1580.
- **OMG2021SACM** — Object Management Group, "Structured Assurance Case Metamodel
  (SACM)," v2.x, 2021.
- **BogaertsJakubowski2021** — B. Bogaerts, M. Jakubowski, "Fixpoint Semantics for
  Recursive SHACL," ICLP Technical Communications, EPTCS 345, 2021.
- **BogaertsVdB2022DLDisguise** — B. Bogaerts, M. Jakubowski, J. Van den Bussche,
  "SHACL: A Description Logic in Disguise," LPNMR 2022, LNCS 13416.
- **GSN2023** — Assurance Case Working Group, "Goal Structuring Notation Community
  Standard," v3, 2023.

Added 2026-07-06 (two-lineages section + duality note; ALL unverified stubs):

- **RameshJarke2001** — B. Ramesh, M. Jarke, "Toward Reference Models for
  Requirements Traceability," IEEE TSE 27(1), 2001. (typed-link taxonomies)
- **ClelandHuangGotelZisman2012** — J. Cleland-Huang, O. Gotel, A. Zisman (eds.),
  *Software and Systems Traceability*, Springer, 2012. (CoEST)
- **GotelEtAl2012GrandChallenges** — O. Gotel et al., "The Grand Challenge of
  Traceability (v1.0)," in *Software and Systems Traceability*, Springer, 2012.
  (trusted/ubiquitous traceability — verify exact chapter authors)
- **HaddonCave2009** — C. Haddon-Cave, *The Nimrod Review*, HMSO, 2009.
  (safety-cases-as-paperwork critique)
- **Leveson2011SafetyCases** — N. Leveson, "The Use of Safety Cases in
  Certification and Regulation," MIT ESD working paper, 2011. (verify venue/year)
- **GoodenoughWeinstockKlein2012** — J. Goodenough, C. Weinstock, A. Klein,
  "Toward a Theory of Assurance Case Confidence," SEI CMU/SEI-2012-TR-002, 2012.
  (eliminative induction; verify report number)
- **BloomfieldLittlewoodConfidence** — R. Bloomfield, B. Littlewood — confidence /
  multi-legged dependability arguments (exact paper TBD: DSN 2003 "Multi-legged
  Arguments" or the later confidence-in-claims line; pick during hardening).
- **DenneyPaiPohl2012AdvoCATE** — E. Denney, G. Pai, J. Pohl, "AdvoCATE: An
  Assurance Case Automation Toolset," SAFECOMP 2012 Workshops (SASSUR), LNCS
  7613, Springer, 2012. **[verified 2026-07-07 via search; venue/volume from
  publisher listing]**
- **DenneyPai2018ToolSupport** — E. Denney, G. Pai, "Tool Support for Assurance
  Case Development," Automated Software Engineering (journal; NASA NTRS
  20170011550 manuscript **read in full 2026-07-07** — zero hash/staleness
  content; verify final vol/pages before cite). (argument auto-generation kin)
- **BasirDenneyFischer2009** — N. Basir, E. Denney, B. Fischer, "Deriving Safety
  Cases from Automatically Constructed Proofs," 4th IET Intl. Conf. on System
  Safety, London, 2009. **[found as Rushby's ref [2]; the origin of the
  generation line — verify pages]**
- **Rushby2010Formalism** — J. Rushby, "Formalism in Safety Cases," in *Making
  Systems Safer* (Proc. 18th Safety-Critical Systems Symposium), pp. 3–17,
  Springer, 2010. **[read in full 2026-07-07]** — NB the `good_doc` affirmation
  kin; cite when introducing affirmation.
- **CruanesEtAl2013ETB** — S. Cruanes, G. Hamon, S. Owre, N. Shankar, "Tool
  Integration with the Evidential Tool Bus," VMCAI 2013, LNCS 7737,
  pp. 275–294. (ETB; paywalled — capability claims taken from the 2014
  semantics paper instead)
- **CruanesEtAl2014ETBSemantics** — S. Cruanes, S. Heymans, I. Mason, S. Owre,
  N. Shankar, "The Semantics of Datalog for the Evidential Tool Bus (Extended
  Abstract)," Futatsugi Festschrift (Specification, Algebra, and Software),
  LNCS 8373, Springer, 2014. **[read in full 2026-07-07]** — positive-fragment
  restriction stated on p.4.
- **SorokinEtAl2024ETBContinuous** — L. Sorokin, R. Bouchekir, T. A. Beyene,
  B. H.-C. Liao, A. Molin, "Towards Continuous Assurance Case Creation for ADS
  with the Evidential Tool Bus," arXiv:2403.01918, 2024 (fortiss/DENSO, FOCETA;
  ETB2: git.fortiss.org/etb2). **[read in full 2026-07-07]** — hash-identified
  evidence; change-impact incremental re-derivation; no affirmation state, no
  negation, no seal.
- **RuessShankar2023Cyberlogic** — H. Ruess, N. Shankar, "Evidential
  Transactions with Cyberlogic," SRI CSL Technical Report SRI-CSL-2023-01 /
  arXiv:2304.00060, 2023. **[read 2026-07-07 — complementary, not competing;
  assessment in the Seam section]** — intuitionistic FOL + attestation modality
  `K ▷ φ`; certificates as realizers (`c : K ▷ φ` = signature over φ or its
  hash); attestation ⇏ validity; trust ONLY as explicit axiom `k ▷ φ ⇒ φ`;
  delegation/revocation/timed attestation definable; distributed proof search
  builds tree-like certificates (poly-time checkable; scaling caveats).
- **BeyeneCarlan2021CyberGSN** — T. A. Beyene, C. Carlan, "CyberGSN: A
  Semi-formal Language for Specifying Safety Cases," DSN-W 2021, pp. 63–66.
  (cyberlogic-adjacent safety-case language — the bridge artifact between the
  authority logic and lineage B; **unread**, low priority, skim before Paper 1
  related work freezes)
- **Kelly2001ModularGSN** — T. Kelly, compositional/modular safety case
  construction (exact cite TBD; away goals, argument contracts). (composition
  ancestor of TSF's needs graph and modular exchange)
- **GreenKarvounarakisTannen2007** — T. J. Green, G. Karvounarakis, V. Tannen,
  "Provenance Semirings," PODS 2007. (the duality note §6 universal object;
  survey the negation/monus follow-ups before citing for stratified rulesets)
- **EclipseTSF** — Eclipse Trustable Software Framework, pages.eclipse.dev/
  eclipse/tsf/tsf + gitlab.eclipse.org/eclipse/tsf/tsf (retrieved 2026-07-06;
  pin trudag version at WP-7 spike time).

### Gaps to fill before submission
- Requirements traceability lineage — **elaborated 2026-07-06** ("The two
  lineages" section); remaining work is stub verification (Ramesh & Jarke,
  grand-challenges chapter authors).
- Argument-generation kin — **RESOLVED 2026-07-07, all four primaries read**
  (Rushby SSS10, ETB semantics 2014, AdvoCATE ASE manuscript, ETB-2024
  continuous-assurance; outcome + final claim wording in the two-lineages
  section's honesty flag — NB the 2024 read *sharpened* the wording: mechanical
  liveness-under-change is occupied; claim the assurance-state half).
  Remaining: verify BasirDenneyFischer2009 pages and DenneyPai2018 final
  vol/pages. ~~Read RuessShankar2023Cyberlogic~~ **done 2026-07-07**
  (complementary; assessment in the Seam section — DEC-026 gets its semantics,
  DEC-017 its logical form). New (low priority): skim CyberGSN
  (BeyeneCarlan2021) before Paper-1 related work freezes; watch ETB's
  IPFS-based attestation layer.
- IEC 61508 itself + any existing tool-qualification / evidence-management prior art.
- ShEx primary citation (exact author/year/venue) — currently a stub.
- Verkle trees (if `flat`/`deep` discussion wants the modern commitment frontier).