# SEG ↔ SPDX Functional Safety Profile — Exploration Handoff (v1)

**Assembled:** 2026-06-22, just after the OSS Summit EU 2026 abstract *"A Safety BOM Is a Contract: Producing and Consuming SPDX Functional Safety Cases"* was submitted.
**Goal for the fresh session:** explore — more thoroughly than the 1200-char abstract allowed — how SEG relates to the SPDX Functional Safety (FuSa) profile, especially producing/consuming a safety BOM and the "consume a received BOM as a contract" idea.

---

## 0. Status caveats — read first; these bound every claim below
- The FuSa profile is **not in a released SPDX spec**. It lives in the `spdx-3-model` **`develop`** branch and is tracked under the unreleased **3.1** milestone (issues still open). The community (Nicole Pappler / AlektoMetis, ELISA, Zephyr FuSa group) refer to the current state as a "Release Candidate" — that is a community framing, not a frozen spec tag.
- Every SPDX fact below was read directly from the `develop` branch at tip commit **`1c7f1e0` (2026-06-12)**. I did **not** check for an RC tag or open PRs; anything agreed at the June 2026 London meeting may not be merged to `develop` yet.
- **One question left open:** whether SPDX gives any *single recomputable commitment over a whole safety case* vs only per-Element integrity (`verifiedUsing` / `IntegrityMethod`). An `SpdxDocument` is itself an Element and could carry a Hash — so do **not** assert a "global commitment gap" without checking.

---

## 1. What the SPDX FuSa profile actually models (verified, `develop`)
Directory `model/FunctionalSafety/`:
- **Classes:** `Assumption`, `RequirementVerification`, `EvaluationResult`, `EvidenceRelationship`.
- **`EvaluationResult`** — a recorded outcome: `evaluation ∈ {pass, fail, inconclusive}` (required), `evaluationBasedOn` → a `RequirementVerification` (required), required `rationale`. *Added 2025-12-05.*
- **`RequirementVerification`** — the verification *method*: `verificationMethod ∈ {analysis, assessment, audit, demonstration, inspection, review, test, other}`, with free-text `verificationPrecondition` / `verificationPostcondition`.
- **`EvidenceRelationship`** (subclass of `Core/Relationship`) — ties evidence (`evidenceCategory ∈ {report, log, recording, observation, other}`) to results.
- **`Assumption`** — "a constraint associated with an item's use in a system" (i.e. conditions/assumptions of use). Required free-text `assumptionStatement` (xsd:string), optional `assumptionUID`, `rationale`. *Added 2026-04-17.*

Relevant **Core** pieces:
- **`Requirement`** class (Core, added 2025-08-07): required `requirementStatement`, plus `requirementUID`, `rationale`, `devLifecycleStage`.
- **Core relationships** (`Core/Vocabularies/RelationshipType.md`) giving assume-guarantee structure:
  - `assumes`: *the `from` Element assumes each `to` Assumption* (added 2026-04-10)
  - `conformsTo`: *the `from` Element conforms to each `to` Assumption or Specification*
  - `tracedToDetail` (Requirement → refining Requirement ≈ SEG `refines`), `implementedBy` (≈ SEG `implements`), `verifiedBy` (Requirement → RequirementVerification ≈ SEG `verifies`), `hasEvidence`.
- **Validation is two-mechanism:** JSON Schema (structure) + the **SHACL** model (semantics); the OWL ontology embeds SHACL shape restrictions.

**Timeline takeaway:** end-to-end safety-case modelling *including a first-class assumption concept* is only ~2 months old (assumptions: April 2026). That recency is why the consumer-side question is genuinely live.

---

## 2. SEG ↔ SPDX vocabulary correspondence (near 1:1)

| SEG | SPDX FuSa / Core |
|---|---|
| Requirement | Core `Requirement` |
| refines (child→parent) | `tracedToDetail` |
| implements | `implementedBy` |
| TestSpecification / verifies | `RequirementVerification` / `verifiedBy` |
| TestOutcome (pass/fail) | `EvaluationResult.evaluation` (pass/fail/inconclusive) |
| evidence | `EvidenceRelationship` / `hasEvidence` |
| assumes (composition) | `assumes` → `Assumption` |
| (no direct SEG equivalent yet) | `conformsTo` |

---

## 3. The SEG delta — what SEG adds that the profile does not have
The honest distinction is **recorded vs recomputed**, *not* "SPDX has no verdict":
- SPDX `EvaluationResult` is an **asserted, per-verification** outcome (a producer records pass/fail + rationale). There is **no aggregation / roll-up semantics** — nothing derives a *requirement-tree* verdict from leaf outcomes up the `tracedToDetail` DAG. SEG's recursive leaf/non-leaf satisfaction (DEC-001) is exactly that missing computation.
- SEG's verdict is a **deterministic function of committed content**, recomputed (stratified Datalog / clingo), not a stored datum — the property that makes it a *proof* rather than a record.
- **Drift:** SPDX has no notion that a source change *invalidates* a recorded `EvaluationResult`. SEG's staleness/suspect tracking adds this. (NB: SEG v1 recomputes at checkpoints, **not** continuously — DEC-002. Don't claim "continuous monitoring" for the prototype.)
- **Assumptions are free-text strings**, so they can be carried and human-reviewed but not **machine-discharged**. SEG's contract discharge (every sealed `assumes` condition must be discharged — DEC-015) needs assumptions as *checkable conditions linked to the guarantees they constrain*. **This is the concrete, scoped "what the profile could add" message to the FuSa group.**
- **Global commitment** over the whole case as a verdict input vs SPDX per-Element integrity — *open; see §0.*

---

## 4. Open questions worth a thorough session (roughly simplest-first)
1. **Import-as-contract soundness.** A contract = (assumptions, guarantees). SPDX now models both sides. What exactly must hold for SEG to *soundly* import an SPDX safety case as a contract and discharge it? (Tie to DEC-015 residual definition and DEC-010 composability.)
2. **Machine-checkable assumptions.** What minimal structured form would an `Assumption` need beyond `assumptionStatement` to be auto-dischargeable, and how would it link to the guarantee it conditions? (Candidate SPDX proposal.)
3. **Verdict roll-up vs `EvaluationResult`.** Can SEG's roll-up be expressed *as* derived SPDX `EvaluationResult`s, or must it live outside the profile? Where is the projection boundary?
4. **SHACL conformance bridge.** Concretely, how would SEG (a) validate a received SPDX doc against the FuSa SHACL shapes and (b) emit FuSa-conformant output? (SEG's SHACL layer + DSL transpiler are its least-built parts — DEC-007 future.)
5. **Integrity comparison.** Any whole-document commitment in SPDX (SpdxDocument Hash) vs SEG's flat-sealed design root? (§0 caveat.)
6. **Namespace genericity.** SEG's stable global IRIs are a prerequisite for any cross-project / SPDX round-trip (design summary §14; DEC-010 prerequisite).

---

## 5. Sources

### Web — verified this session (`develop` tip `1c7f1e0`, 2026-06-12)
- SPDX 3 model repo: https://github.com/spdx/spdx-3-model
- FuSa profile dir: https://github.com/spdx/spdx-3-model/tree/develop/model/FunctionalSafety
- Assumption: https://github.com/spdx/spdx-3-model/blob/develop/model/FunctionalSafety/Classes/Assumption.md
- EvaluationResult: https://github.com/spdx/spdx-3-model/blob/develop/model/FunctionalSafety/Classes/EvaluationResult.md
- RequirementVerification: https://github.com/spdx/spdx-3-model/blob/develop/model/FunctionalSafety/Classes/RequirementVerification.md
- EvidenceRelationship: https://github.com/spdx/spdx-3-model/blob/develop/model/FunctionalSafety/Classes/EvidenceRelationship.md
- EvaluationResultType vocab: https://github.com/spdx/spdx-3-model/blob/develop/model/FunctionalSafety/Vocabularies/EvaluationResultType.md
- Core Requirement: https://github.com/spdx/spdx-3-model/blob/develop/model/Core/Classes/Requirement.md
- Core RelationshipType (assumes / conformsTo / tracedToDetail / verifiedBy): https://github.com/spdx/spdx-3-model/blob/develop/model/Core/Vocabularies/RelationshipType.md
- Published spec **v3.0.1** (does **not** yet contain FuSa): https://spdx.github.io/spdx-spec/v3.0.1/
- 3.1 milestone tracking FuSa (open issues): https://github.com/spdx/spdx-spec/milestone/4

### Web — leads, NOT re-verified this session (confirm URLs before citing)
- Nicole Pappler (AlektoMetis), "SPDX Safety Profile Release Candidate," ELISA workshop, Munich, ~Nov 2025.
- FOSDEM 2026 talk on the SPDX Safety profile (REQUIREMENT-class framing).

### Project space — use the **highest version present**
- `seg_decision_log_v7.md` — esp. DEC-001 (satisfaction roll-up), DEC-002 (checkpoint refresh), DEC-007, DEC-010 (composability), DEC-015 (residual / discharge).
- `knowledge_graph_design_summary_v6_1.md` — node/edge taxonomy, projection-core, §14 namespace genericity.
- `seg_composability_cbd_v7.md` — assume-guarantee / contract model.
- `seg_paper_seed_v5.md` — §9 SPDX framing. **Note:** its "SPDX can't express…" line is *superseded* by this handoff; treat as outdated.
- `seg_future_directions_research_context_v5.md` — SPDX projection as future work.
- `seg_glossary_v5.md`, `seg_definition_language_v5.md` — authoritative vocabulary (do not coin terms outside these).
- `seg_prior_art_v5.md` — OFT / Doorstop positioning.
- Demos: `seg_demo_clingo_verdict_v5.py`, `seg_demo_shacl_projection_v5.py`, `seg_demo_datalog_projection_v5.py`, `seg_demo_clingo_composition_v2.py`, `seg_demo_clingo_partial_discharge_v2.py`.

---

## 6. Prompt to paste into the fresh session
> I want to explore thoroughly how SEG relates to the SPDX Functional Safety (FuSa) profile — in particular producing and consuming a safety BOM and the "consume a received BOM as a contract" idea (this follows our OSS Summit EU abstract *"A Safety BOM Is a Contract"*).
>
> First read, from the project, the highest-version files: `seg_decision_log_v7.md`, `knowledge_graph_design_summary_v6_1.md`, `seg_composability_cbd_v7.md`, and `seg_paper_seed_v5.md` (§9). Treat the paper seed's "SPDX can't express…" line as superseded.
>
> Context on the SPDX side (verify it yourself against the source — don't trust this summary): the FuSa profile is in the `spdx-3-model` `develop` branch (unreleased 3.1 milestone), not a published spec. As of tip `1c7f1e0` (2026-06-12) it models Requirement (Core) with `tracedToDetail` / `implementedBy` / `verifiedBy`; `RequirementVerification`; `EvaluationResult` (pass/fail/inconclusive); `EvidenceRelationship`; and `Assumption` (free-text `assumptionStatement`) reachable via the Core `assumes` relationship (also `conformsTo`). Validation is JSON Schema + SHACL. Source links are in the handoff doc.
>
> Keep my standing rules: verify before claiming (read the actual model and demo files), prefer the simplest construction that works, flag load-bearing assumptions, don't coin terms, and say "I don't know" rather than guess. Don't restate "SPDX can't" — the honest distinction is *recorded* (SPDX `EvaluationResult`) vs *recomputed* (SEG verdict roll-up). Work iteratively: propose and let me ratify before any document edits.
>
> Start with these open questions, simplest first:
> 1. Import-as-contract soundness — what must hold for SEG to soundly import an SPDX case as a contract and discharge it? (DEC-015, DEC-010)
> 2. Machine-checkable assumptions — minimal structured form for `Assumption` to be auto-dischargeable, and its link to the guarantee it conditions.
> 3. Verdict roll-up vs `EvaluationResult` — can SEG's roll-up project to derived `EvaluationResult`s, or must it stay outside the profile?
> 4. SHACL conformance bridge — how SEG validates against, and emits, FuSa-conformant output.
> 5. Integrity comparison — any whole-document commitment in SPDX vs SEG's flat-sealed design root?
> 6. Namespace genericity — stable global IRIs as a prerequisite for round-trip.
