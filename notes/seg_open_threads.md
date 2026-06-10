# SEG — Open Threads (next-session backlog)

> **START HERE (next session).** Read this file, pick one thread below, then load only
> the doc(s) that thread points to — not all of them. Tell the assistant your working
> style up front (incremental, runnable evidence, push back on weak reasoning). If any
> doc and a fresh chat disagree, trust the doc; if two docs disagree, trust the more
> specific one and flag it. Standing caution for this project: every "we're the first
> to…" claim needs an external check before it hardens — verify, then write it down.

**What this is.** A single pickup point. The detail lives in the per-topic docs;
this file just lists what's open, why, and where to read. Update it at the end of
each session.

**Document set (for orientation):**
- `seg_glossary.md` — vocabulary (definition pass in progress).
- `seg_prior_art.md` — where SEG sits in the literature + bibliography.
- `seg_reconciliation.md` — term substitute/explain/novel + tool-leverage map.
- `seg_adr_projection_core.md` — the projection-core architecture decision.
- `seg_definition_language.md` — grammar, field model, facets, compilation, invariants.
- `seg_paper_seed.md` — contribution/novelty material + the two/three venue framings.
- Demos (runnable evidence): `seg_demo_shacl_projection.py`,
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

7. **Bibliography hardening.**
   All entries are stubs — verify authors/venues/pages/DOIs before submission. Named
   gaps: ShEx primary cite, IEC 61508 + tool-qualification prior art, requirements-
   traceability lineage (Gotel & Finkelstein 1994; CoEST), Verkle trees.
   → `seg_prior_art.md` ("Gaps to fill") + `seg_reconciliation.md` tooling list.

8. **SPDX 3.1-RC1 FunctionalSafety profile — projection target + standards alignment.**
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
   incompatible. → revises `seg_definition_language.md`; new sub-claim in `seg_paper_seed.md`
   §8 (currently marked UNVERIFIED — this thread is that verification).

## Small confirmations left hanging (cheap; resolve when convenient)
- `Implementation.identity`: `symbol` vs `component_name` (which is stable under file
  moves?). → `seg_definition_language.md` §2.
- Sanity-check `binds`/`propagates` per edge type (e.g. does suspicion really
  propagate along `adheres_to`?). → `seg_definition_language.md` §2.

## Decided this session (so we don't re-litigate)
- IRIs for node identity; namespace = per-graph definition param, local part = data;
  identity not hashed.
- `answers_to`, `implements`, `adheres_to` are all `fingerprint: deep` (proof must
  attest the affirmed-against-content pairing).
- Third field category `tracked` (uncommitted, report-only); `status` is tracked.
- Verdicts are sealed/reproducible, not live: no sealed verdict reads a tracked field;
  promotion to `hash_fields` is the sanctioned escape hatch.
- clingo is the prototype verdict engine; single-answer-set determinism guardrail.
