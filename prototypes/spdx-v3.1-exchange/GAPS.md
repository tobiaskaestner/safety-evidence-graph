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

## G9 — Re-publish of an undischarged inherited assumption = hard gap, not conditional  [LOAD-BEARING]
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
