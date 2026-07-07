# SEG — Paper Seed (contribution & novelty)

**What this is.** Raw material for a paper, captured — *not* a section structure.
Records SEG's actual contribution, kept separate from the prior art it reuses.
**Revised** after a prior-art check surfaced two close applied tools (OpenFastTrace,
Doorstop); the novelty boundary below is the *redrawn* one. Read with
`seg_prior_art.md` (literature map) and `seg_reconciliation.md` (term verdicts).
**Revised again (2026-07-04):** applied the commitment-layer corrections the decision
log had authorized (DEC-012 c4, DEC-013 c3, DEC-014 c2 — flat-sealed root, no
"two-mode/deep"), folded in the composability/exchange results (DEC-015…028 + the SPDX
round-trip prototype), and restructured §9 to the two-paper plan (Prague first; ZiSE
dropped).
**Revised (2026-07-06):** ratified reframing of SEG's identity — one identity in
three roles (comparison instrument / integrating engine / composition payoff), with
the pull-vs-novelty split made explicit. §1 extended, §9 Paper-1 lead updated.

---

## 1. One-line framing

SEG is a **cryptographically-committed, drift-tracking assurance case with a
programmable verdict layer and assume-guarantee composition**.

### 1a. Position — one identity, three roles (ratified 2026-07-06, post tool-landscape)

1. **A reasoning framework for evidence in assurance cases — demonstrated, not
   aspirational.** The tool-landscape axes (A1–A8) were derived from SEG's facet
   vocabulary and *discriminated* five tools that all self-describe as
   "traceability" (`seg_tool_comparison.md` §1); RTEMS' six documented limitations
   and their rebuild map onto the same facets (WP-6). Claim the conceptual model as
   the instrument that produced the spectra — never as an abstract "framework to
   discuss evidence" (unfalsifiable puffery; cf. the §9 Paper-2 vocabulary caution).
2. **An integrating engine, not a competing tool.** The field lacks exactly four
   semantics — two-sided content binding, stored affirmation + derived suspicion,
   programmable (recursive) verdicts, whole-case commitment (§3) — and is good at
   everything else. SEG owns the four and does not reinvent the rest: it
   consumes/projects to **sphinx-needs** for authoring/rendering (dogfooded in
   Phase B; SEG's extractor supplies the source-binding half sphinx-needs lacks,
   N5), treats evidence-format ingestion as solved territory (StrictDoc's
   JUnit/Robot/gcov readers show the shape, S7), and serializes exchange as SPDX.
   **Trust-boundary caveat (binding):** integration never moves the TCB — existing
   tools are input adapters and projection targets only (AC-003/014 seams); hashes
   stay over raw source byte spans and the parser only locates (DEC-003). Consuming
   a needs.json *as the content source* would silently inherit the drift-blindness
   N4/N7 measured.
3. **Composition over SPDX is the payoff — strongest *pull*, not the novelty
   core.** The composition gap is the widest measured (A5 "absent" across the
   matrix; the field's only cross-project mechanism is drift-blind, N7; exchanges
   are textual, O8/S8) and the ecosystem is demonstrably reaching for SPDX
   (linux-strictdoc `SPDX-Req`) — lead Paper 1 with it. The strongest *novelty*
   claim stays one layer down: the suspicion lifecycle bound to the commitment
   layer (§4), which composition is *built from* — the sealed `(G, A, I)` contract
   means something only because content binding makes drift detectable, and
   recompute-not-trust works only because verdicts are reproducible from committed
   content. WP-6 is the proof of the layering: RTEMS independently reinvented the
   *mechanics* (hash-pinned links, flat recomputable root) and stopped at build
   invalidation — the assurance semantics remain the delta. Headlining composition
   without the core invites two misreadings: SEG as yet-another exchange format
   (SPDX is the format — open thread #8), and the single-project value (where
   adoption starts) undersold.

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

All three overlap entries are now **hands-on verified** (2026-07-04, Doorstop 3.1 /
OFT 4.5.0; pre-registered spikes, evidence in `seg_tool_landscape.md` WP-1/WP-2):

- content fingerprinting with **field selection** (normative vs non-normative) — that
  is Doorstop's fingerprint; it is also our `hash_fields` vs `tracked` split (verified
  P5/P6: `attributes.reviewed` is a real committed/tracked split). **But the overlap is
  item-level only:** Doorstop never content-binds *referenced source* — the `ref`
  keyword is existence-checked, and even the opt-in `references:` sha is review-time
  bookkeeping that validation never recomputes (P8). SEG's raw-byte-span source binding
  (DEC-003) is a delta, not overlap.
- **affirmation / review stamps** and **break-on-change** — Doorstop's review stamps and
  OFT's revision-pinned coverage breaking on an upstream bump. Verified, with a
  sharpening: Doorstop's link stamp is a *one-sided* copy of the parent item's stamp —
  child-endpoint drift is invisible (P4); OFT's break is *two-sided* but fires only on
  a manual integer bump — content edits are silent (O3a).
- **transitive propagation + auto-clear** — verified **present** in OFT (O1/O3b): deep
  coverage is a stateless whole-chain fixpoint, a break propagates in both directions,
  and re-trace clears everything trivially because nothing is stored. Absent in
  Doorstop (P7: strictly one-hop). The former hands-on-check hedge is resolved; the
  shape must not be claimed.

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
   over the entire evidence graph that a third party recomputes to verify the whole case
   at once. SEG pairs a local commitment (`edgeHash`, drift detection) with a global
   **`flat-sealed` design root** — one hash over the canonically-sorted node/edge set,
   no per-node aggregation; per-node `merkleHash` is dropped (DEC-012/014) — sealed into
   an independently-verifiable proof. A `flat-openable` (Merkle) sub-mode adds selective
   disclosure and earns its place only at composition scale (DEC-012/020).
3. **Assume-guarantee composition of sealed proofs across projects (DEC-010; realized
   in prototype, DEC-015…028).** Neither tool has a proof object, so neither has a
   composition story. SEG's is now prototyped end-to-end: a case is a vector of
   per-component contracts, each opening to **`(G, A, I)`** — guarantee, assumption
   down-closure, implementation pin — under a flat-openable set-commitment, so dropping
   an assumption *or* swapping an implementation breaks the seal (DEC-019/020/028).
   Exchange runs over SPDX 3.x FuSa BOMs: a producer-side `conformsTo` declaration is
   resolved to the derived reliance edge `covers` on import (DEC-024); an undischarged
   inherited condition is either `forward`ed as an affirmation-gated condition of use
   (DEC-022) or discharged by a compliant-item supplier under a document-root
   version-pin check (DEC-023); the assessor certificate signs `(hash(case), BOM)`
   (DEC-026, design-only). The thesis throughout: **the roll-up verdict is never carried
   in a BOM — each consumer recomputes it** (recorded vs recomputed, GAPS G5).
4. **A graph-type definition / meta-model that compiles to existing engines
   (projection-core).** OFT/Doorstop have *conventions* (artifact-type-in-ID, YAML
   attributes); SEG has a *schema language* that generates SHACL + Datalog + commitment
   config. The "definition transpiles to validators" idea has no counterpart.

## 4. The novel core, restated (the technical heart, post-redraw)

The defensible kernel is **the binding of a programmable verdict layer and a derived
suspicion closure to a recomputable cryptographic commitment over the whole graph**
(local `edgeHash` + a global `flat-sealed` design root, DEC-014) — i.e.
contributions 1+2 fused. The suspicion lifecycle itself (states, direct vs transitive,
derivation, auto-clear) is *shared in shape* with OFT's stateless coverage tracer —
now verified hands-on (WP-2). What is ours, exactly (each backed by a spike probe):
(a) the **trigger** is a content-hash *drift* event, not a manual revision bump (OFT
passes a reworded requirement silently, O3a); (b) the **combination of stored and
derived**: SEG keeps content-bound, two-sided edge affirmations *and* derives a
suspicion closure on top — Doorstop stores stamps but derives nothing (one-hop only,
P7), OFT derives everything but stores nothing (no affirmation concept exists, O3b);
and (c) the closure runs over an **evidence subgraph neither tool can represent** —
a test *outcome* has no home in OFT's model at all (O7). Plus the integration with a
global recomputable proof and a user-authored verdict rule set. Claim the *integration
and the verdict/commitment seams*, not the lifecycle in isolation.

## 5. The borrowed substrate (cite, don't claim)

Per-layer canonical formalisms (full refs in `seg_prior_art.md`): typed attributed
graphs (Ehrig et al.); SHACL/ShEx shapes; recursive-SHACL + stratified Datalog
(tractability vindication of DEC-007); commitment schemes — a non-openable scalar set
commitment (`flat-sealed`) vs a Merkle/vector commitment over the set with logarithmic
openings (`flat-openable`); `deep` structure-binding aggregation retired, DEC-012; GSN/CAE/SACM assurance cases (Toulmin root);
assume-guarantee / contract-based design (Benveniste et al.); in-toto/SLSA/Sigstore for
the signing/identity half (and its known actor-authentication gap). **And now: OFT +
Doorstop as the closest *applied* prior art**, plus the traceability lineage (Gotel &
Finkelstein).

## 6. Secondary contributions

- **Soundness reduces to a handful of static invariants** (field-routing totality;
  acyclicity of the `{refines, covers, assumes}` union — with `covers` read in dependency
  orientation R → G, and resting on the satisfaction-role entailment rather than any
  commitment mode (DEC-012/013/017); verdict purity; verdict determinism). The
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
- `seg_demo_clingo_partial_discharge` / `seg_demo_clingo_composition` — the three-state
  proof rollup (total / conditional / unsatisfied) and the composition semantics
  (DEC-015/016/017).
- The three-party SPDX FuSa round-trip (`research/prototypes/spdx-v3.1-exchange/`) —
  producer → supplier → integrator; three BOMs conforming under federated SHACL; the
  seal rejects a dropped assumption and a swapped implementation (DEC-020/028).
- `seg_demo_provenance_polynomial.py` — the provenance triangle
  (`seg_tsf_duality.md` §6.2/§6.8) made runnable: a minimal SEG verdict's
  polynomial built symbolically over ℕ[X], self-checked, then evaluated as
  Boolean verdict / proof count / Viterbi confidence / drift-gated valuation;
  includes the exponent-detects-degenerate-redundancy rule audit. Companion:
  `research/spikes/tsf/t8_clingo_score.lp` (TSF's score calculus as a
  ruleset, exact numeric parity with trudag).
- Six standing clingo gates behind DEC-018…024 (obligation, contract vector, forward ×2,
  compliant-item, conformsTo), each proven verdict-invariant before its decision landed.

## 8. Not yet evidence / claim — be honest

- **OFT & Doorstop are the related-work baseline AND the evaluation target.** Strongest
  framing: "these tools established lightweight, hash/revision-pinned traceability for
  OSS safety projects; SEG asks what they must become to be a *machine-checkable,
  cryptographically-committed, composable* assurance case — a programmable verdict layer,
  a global recomputable proof, and assume-guarantee composition." A comparison/migration
  story (can SEG ingest a Doorstop tree? can it reproduce OFT's coverage as one verdict
  ruleset?) would be a strong evaluation.
- ~~Verify directly: OFT's transitive-break + re-trace-clear semantics~~ **Done**
  (2026-07-04, WP-2 in `seg_tool_landscape.md`): present, whole-chain, two-sided,
  trivially auto-clearing — §2/§4 wording updated accordingly. The comparison also
  yielded two claim-safe bonuses: OFT has *no* extensibility at all while Doorstop's
  only hook is arbitrary Python — SEG's auditable stratified Datalog sits exactly
  between "nothing" and "anything"; and the drift axis has three verified settings
  (one-sided hash / two-sided counter / two-sided hash).
- Composability is **prototyped, not productized**: the round-trip rests on the GAPS
  G1–G12 idealizations — signing/authenticity stubbed (G6), the `forward` affirmation
  idealized (G9 residue), `sha1` a stand-in content-ref (DEC-028) — and the assessor
  certificate (DEC-026) is design-only, with no code path.
- Signed external projection (in-toto/DSSE/Sigstore) still not pressure-tested; DEC-026
  names a transparency-log keystore but nothing is wired.
- No Zephyr-scale evaluation yet (clingo grounding may need Soufflé/Nemo).
- Bibliography entries are stubs pending verification — including the newly grounded
  ones to check verbatim: KAOS (DEC-017 flags it as a conceptual parallel, not a
  confirmed lineage), IEC 61508 compliant item / safety manual (read from secondary
  commentary, DEC-025 honest note), EU CRA "integrator".

## 9. The two-paper plan (venue framings)

Two papers, not one spine with reordered emphasis — the framings diverged as the
exchange work grew. **Priority: Paper 1 (Prague).** ZiSE will not happen; its material
seeds Paper 2 (venue open).

### Paper 1 (priority) — the Prague paper: composition + SPDX exchange
Target: **OSS Summit EU 2026 (Prague)** — the talk plus its backing material; no
proceedings deadline. Builds on the submitted abstract *"A Safety BOM Is a Contract:
Producing and Consuming SPDX Functional Safety Cases"* (2026-06-22). Audience:
cross-project safety, standards / supply-chain literate. Centerpiece = **ecosystem
position + interoperability + composition**, now backed by the round-trip prototype
rather than unverified claims:
- Lead with the **tool-landscape comparison** — five tools plus the RTEMS churn
  study, and the adoption cluster is literally this audience (ELISA, Zephyr,
  Eclipse SDV, space; `seg_tool_comparison.md` §2–§3) — and the redrawn boundary
  (§2–§4). Position SEG per §1a role 2: the **engine behind the tools they already
  run** (integrates with sphinx-needs/StrictDoc, owns only the four missing
  semantics), not a replacement.
- **SPDX 3.x FuSa is the interchange schema; SEG is the engine it lacks** — computes
  verdicts, detects drift, emits the recomputable commitment. The old "SPDX can't model
  safety evidence" line is dead (verified — open thread #8); the honest distinction is
  *recorded* (`EvaluationResult`) vs *recomputed* (SEG's roll-up). SEG projects *to*
  the profile and re-imports downstream.
- **The BOM-is-a-contract story** (§3 claim 3): the `(G, A, I)` opening; the seal that
  breaks on a dropped assumption or a swapped implementation; `conformsTo` → `covers`;
  `forward`ed conditions of use; compliant-item discharge under the version-pin check
  (DEC-017…028). Resonates directly with supply-chain thinking.
- **in-toto / SLSA / Sigstore** signing + transparency-log story; the "recompute-vs-sign"
  question = the known in-toto actor-authentication gap; the assessor certificate over
  `(hash(case), BOM)` (DEC-026) is SEG's design answer.
- Frame the verdict layer as **programmable policy** (maps to their Rego/CUE world), not
  as Datalog semantics.

### Paper 2 (later) — the engine / design-space paper (ex-ZiSE material; venue open)
Centerpiece = **twin contributions**, with vocabulary as the *instrument* behind them:
1. **The facet design space.** Content-addressed evidence graphs decompose into a small
   set of facets — `binds`, `propagates`, `fingerprint ∈ {none, flat-sealed,
   flat-openable; deep retired}`, `acyclic` — that are *orthogonal but
   entailment-linked*. NB the lattice changed under DEC-012/013: the `deep ⟹ acyclic`
   (hard) arrow lost its antecedent; `refines` acyclicity now rests on the
   satisfaction-role (soft) entailment — the clingo two-answer-set result. The axes +
   their dependency structure are the finding.
2. **The projection-core architecture.** One integrity-shaped source; lawful,
   one-directional, *overlapping* derived projections; each layer/facet discharged by a
   different existing engine.

- **Do NOT pitch it as "a common vocabulary"** — a reviewer hears "terminology." The
  glossary is how we *found* the axes; pitch the **design space with named,
  dependency-linked axes**. Vocabulary is the instrument, not the headline. The
  executed tool landscape (WP-1…WP-6) is now the demonstration that the instrument
  discriminates (§1a role 1) — cite the verified spectra as its output.
- **Existing tools = facet-*bundling* points.** Doorstop/OFT aren't merely points in the
  space — they collapse several facets into one switch (the `strong` bundle), which is
  *why* they can't reach regions like programmable verdicts. The `calls` contradiction is
  the existence proof that the bundling is a real limitation, not a style choice.
- **Zephyr = motivating & validating instance, not a dependency.** Large, real,
  safety-targeted, `west`-managed multi-repo — exactly where "evidence over an evolving
  multi-repo graph" gets hard. If an academic venue is chosen, the
  Zephyr-arising-question-that-generalizes shape still applies.
- **Pose open research questions** (academic venues reward these): the
  vocabulary/satisfaction boundary (the `excuses`-generalization tension); is the facet
  set *complete*?; is the three-engine compilation *semantics-preserving*?; must
  projections partition, or is overlap essential — and what soundness property governs
  overlapping derived views?; the per-type facet questions (`witnesses`-binds
  independence).
- **Caution:** present the facet set as the *best decomposition found*, NOT as proven
  complete (known soft spot: the `witnesses`-binds question). Honesty is an asset here.

### Zephyr Developer Summit — practitioner cut (option; draws on either paper's material)
Centerpiece = **concrete workflow + teachable architecture.**
- A real Zephyr tree: requirement ↔ Zephyr test ↔ driver impl; drift when a
  `west`-managed source file is edited; a real safety verdict rule.
- Lead with the **runnable demos**; formal lineage (recursive-SHACL, stratified Datalog)
  is supporting depth, not headline.
- Teaching moments: the prism/projection intuition; the clingo
  determinism-guardrail-trips-on-an-injected-cycle demo (memorable "why acyclicity
  matters").
