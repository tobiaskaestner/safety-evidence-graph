# SEG — Paper Seed (contribution & novelty)

**What this is.** Raw material for a paper, captured — *not* a section structure.
Records SEG's actual contribution, kept separate from the prior art it reuses.
**Revised** after a prior-art check surfaced two close applied tools (OpenFastTrace,
Doorstop); the novelty boundary below is the *redrawn* one. Read with
`seg_prior_art.md` (literature map) and `seg_reconciliation.md` (term verdicts).

---

## 1. One-line framing

SEG is a **cryptographically-committed, drift-tracking assurance case with a
programmable verdict layer and assume-guarantee composition**.

## 2. Closest applied prior art (the baseline to beat)

Two open tools occupy almost exactly SEG's niche — version-controlled, text-based
requirements traceability for open-source safety projects (RTEMS, Space ROS):

- **Doorstop.** A DAG of typed items, each a YAML file; a **SHA-256 fingerprint over
  the *normative* fields** of an item (deliberately excluding non-normative ones); and
  **review "stamps"** that mark an item reviewed until a linked item changes.
- **OpenFastTrace (OFT).** Specification items with a mandatory artifact-type-in-ID
  convention (`req~…`, `dsn~…`, `impl~…`); **shallow + deep coverage** (deep coverage
  traces the whole chain); and **revision-pinned coverage tags** that *break the chain*
  when an upstream item's revision bumps. The tracer is **stateless** — it recomputes
  coverage every run.

**This forces honesty.** Several things the first draft of this seed called novel are
*already shipping* in these tools and MUST NOT be claimed:

- content fingerprinting with **field selection** (normative vs non-normative) — that
  is Doorstop's fingerprint; it is also our `hash_fields` vs `tracked` split.
- **affirmation / review stamps** and **break-on-change** — Doorstop's review stamps and
  OFT's revision-pinned coverage breaking on an upstream bump.
- **transitive propagation + auto-clear** — OFT's deep-coverage tracer is stateless and
  whole-chain, so transitive coverage failure *and* automatic clearing-on-re-trace are
  arguably already present. (Trigger differs — OFT uses a manual revision integer, SEG a
  content hash — but the architectural shape is a cousin. The precise transitive-*break*
  semantics in OFT warrant a hands-on check before any claim.)

## 3. The redrawn novelty boundary (what genuinely survives)

Against these tools specifically, four things have no counterpart:

1. **A programmable, declarative verdict layer (stratified Datalog).** *This is the
   primary contribution* — promoted from secondary after the prior-art check. OFT and
   Doorstop answer one *hardwired* question ("is everything covered?"); their validity
   logic is baked into the tool. SEG lets the user *author* the validity predicate —
   ADR-adherence, waivers, domain-specific satisfaction (e.g. our `impl_violates_adr`) —
   with a tractability guarantee borrowed from recursive-SHACL (stratified fragment:
   LFP = well-founded = stable-model coincide) and a single-answer-set determinism
   guardrail. Neither tool can express a user-defined verdict rule.
2. **A global, recomputable commitment over the whole graph + a sealed proof object.**
   Doorstop fingerprints *individual items*; OFT pins *individual link revisions* — both
   are **local, per-link** integrity. Neither emits a single cryptographic commitment
   over the entire evidence graph (`merkleHash` / design root) that a third party
   recomputes to verify the whole case at once. SEG's local (`edgeHash`) + global
   (`merkleHash`) two-mode commitment, sealed into an independently-verifiable proof, is
   unlike either tool.
3. **Assume-guarantee composition of sealed proofs across projects (DEC-010).** Neither
   tool has a proof object, so neither has a composition story. Importing a hash-pinned
   requirement boundary and discharging it via another project's sealed proof, valid iff
   assumptions ⊆ proven scope, has no analogue.
4. **A graph-type definition / meta-model that compiles to existing engines
   (projection-core).** OFT/Doorstop have *conventions* (artifact-type-in-ID, YAML
   attributes); SEG has a *schema language* that generates SHACL + Datalog + commitment
   config. The "definition transpiles to validators" idea has no counterpart.

## 4. The novel core, restated (the technical heart, post-redraw)

The defensible kernel is **the binding of a programmable verdict layer and a derived
suspicion closure to a two-mode cryptographic commitment over the whole graph** — i.e.
contributions 1+2 fused. The suspicion lifecycle itself (states, direct vs transitive,
derivation, auto-clear) is *shared in shape* with OFT's stateless coverage tracer; what
is ours is (a) its trigger being a content-hash *drift* event rather than a manual
revision bump, and (b) its integration with a global recomputable proof and a
user-authored verdict rule set. Claim the *integration and the verdict/commitment
seams*, not the lifecycle in isolation.

## 5. The borrowed substrate (cite, don't claim)

Per-layer canonical formalisms (full refs in `seg_prior_art.md`): typed attributed
graphs (Ehrig et al.); SHACL/ShEx shapes; recursive-SHACL + stratified Datalog
(tractability vindication of DEC-007); Merkle/Merkle-DAG (deep) + accumulators (flat)
= structure-binding vs set commitment; GSN/CAE/SACM assurance cases (Toulmin root);
assume-guarantee / contract-based design (Benveniste et al.); in-toto/SLSA/Sigstore for
the signing/identity half (and its known actor-authentication gap). **And now: OFT +
Doorstop as the closest *applied* prior art**, plus the traceability lineage (Gotel &
Finkelstein).

## 6. Secondary contributions

- **Soundness reduces to a handful of static invariants** (field-routing totality;
  acyclicity of the deep-fingerprint union; verdict purity; verdict determinism). The
  *trusted core is these checks, not the engines.*
- **The projection-core architecture** (thin integrity core + one-directional,
  overlapping, derived projections). Note this now also underpins contribution 4.
- **Verdict reproducibility** (sealed verdict = pure function of committed content +
  sealed evidence; `tracked` state is report-only). This is what makes a SEG proof a
  *proof* and is exactly what OFT/Doorstop's local checks do not provide.

## 7. Evidence already in hand (runnable)

- `seg_demo_shacl_projection.py` — structural validation via real SHACL on a projection.
- `seg_demo_datalog_projection.py` — satisfaction + direct/transitive suspicion.
- `seg_demo_clingo_verdict.py` — verdicts on real clingo; determinism guardrail trips on
  an injected refines cycle.

## 8. Not yet evidence / claim — be honest

- **OFT & Doorstop are the related-work baseline AND the evaluation target.** Strongest
  framing: "these tools established lightweight, hash/revision-pinned traceability for
  OSS safety projects; SEG asks what they must become to be a *machine-checkable,
  cryptographically-committed, composable* assurance case — a programmable verdict layer,
  a global recomputable proof, and assume-guarantee composition." A comparison/migration
  story (can SEG ingest a Doorstop tree? can it reproduce OFT's coverage as one verdict
  ruleset?) would be a strong evaluation.
- **Verify directly:** OFT's transitive-break + re-trace-clear semantics, to fix exactly
  how much of the suspicion lifecycle is shared vs novel.
- Composability (DEC-010) is designed, not built.
- Signed external projection (in-toto/DSSE) not yet pressure-tested.
- No Zephyr-scale evaluation yet (clingo grounding may need Soufflé/Nemo).
- Bibliography entries are stubs pending verification.

## 9. Venue framings (talk tuning)

Same spine, emphasis reorders per audience. Active plan: **ZiSE** + **OSS Summit
Safety**. The **Zephyr Developer Summit** variant is noted as the practitioner cut
(where the concrete-workflow material belongs — not ZiSE).

### ZiSE (Zephyr in Science & Education) — academic
Centerpiece = **twin contributions**, with vocabulary as the *instrument* behind them:
1. **The facet design space.** Content-addressed evidence graphs decompose into a small
   set of facets — `binds`, `propagates`, `fingerprint ∈ {none,deep,flat}`, `acyclic` —
   that are *orthogonal but entailment-linked* (`fingerprint:deep ⟹ acyclic` hard;
   `satisfaction-role ⟹ acyclic` soft; `propagates` cycle-tolerant). The axes + their
   dependency structure are the finding.
2. **The projection-core architecture.** One integrity-shaped source; lawful,
   one-directional, *overlapping* derived projections; each layer/facet discharged by a
   different existing engine.

- **Do NOT pitch it as "a common vocabulary"** — a reviewer hears "terminology." The
  glossary is how we *found* the axes; pitch the **design space with named,
  dependency-linked axes**. Vocabulary is the instrument, not the headline.
- **Existing tools = facet-*bundling* points.** Doorstop/OFT aren't merely points in the
  space — they collapse several facets into one switch (the `strong` bundle), which is
  *why* they can't reach regions like programmable verdicts. The `calls` contradiction is
  the existence proof that the bundling is a real limitation, not a style choice.
- **Zephyr = motivating & validating instance, not a dependency.** Large, real,
  safety-targeted, `west`-managed multi-repo — exactly where "evidence over an evolving
  multi-repo graph" gets hard. The research question *arises in* Zephyr but generalizes.
  (This is the shape ZiSE wants: a Zephyr-arising question that generalizes.)
- **Pose open research questions** (academic venues reward these): the
  vocabulary/satisfaction boundary (the `excuses`-generalization tension); is the facet
  set *complete*?; is the three-engine compilation *semantics-preserving*?; must
  projections partition, or is overlap essential — and what soundness property governs
  overlapping derived views?; the per-type facet questions (`witnesses`-binds
  independence).
- **Caution:** present the facet set as the *best decomposition found*, NOT as proven
  complete (known soft spot: the `witnesses`-binds question). Honesty is an asset here.

### OSS Summit — Safety track (cross-project; standards / supply-chain literate)
Centerpiece = **ecosystem position + interoperability + composition.**
- Lead with the **OFT/Doorstop comparison** (this audience uses them) and the redrawn
  boundary (§2–§4).
- **SPDX 3.x projection** — their native vocabulary. SEG projects an *assurance* graph
  (not a BOM) into SPDX Elements/Relationships, extending the ecosystem from "what is in
  the build" to "why the build satisfies its safety requirements." Frame the global
  commitment (`merkleHash`) as what SPDX per-element integrity *cannot* express — the
  serialization face of contribution #2. SPDX is an OSS-Summit asset; NOT in the Zephyr
  talks. **UNVERIFIED — run the SPDX checks (RelationshipType vocabulary, 3.1 profile
  catalog/changelog, `verifiedUsing`/`IntegrityMethod`) before claiming "SPDX can't.")**
- **Assume-guarantee composition** of sealed proofs across projects — resonates directly
  with supply-chain thinking (one project relying on another's verified artifact).
- **in-toto / SLSA / Sigstore** signing + transparency-log story; the "recompute-vs-sign"
  question = the known in-toto actor-authentication gap.
- Frame the verdict layer as **programmable policy** (maps to their Rego/CUE world), not
  as Datalog semantics.

### Zephyr Developer Summit — practitioner variant (if used)
Centerpiece = **concrete workflow + teachable architecture.**
- A real Zephyr tree: requirement ↔ Zephyr test ↔ driver impl; drift when a
  `west`-managed source file is edited; a real safety verdict rule.
- Lead with the **runnable demos**; formal lineage (recursive-SHACL, stratified Datalog)
  is supporting depth, not headline.
- Teaching moments: the prism/projection intuition; the clingo
  determinism-guardrail-trips-on-an-injected-cycle demo (memorable "why acyclicity
  matters").
