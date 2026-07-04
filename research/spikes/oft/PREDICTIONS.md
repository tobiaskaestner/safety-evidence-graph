# OpenFastTrace Spike — Pre-Registered Predictions (A1)

**IMPORTANT — not sandbox-verified.** Unlike the Doorstop kit (built and run
against Doorstop 3.1), this kit was authored against the **OFT 4.2.0 user
guide**, not executed — the release jar wasn't reachable from the build
environment. So **probe O0 is "does it even import"**, and any format fix you
make is itself a finding worth noting. OFT 4.0+ needs Java 17+.

**The fragment** (same as Doorstop kit; OFT artifact-type mapping):

| SEG node | OFT artifact | SEG edge | OFT mechanism |
|---|---|---|---|
| SYS req | `sys~deterministic-scheduling~1` | — | Needs: req |
| SW req (REQ) | `req~scheduler-lock~1` | refines→SYS | Covers: sys; Needs: dsn,impl,utest |
| ADR | `dsn~cooperative-locking~1` | answers→REQ | Covers: req; Needs: impl |
| IMPL | `[impl->...]` tags in scheduler.c | implements→REQ, adheres_to→ADR | two tags: →req and →dsn |
| TST | `utest~scheduler-lock-test~1` | verifies→REQ | Covers: req |
| **TestOutcome** | **— (no artifact exists) —** | confirms→TST | **see O7** |

**Run:** `./run.sh` (finds `oft` or a local `openfasttrace-*.jar`). It runs
`oft trace -o plain -v failure_details doc/ src/`. Exit code IS the verdict:
0 = all deeply covered. Between destructive probes: `git checkout -- . src/`.

---

## O0 — Import sanity
**Probe.** `./run.sh` on the untouched baseline. Expect exit 0 and a clean
trace: every item deeply covered (sys←req←{dsn,impl,utest}, dsn←impl).
**If it fails to parse**, fix the format and record what was wrong — a finding
about the authoring-format learning curve, and a correction for the paper's
reproducibility.

## O1 — Recursive deep coverage IS present (OFT's strength; SEG-parity cell)
**Prediction (high confidence).** OFT natively computes deep coverage: an item
is deeply covered iff covered for all needed types *and* every covering item is
itself deeply covered — the recursive satisfaction predicate, computed for
free. Remove the `[impl->dsn~cooperative-locking~1]` tag → `dsn` becomes
uncovered → it is not deeply covered → that defect *propagates up*: `req` and
`sys` report not-deeply-covered too.
**Probe.** Delete the dsn tag line in scheduler.c, run, observe propagation.
**Table cell.** Recursive verdict / fixpoint: **PRESENT** (this is where OFT
beats Doorstop and matches SEG's satisfaction closure — note the polarity:
coverage, not taint).

## O2 — Multi-coverage is native (the Doorstop P2 surprise, but first-class)
**Prediction (high confidence).** One impl covering both `req` and `dsn` is
ordinary OFT (the two tags in scheduler.c). No warning. The "multi-parent
wall" that surprised us in Doorstop simply does not exist here.
**Probe.** Confirm baseline shows both coverages as wanted/satisfied.
**Table cell.** Multi-edge from one node: native.

## O3 — Drift detection is by MANUAL REVISION COUNTER, honor-system (headline)
**Prediction A (high confidence).** Edit the *text* of `req~scheduler-lock~1`
WITHOUT changing `~1` → OFT reports nothing; coverage stays green. There is no
content hash; the revision integer is human-maintained. **Silent content
drift.** This is the sharpest OFT cell: it is SEG's edgeHash with the
SHA-256 replaced by an honor-system counter.
**Prediction B (high confidence).** Now bump the id to `req~scheduler-lock~2`
but leave the covering tags/items pointing at `~1` → the covering items report
**Outdated** (outgoing) and `req` reports **Covered Outdated** (incoming).
Drift *is* caught — but only because a human remembered to bump the integer.
**Probe.** (a) edit text only, run; (b) bump revision, run; read statuses.
**Table cell.** nodeHash: **absent**. edgeHash: present-but-degraded to a
manual two-sided revision compare (note: two-sided, unlike Doorstop's
parent-only stamp — but not content-bound).

## O4 — adheres_to enforcement: monotone Needs yes, conditional rule no
**Prediction (MEDIUM confidence — the subtle one).** OFT *can* force "every ADR
must be implemented" via `dsn Needs: impl` (O1 already shows removing the tag
breaks deep coverage). What it **cannot** express is SEG's
`impl_violates_adr` as a *custom predicate with negation* — "an impl that
covers req is in violation IFF some dsn covers req AND that impl does not cover
that dsn." OFT's model is monotone coverage: "needed → must be covered." There
is no rule language, no negation, no way to define a new verdict relation. The
closest OFT encoding (`dsn Needs: impl`) is weaker and structural, not a
verdict you can name, query, or seal.
**Probe.** 20-min user-guide search for any rule/constraint/derived-verdict
facility beyond Needs/Covers/Depends. Do NOT build external Java.
**Table cell.** User-definable verdict semantics: absent (Needs is the only,
monotone, lever).

## O5 — TestSpecification present, but only as "a test exists"
**Prediction (high confidence).** `utest~scheduler-lock-test~1` covering `req`
means exactly "a test artifact exists and claims to cover this requirement."
Deep coverage being green says nothing about whether the test was *run* or
*passed* — only that it is declared.
**Probe.** Confirm baseline is green with the utest present; note that no
pass/fail information exists anywhere in the model.
**Table cell.** Test *specification*: representable. Test *execution status*:
see O7.

## O6 — Status keyword is inert
**Prediction (high confidence; from docs).** `Status: approved` on the dsn item
has no effect on tracing — per the guide it only surfaces in `-o aspec` XML.
Setting it to `draft` will not change the verdict. So OFT has a status field
but no status-gated semantics.
**Probe.** Change dsn Status to `draft`, run, confirm verdict unchanged. Then
try `-o aspec` and confirm status appears only in the XML.
**Table cell.** Lifecycle status: stored, semantically inert.

## O7 — TestOutcome has NO representation (the evidence-subgraph wall)
**The probe that matters most.** In SEG, TestOutcome is an evidence-subgraph
node carrying a value (passed/failed), and the discharge rule reads that value:
`discharged(TS) :- has_confirming_outcome(TS), not some_outcome_fails(TS).`

**Prediction (high confidence).** OFT has **no artifact type for a test
result**. A `utest` is the test's specification/existence, not its outcome.
There is nowhere in the model for "passed/failed" to live, so the discharge
rule is not merely inexpressible (as in Doorstop) — the **data itself is
unrepresentable**. The only path is the CI workaround: emit the `utest`
coverage tag *only when the test passes*, which (a) silently conflates "test
absent" with "test failed," and (b) exiles the verdict into unversioned
pipeline glue — exactly the design/evidence split SEG makes first-class.
**Probe.** Try to model OUT001(pass)/OUT002(fail). Options to attempt and
record why each dead-ends: (i) a `result` keyword — does OFT have one? (no);
(ii) two `utest` items, one per run — they still only express existence;
(iii) Status: on the utest — inert (O6) and not a pass/fail anyway. Conclude:
no representation.
**Table cells.** Evidence nodes with values: **absent**. Design/evidence
split: absent (the axis Doorstop also lacked — confirmed on both tools).

## O8 — Report is not a sealed proof; ReqM2 is import/export, not composition
**Prediction (high confidence, with a nuance worth a cell).** `oft trace`
emits plain/HTML; `oft convert` emits ReqM2 XML. None is a commitment: no hash,
no signature, nothing a third party verifies without trusting your working
tree. **Nuance:** ReqM2 export/import *does* let you merge specs from multiple
sources — so on the composition axis OFT is ahead of Doorstop (it has a
cross-source exchange format) but still short of SEG: ReqM2 is textual merge
with no scope commitment and no assumption-⊆-proven-scope check.
**Probe.** Run `oft trace -o html`; run `oft convert -o specobject` (ReqM2).
Inspect both. Note ReqM2 as partial multi-source input.
**Table cells.** Sealed proof: absent. Composition: partial (textual merge via
ReqM2; no scoped/committed assume-guarantee).

---

## Scoring
Record per probe in `RESULTS.md`: observed status lines (paste OFT output),
verdict (CONFIRMED / REFUTED / SURPRISE), table cell settled. The cross-tool
synthesis to carry into §3:
- **Recursive verdict:** Doorstop absent, OFT **present** → so SEG's novelty is
  *not* the fixpoint per se; it's (a) content-bound two-sided affirmation and
  (b) user-definable stratified semantics over (c) an evidence subgraph OFT
  cannot represent.
- **Drift:** Doorstop = one-sided content hash; OFT = two-sided manual counter;
  SEG = two-sided content hash. The axis has three settings, and the tools sit
  at two different weaker points — a clean figure.
- **Evidence/design split (O7 + Doorstop P11):** absent in both. This is the
  structural reason the discharge rule is inexpressible, and likely the §3
  headline.
