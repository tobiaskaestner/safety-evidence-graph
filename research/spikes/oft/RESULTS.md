# OFT Spike — Results (fill during execution)

OFT version: ______   Java: ______   Date: ______

| O# | Prediction (short) | Observed (paste status lines) | Verdict | Table-cell impact |
|----|--------------------|-------------------------------|---------|-------------------|
| O0 | baseline imports, all deep-covered | | | |
| O1 | deep coverage recursive; defect propagates up | | | |
| O2 | one impl covers req+dsn, native | | | |
| O3a| edit text, keep ~1 ⇒ silent (no content hash) | | | |
| O3b| bump ~2 ⇒ Outdated / Covered Outdated | | | |
| O4 | impl_violates_adr inexpressible (monotone Needs only) | | | |
| O5 | utest = test exists, not run/passed | | | |
| O6 | Status inert (only in aspec XML) | | | |
| O7 | TestOutcome unrepresentable (no result node) | | | |
| O8 | report≠proof; ReqM2 = textual merge only | | | |

## Surprises / format fixes needed (this kit was NOT sandbox-run)
-

## Cross-tool synthesis (Doorstop vs OFT vs SEG)
- Recursive verdict: Doorstop ___ / OFT ___ / SEG present+user-definable
- Drift axis (one-sided hash / two-sided counter / two-sided hash): ___
- Design vs evidence subgraph: Doorstop ___ / OFT ___
