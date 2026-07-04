# OFT Spike — Results (fill during execution)

OFT version: 4.5.0 (kit authored against 4.2.0 docs)   Java: OpenJDK 25.0.3   Date: 2026-07-04

| O# | Prediction (short) | Observed (paste status lines) | Verdict | Table-cell impact |
|----|--------------------|-------------------------------|---------|-------------------|
| O0 | baseline imports, all deep-covered | `ok - 6 total`, exit 0 on first run; verbose: all six items green, every wanted type `covered shallow` | CONFIRMED — zero format fixes needed | Kit authored from docs parses on 4.5.0 as-is |
| O1 | deep coverage recursive; defect propagates up | Deleted `[impl->dsn…]` tag ⇒ `not ok dsn (-impl)`; req `not ok` despite own shallow coverage all green (`in: 3/3 ✔`); sys `not ok`; `5 total, 3 defect`, exit 1 | CONFIRMED | Recursive verdict/fixpoint: **PRESENT** (stateless recompute; polarity = coverage, not taint) — the SEG-parity cell |
| O2 | one impl covers req+dsn, native | Baseline green with both tags in one file; no warnings. Nuance: OFT mints one auto-named `impl` item *per tag* (impl~scheduler-lock-…~0 + impl~cooperative-locking-…~0), not one node with two edges | CONFIRMED (+nuance) | Multi-coverage from one source: native, modeled as per-tag artifacts |
| O3a| edit text, keep ~1 ⇒ silent (no content hash) | req text reworded, revision kept ⇒ `ok - 6 total`, exit 0 | CONFIRMED | nodeHash: absent; drift detection = honor-system integer |
| O3b| bump ~2 ⇒ Outdated / Covered Outdated | Bump to ~2, coverers at ~1 ⇒ coverers dual-status `orphaned`+`outdated`; req~2 `outdated coverage` ×3, `-dsn -impl -utest`; **propagates up: sys `not ok`** (deep, despite green shallow); `6 total, 5 defect`, exit 1. Re-trace after fix: instantly `ok`, no clear act, no stored state | CONFIRMED (richer: dual statuses; whole-chain, two-sided) | Transitive break: present, whole-chain, TWO-sided (vs Doorstop parent-only) — but manual-trigger, coverage-polarity; auto-clear trivial by statelessness; **no affirmation concept exists** (nothing stored). Settles paper-seed §8 |
| O4 | impl_violates_adr inexpressible (monotone Needs only) | `oft help`: entire CLI = `trace` + `convert`; only knobs are artifact-type/tag *filters*. No rule, constraint, plugin, or hook facility of any kind (OFT is stricter than Doorstop here — not even an escape hatch) | CONFIRMED | User-definable verdicts: absent; monotone Needs is the only lever |
| O5 | utest = test exists, not run/passed | Baseline green with `utest~scheduler-lock-test~1` declared in tests.md; no run/pass datum exists anywhere in the model | CONFIRMED | Test specification: representable; execution status: no home (→O7) |
| O6 | Status inert (only in aspec XML) | `Status: approved→draft` on dsn ⇒ `ok - 6 total` unchanged; aspec XML shows `<status>draft</status>` on the dsn item (other items default `approved`) | CONFIRMED | Lifecycle status: stored, semantically inert |
| O7 | TestOutcome unrepresentable (no result node) | (i) no result/outcome field in CLI, markdown format, or aspec schema (id/version/doctype/status/desc/coverage only); (ii) a second utest item still only asserts existence; (iii) Status inert (O6). The only path is the CI workaround: emit the coverage tag only on pass — conflates absent with failed, exiles the verdict into pipeline glue | CONFIRMED | Evidence nodes with values: absent; design/evidence split: absent (both tools) |
| O8 | report≠proof; ReqM2 = textual merge only | HTML report: 0 hits for sha256/checksum/signature. `convert -o specobject`: plain ReqM2 XML — items + `providescoverage`/`linksto` with `dstversion` (revision pins DO travel); no hash, no signature, no scope statement | CONFIRMED (+nuance: dstversion travels) | Sealed proof: absent. Composition: partial — a real multi-source exchange format with version pins, but text-only: no content binding, no scope commitment, no assumptions⊆scope check |

## Surprises / format fixes needed (this kit was NOT sandbox-run)
- Ran on OFT 4.5.0 (kit authored against 4.2.0): ZERO format fixes needed — O0 green first try.
- O3b richer than predicted: stale coverers get DUAL statuses (`orphaned` → old id + `outdated` → new id); the break propagates whole-chain including *upward* (sys not ok through deep coverage while its shallow link is green).
- Multi-coverage nuance (O2): OFT mints one auto-named `impl` item per tag, not one impl node with two out-edges.
- ReqM2 `dstversion` (O8): the revision pin survives export — the exchange format carries OFT's (manual) drift anchor.

## Cross-tool synthesis (Doorstop vs OFT vs SEG)
- Recursive verdict: Doorstop **absent** / OFT **present** (deep coverage, stateless, coverage-polarity) / SEG present+user-definable. So SEG's novelty is NOT the fixpoint per se — it is (a) content-bound two-sided affirmation, (b) user-definable stratified semantics, (c) over an evidence subgraph neither tool can represent.
- Drift axis (three settings, clean figure): Doorstop = **one-sided content hash** (parent-only stamp) / OFT = **two-sided manual counter** (silent on content edits; whole-chain on bump) / SEG = **two-sided content hash**.
- Affirmation/state: Doorstop stores stamps (two manual re-affirmation acts; nothing derived) / OFT stores **nothing** (no affirmation concept; everything derived per run, auto-clear trivial) / SEG stores content-bound edge affirmations with suspicion *derived on top* — the only one with both a stored human judgment and a derived closure.
- Design vs evidence subgraph: Doorstop absent / OFT absent (O7: unrepresentable). Likely the §3 headline.
- Extensibility: Doorstop = arbitrary per-item Python plugin (Turing-complete escape hatch) / OFT = none at all / SEG = declarative stratified Datalog. The DEC-007 auditability position sits exactly between "nothing" and "anything".
