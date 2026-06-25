# SEG ↔ SPDX round-trip — GAPS ledger

Idealizations taken to reach a working round-trip fast. Each is a "return-to",
not a solved problem. Recorded so nothing is silently assumed away.

## G1 — No published FuSa JSON-LD context
The FuSa profile is unreleased (develop branch, 3.1 milestone). There is no
canonical `spdx-context.jsonld` carrying the FuSa terms. We generate it from the
`develop` model with `spec-parser -r` and **embed it inline** in the BOM so the
artifact validates offline. Production would reference a published context URL.
Return-to: swap inline context for canonical URL once 3.1 ships.

## G2 — Validation mode is non-obvious (how-to, not a SEG gap)
pyshacl must run with `inference="none"`. rdfs/owlrl materialize `rdf:type
Element` and trip SPDX's abstract-class guard. Recorded so the consumer side and
CI use the same setting.

## G3 — Lossy Assumption round-trip  [LOAD-BEARING]
A SEG residual condition is an ordinary `Requirement`; SPDX models it as a
distinct free-text `Assumption` (`assumptionStatement`). On export we drop the
Requirement typing and stash a hint `comment: "seg:type=requirement"` so the
consumer can reconstruct it. This is fragile (a free-text hint standing in for a
type). It is exactly the "machine-checkable assumptions" proposal to the FuSa
group: an Assumption needs structured, checkable content + a link to the
guarantee it conditions, not just a string. Return-to: open Q2.

## G4 — `refines` direction flips on the wire
SEG `refines` is child→parent; SPDX `tracedToDetail` is parent→refining-child.
Export inverts it; import must invert back. Mechanical but must stay paired.

## G5 — Roll-up verdict is NOT exported (intentional)
The BOM carries records (requirements, assumptions, later: EvaluationResults),
never the rolled-up verdict. The consumer recomputes the verdict in SEG. This is
the thesis ("the verdict engine SPDX lacks"), logged here only so it is explicit.

## G6 — Global commitment is idealized
The `SpdxDocument` carries a single `sha256` Hash via `verifiedUsing`, computed
over the (G, A) content only — NOT a Merkle over the full element set, and NOT
the SEG flat-sealed design root. Authenticity (signing) is stubbed. Return-to:
decide whether the SpdxDocument Hash is an acceptable projection of the SEG
design root (handoff §0 open question) and what it must cover.

## G7 — Evidence layer omitted from the minimal BOM
No `RequirementVerification` / `EvaluationResult` / `EvidenceRelationship` yet.
The contract import (rely on G, discharge A) does not need them. Return-to:
richer BOM pass that projects TestSpecification/TestOutcome → the FuSa evidence
classes (open Q3: can SEG's roll-up project to derived EvaluationResults?).

## G8 — G-subtree collapsed to the guarantee root on import
The BOM carries the full upstream G tree (p_sys refines p_rng). The consumer
reconstructs only the guarantee ROOT (p_sys) as a single `Guarantee` node sealed
under the Manifest; the internal refinement is treated as sealed-inside, not
re-imported as downstream nodes. Defensible (the downstream relies on the
guarantee, not its internals) but it is a choice. Return-to: confirm the
guarantee identity that `covers` should point at is the root, and whether any
multi-guarantee BOM needs >1 Guarantee node.

## G9 — Re-publish of an undischarged inherited assumption  [RESOLVED — DEC-022]
Scenario B: downstream does not discharge the inherited condition and authors a
local re-published condition. Observed: proof_state = UNSATISFIED. The inherited
referenced condition is `unsatisfied`, which poisons the relying requirement via
`unsatisfied(R) :- covers(G,R), assumes(G,C), unsatisfied(C)`; the local
residual cannot offset it. This CONTRADICTS the stated DEC-015 / cbd §9 intent
that an incompletely-discharged downstream proof should be CONDITIONAL by
re-publishing the remainder. The rule set has no "discharge-by-re-publish"
linkage between an inherited referenced condition and a downstream re-published
A_up. Return-to: decide whether (a) this is correct strict semantics (an
inherited assumption you neither satisfy nor formally forward IS a gap), or
(b) DEC-015 requires a new rule letting a re-published condition discharge its
inherited source. This is the sharpest composability-semantics finding so far.

**Resolved (DEC-022) — option (b), with (a) preserved as the guard.** An *affirmed*
`forward` edge re-publishes the inherited condition as a `forwarded` `condition_of_use`:
the relying proof becomes `proof_conditional`, and the remainder re-exports through
`covers` into the integrator's `A_i` (one additive `guards` clause). Option (a) is kept
as the guard, so re-publish cannot launder a gap: a silent drop or an *unaffirmed*
`forward` edge stays `unsatisfied`, and a genuine in-scope gap still dominates
(DEC-015). Deliberateness rides on the affirmation, not the bare edge (the reliance
`seal_ok` shape). Gates: `seg_demo_clingo_forward_v1.py` (5/5 + invariance),
`seg_demo_clingo_forward_export_v1.py` (3/3 + invariance). Standing residue: the
affirmation is idealized (not yet the content-bound anchor), and propagation into
`seg_ruleset` / the demos-of-record / `seg_composability_cbd` / `seg_glossary` is pending.

## G10 — Opening proofs have no SPDX carrier
The flat-openable commitment's inclusion proofs are emitted to a sidecar
(`openings.json`), not inside the SPDX BOM — SPDX carries integrity *hashes*
(member hashes on each Bom, the Merkle root on the SpdxDocument) but has no
field for a vector-commitment inclusion proof. A real cross-org exchange needs
an agreed proof carrier or a small profile extension. Return-to: decide carrier.

## G11 — Surrogate faithfulness (representativeness) not modeled
`surrogate_for` records that a witness-side `environment` stood in for an assumed
condition (QEMU for a compliant HAL) but NOT whether it faithfully represents it.
Representativeness is a witness-validity / tool-qualification concern (ISO 26262-8,
DO-330). Return-to: a validity gate on outcomes produced on a surrogate environment.

## G12 — Cross-component discharge target not carried; integrator invents `covers`  [RESOLVED — DEC-024]
A supplier's BOM declared its contract `C = (m_hal, {m_clk, m_pwr})` but recorded
nothing about which upstream assumption `m_hal` is offered to satisfy, so the
integrator could not derive the reliance edge from data — `consumer.py` hard-coded
`covers(g_m_hal, p_hal)` from a literal; `supplier_bom.jsonld` mentioned `p_hal`
zero times. RESOLVED by DEC-024: a producer-side `conformsTo(G, A_iri)` declaration
(verbatim SPDX Core relationshipType), verdict-inert in the producer, resolved to
`covers` on import by matching the target IRI against an imported assumption's IRI.
The integrator now mints `covers` from data (read-match-mint); the literal is gone.
Note: a `conformsTo` whose `to` is an external (imported) element only satisfies the
SHACL `to sh:class Element` constraint against the FEDERATED graph — validate the
supplier BOM resolved against M (`validate.py supplier_bom.jsonld safety_bom.jsonld`),
which is exactly the graph the integrator holds.
