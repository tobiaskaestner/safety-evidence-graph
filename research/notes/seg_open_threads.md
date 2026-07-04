# SEG — Research Backlog (open threads)

> **The research-stage open-work backlog** — what research is open, why, and where to
> read. Companion: `notes/sessions/SESSIONS.md` tracks *conversations* (which sessions
> exist, how to resume); **this file tracks *work***. Pick one thread, load only the
> doc(s) it points to. Standing caution: every "we're the first to…" claim needs an
> external check before it hardens — verify, then write it down.

**What this is.** A research pickup point — what's open, why, and where to read.
Update it at the end of each research session.

**Document set (for orientation):**
- `notes/seg_glossary.md` — vocabulary (definition pass in progress).
- `research/notes/seg_prior_art.md` — where SEG sits in the literature + bibliography.
- `research/notes/seg_reconciliation.md` — term substitute/explain/novel + tool-leverage map.
- `research/notes/seg_adr_projection_core.md` — the projection-core architecture decision.
- `research/notes/seg_definition_language.md` — grammar, field model, facets, compilation, invariants.
- `research/notes/seg_paper_seed.md` — contribution/novelty material + the venue framings.
- Demos (runnable evidence): `research/prototypes/demos/seg_demo_shacl_projection.py`,
  `seg_demo_datalog_projection.py`, `seg_demo_clingo_verdict.py`.

---

## Open threads (roughly in dependency order)

1. **States & suspicion glossary batch — the NOVEL core.**
   Define `link state` + `active`/`pending`/`suspect`/`broken`, `drift`,
   `suspect-detection seed`, `suspicion` (direct/transitive), `suspicion propagation`,
   `auto-clear`, `derived state`. This is the cluster the reconciliation marked as
   genuinely novel, so it deserves the most careful definitions. We exercised it live
   on clingo, so mechanics are fresh. → continues `seg_glossary.md` (Pending list).

2. **Fold in already-decided glossary terms.**
   From the ADR/definition work: `projection`, `projector`, `projection-core`,
   `write-only projection`, `identity field`, `committed content`, `tracked field`,
   `verdict reproducibility`, `static invariant`, `field routing`. → `seg_glossary.md`.

3. **Definition-language surface syntax.**
   Choose: structured data format (YAML/JSON + schema) vs bespoke grammar. Leaning
   structured-data (avoid owning a parser near the TCB). → `seg_definition_language.md` §8.

4. **`acyclic` on the SHACL side.**
   SHACL-SPARQL vs a dedicated structural pass (core SHACL can't express a global
   no-cycles constraint). → `seg_definition_language.md` §6/§8.

5. **Signed external projection (in-toto / DSSE / Sigstore).**
   The one projection consumer not yet pressure-tested; tied to DEC-010 composability
   and the in-toto actor-authentication gap. → `seg_adr_projection_core.md` §8.

6. **Paper skeleton.**
   Contribution claim is sharpened (the novel core = suspicion lifecycle + its binding
   to the commitment layer; plus the static-invariants-as-trusted-core framing).
   Related-work section can be grown from `seg_prior_art.md`. → new doc when ready.
   **Plan (2026-07-04): two papers.** Priority = **Paper 1, the Prague paper** (OSS
   Summit EU 2026; talk + backing material, no proceedings deadline; builds on the
   submitted *"A Safety BOM Is a Contract"* abstract). ZiSE is off; its facet /
   projection-core material seeds Paper 2 (venue open). The paper seed was reconciled
   the same day: DEC-012/013/014 commitment corrections applied, DEC-015…028 exchange
   results folded in, §9 restructured to the two-paper plan.

7. **Bibliography hardening.**
   All entries are stubs — verify authors/venues/pages/DOIs before submission. Named
   gaps: ShEx primary cite, IEC 61508 + tool-qualification prior art, requirements-
   traceability lineage (Gotel & Finkelstein 1994; CoEST), Verkle trees.
   → `seg_prior_art.md` ("Gaps to fill") + `seg_reconciliation.md` tooling list.

8. **SPDX 3.1-RC1 FunctionalSafety profile — projection target + standards alignment.**
   **Status: largely realized.** The three-party round-trip prototype
   (`research/prototypes/spdx-v3.1-exchange/`) projects to/from the FuSa profile and
   validates under federated SHACL (DEC-020/027/028); the "SPDX can't model safety
   evidence" claim is retired. Remaining SPDX idealizations live in
   `research/notes/GAPS.md` (G1–G12). Still open below: vocabulary alignment + the paper
   sub-claim. Original finding kept for context:
   FINDING: SPDX 3.1-RC1 has a **FunctionalSafety profile** (classes
   `RequirementVerification`, `EvidenceRelationship`, `EvaluationResult`; props
   `verificationMethod`, `evidenceCategory`, `evaluationBasedOn`, …) plus Core
   `Requirement`/`Specification`/`Hash`/`IntegrityMethod`/`verifiedUsing`. So the claim
   "SPDX can't model safety evidence" is DEAD — do not make it.
   REFRAME (the strong story, esp. OSS Summit): SPDX-FunctionalSafety is the standard
   *schema/interchange* for safety-evidence graphs; SEG is the *engine* it lacks —
   computes verdicts, detects drift, and emits a global recomputable commitment.
   They are complementary; SEG projects *to* the profile.
   GAPS to confirm before claiming (read full pages, not the index):
   - the 3 FunctionalSafety class pages + `EvaluationResultType`/`EvidenceType`/
     `VerificationType` vocabularies (does it record verdicts only, or compute? — expect
     record-only);
   - `verifiedUsing` / `IntegrityMethod` / **`PackageVerificationCode`** (the last name
     hints at an aggregate value — check before claiming "no global commitment exists");
   - whether Build/SupplyChain `Process`/`verifiedUsing` machinery covers more than it appears.
   ACTION also: align SEG built-in node/edge vocabulary with the profile's terms where
   they correspond, so the projection is near-trivial and SEG isn't gratuitously
   incompatible. → revises `seg_definition_language.md`; the paper-seed sub-claim is
   applied (2026-07-04): the UNVERIFIED marker is retired and §9 carries the
   verified "SPDX is the schema, SEG the engine" framing.

9. **OSS tool landscape — comparison/categorization WPs (Paper 1 lead-in).**
   Five resumable work packages (Doorstop, OFT, StrictDoc, BASIL, sphinx-needs), one
   per tool, human-driven with agent steering; axes + matrix + findings all in
   → `research/notes/seg_tool_landscape.md` (created 2026-07-04). WP-2 (OFT) carries
   the standing paper-seed §8 suspicion-lifecycle semantics check; supersedes the
   browser-era Doorstop/OFT work packages (never run, not migrated).

## Small confirmations left hanging (cheap; resolve when convenient)
- `Implementation.identity`: `symbol` vs `component_name` (which is stable under file
  moves?). → `seg_definition_language.md` §2.
- Sanity-check `binds`/`propagates` per edge type (e.g. does suspicion really
  propagate along `adheres_to`?). → `seg_definition_language.md` §2.

## Where these decisions now live (was: "decided this session")

The decisions once snapshotted here are durably recorded — and some have since moved
on (e.g. the `fingerprint: deep` choice was **retired**, DEC-012). Authoritative homes:
- node-identity/IRIs, the `tracked` field category, verdict reproducibility, and the
  clingo single-answer-set guardrail → `research/notes/seg_adr_projection_core.md`
  (§5, §8, §10) and `research/notes/seg_definition_language.md` (§3, §6, §7).
- the binding decision record → `notes/decision_log_index.md`.
