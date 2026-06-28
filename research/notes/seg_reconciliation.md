# SEG — Term Reconciliation & Leverage Map

**Purpose.** Stay in charted territory. For each SEG term, give the established
literature term and a verdict: **[SUB]** adopt the literature term and retire ours,
**[EXPLAIN]** keep ours but gloss it with the standard term, **[NOVEL]** no
equivalent (this is where the paper's contribution concentrates). A final column
names the off-the-shelf artifact SEG can *build on* rather than reimplement.

**Strategy.** Maximise reuse. Where a layer has a mature engine, SEG should be a
thin orchestration over it, not a reimplementation. Novelty is allowed only at the
seams the literature does not cover.

---

## A. Vocabulary reconciliation (by layer)

### Layer 1–2: structure & shapes

| SEG term | Literature term | Verdict | Note |
|---|---|---|---|
| graph-type definition | type graph (attributed) + shape schema | EXPLAIN | TG defines valid instances; shapes add neighbourhood constraints. |
| node type / edge type | typed/attributed graph node & edge types | SUB | Standard; adopt "type graph" framing. |
| domain / range | property shape `sh:class` on subject/object; edge typing | SUB | Direct SHACL equivalent. |
| constraint slot | additional graph constraints; SHACL constraint components | EXPLAIN | Cardinality etc. are catalogued SHACL components. |
| hash-field selection | (no direct term) — value extraction / `sh:path` selection | EXPLAIN | Closest is SHACL property paths, but ours selects byte spans. |
| binding adapter | (tooling) value extractor | EXPLAIN | Implementation concept, not a formal term. |
| satisfaction | shape validity / conformance | SUB | "Conforms to the shape." |
| satisfaction ruleset | recursive SHACL schema / stratified Datalog program | SUB | Adopt "stratified constraint set." |
| verdict | shape-assignment value (valid/violated); "valid typing" | SUB | SACM also says "verdict" — exact word. |
| verdict layer | the validation/conformance layer | EXPLAIN | Keep as our shorthand for the derived layer. |
| stratified Datalog | stratified Datalog | SUB | Already the literature term. |
| least-fixpoint semantics | LFP semantics (= well-founded = stable on stratified) | SUB | Cite coincidence result. |
| transitive closure | transitive closure | SUB | Standard. |

### Layer 3: the recursion / acyclicity machinery

| SEG term | Literature term | Verdict | Note |
|---|---|---|---|
| acyclic (facet) | stratification condition / DAG constraint | EXPLAIN | Our facet = a structural precondition; ties to stratification. |
| entailment lattice | (no single term) — constraint dependency / stratification order | EXPLAIN | Closest: the stratification dependency graph. Possibly NOVEL as stated. |
| leaf node | base case / leaf of the dependency graph | SUB | Standard recursion vocabulary. |

### Layer 4: commitment

| SEG term | Literature term | Verdict | Note |
|---|---|---|---|
| nodeHash / content hash | content commitment (hash commitment) | SUB | Standard. |
| edgeHash | 2-element / pairwise hash commitment | EXPLAIN | A local commitment over an ordered pair + label. |
| merkleHash / design root | Merkle-DAG root / structure-binding (vector) commitment | SUB | `deep` mode = vector/Merkle commitment. |
| fingerprint: deep | structure/position-binding commitment | SUB | Order & topology bind. |
| fingerprint: flat | set commitment / cryptographic accumulator | SUB | Order-blind membership commitment. |
| design graph | the committed substructure | EXPLAIN | = deep-fingerprint subgraph. |
| drift | (no crypto term) — "commitment no longer opens to current value" | EXPLAIN | Detected by recomputation/non-equality. |
| affirmation | (no direct term) — signing/attesting a statement | EXPLAIN | Closest: issuing an attestation over the pair. |

### Layer 5 + seam: assurance & composition

| SEG term | Literature term | Verdict | Note |
|---|---|---|---|
| Requirement | Goal / Claim (GSN/SACM) | EXPLAIN | Map to claim; keep domain name. |
| refines | decomposition Strategy (GSN) | EXPLAIN | Argument strategy edge. |
| TestOutcome / Implementation | Solution / Evidence | EXPLAIN | Evidence nodes. |
| Waiver / excuses | Assumption / managed weakener | EXPLAIN | SACM "weakener" is the precise term. |
| proof (design+evidence) | assurance case + its evidence; signed attestation | EXPLAIN | The sealed, verifiable case. |
| suspicion (direct/transitive) | (no assurance-case term) — defeater propagation | NOVEL | Closest is "defeater/weakener," but auto-propagation is ours. |
| suspect / broken / pending / active | (no standard) — validity/freshness states | NOVEL | Lifecycle states are SEG-specific. |
| auto-clear | (no standard) — derived-state recomputation | EXPLAIN | Falls out of "state is derived, not stored." |
| dependsOn / imported requirement | assume-guarantee contract link; assumption | SUB | Contract (A,G); imported req = assumption A. |
| scope-match (assumptions ⊆ proven) | contract refinement | SUB | Adopt "refinement." |
| version-pin / cross-graph staleness | (partial) — provenance digest pin | EXPLAIN | in-toto pins by digest; staleness across graphs is ours. |
| TCB / proof-bound | trusted computing base | SUB | Standard. |

**Reading of the verdicts.** Most terms are SUB or EXPLAIN — you are overwhelmingly
in charted territory. The genuine **NOVEL** cluster is small and specific: the
*suspicion lifecycle* (states + automatic direct/transitive propagation + auto-clear)
and its binding to the commitment layer. That is the paper's defensible core; almost
everything else should cite, not claim.

---

## B. Leverage map (what to build on, per layer)

| Layer | Build on | Maturity | Caveat for SEG |
|---|---|---|---|
| Shapes / structural validation | **SHACL** via pySHACL (Python) or Apache Jena SHACL (Java) | Production; W3C Rec | RDF-bound — needs SEG↔RDF mapping, or shapes-on-LPG. |
| Commit-time gate | Jena SHACL `validateTransaction` (validate-then-commit) | Production | Maps onto your commit/proof gates directly. |
| Recursive satisfaction + suspicion closure | **clingo** (ASP, prototype — embeddable, rules run as-is) → **Soufflé**/**Nemo** at scale | clingo & Soufflé production; Nemo unstable | All do stratified negation. clingo: assert exactly one answer set (determinism guardrail); only stay in the stratified fragment. |
| Incremental recompute (auto-clear, drift) | **Differential Datalog** / differential dataflow lineage | Research-grade | The exact match for "recompute only affected verdicts." |
| Content + structure commitment | hashlib + a Merkle library; accumulator lib for `flat` | Trivial / library | The `deep`/`flat` split = vector commitment vs accumulator. |
| Proof signing + identity (the actor-auth gap) | **Sigstore/cosign** + **DSSE** envelopes; **Rekor** transparency log | Production | Fills in-toto's actor-authentication gap; keyless OIDC signing. |
| Proof format / attestation envelope | **in-toto attestation** + **SLSA provenance** predicate | Production standard | Reuse the statement/predicate/DSSE structure for SEG proofs. |
| Verification-gate policy over a signed proof | **Rego** (OPA) or **CUE** policy, run by cosign verify-attestation | Production | Rego ≈ Datalog over JSON — same family as your satisfaction layer. |
| Assurance-case interchange / output | **SACM** (OMG) model; GSN for presentation | Standard | Emit SEG as a SACM instance for tool interop / auditors. |

### The assembled picture
A defensible build is: SHACL shapes for structural well-formedness (gate via
`validateTransaction`); a stratified-Datalog engine (Soufflé/Nemo) for satisfaction
and suspicion closure, with a differential-dataflow path for incremental recompute;
a thin commitment layer (Merkle for `deep`, accumulator for `flat`) over raw byte
spans; in-toto/DSSE as the proof envelope, signed via Sigstore and logged to Rekor;
Rego/CUE as the proof-verification gate; and SACM as the interchange format for
auditors. SEG's *own code* then concentrates on what no engine provides: the
content→hash binding discipline, the suspicion lifecycle, and the assume-guarantee
composition with cross-graph staleness.

### Two open decisions this surfaces
1. **RDF or not.** SHACL + Nemo + SACM all lean RDF. Committing SEG's data model to
   RDF (nodes as IRIs/blank-node-free triples) unlocks the most reuse but collides
   with the byte-span/content-hash identity model and the deferred-namespace
   decision. The alternative is shapes-on-property-graphs, with less mature tooling.
   This is now the highest-leverage architectural fork.
2. **Reuse the attestation envelope, or only its ideas.** Adopting in-toto/DSSE
   verbatim gives you signing + transparency-log + ecosystem verifiers for free, at
   the cost of fitting SEG proofs into the statement/predicate shape. Worth a
   spike before committing.

### Bibliography additions (tooling — verify before paper)
- pySHACL (RDFLib); Apache Jena SHACL; TopBraid SHACL API.
- Jordan, Scholz, Subotić, "Soufflé: On Synthesis of Program Analyzers" (CAV 2016).
- Gebser, Kaufmann, Kaminski, Ostrowski, Schaub, Schneider, "Potassco: The Potsdam
  Answer Set Solving Collection" (AI Communications 2011). (clingo — prototype engine)
- Ivliev, Gerlach, Meusel, Steinberg, Krötzsch, "Nemo: Your Friendly and Versatile
  Rule Reasoning Toolkit" (KR 2024).
- Ryzhyk & Budiu, "Differential Datalog (DDlog)" (Datalog 2.0, 2019).
- in-toto attestation spec; SLSA provenance v1; Sigstore (cosign/Fulcio/Rekor),
  "Sigstore: Software Signing for Everybody" (CCS 2022).
- OPA/Rego; CUE.
