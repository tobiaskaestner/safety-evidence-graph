# Bundle manifest

Artifacts from this session. All are edited copies produced in the workspace —
move them into the project to adopt, and **discard
`seg_demo_clingo_partial_discharge_v1.py`** (superseded). Confirm DEC numbers
against your authoritative log before writing (the live files were twice found
ahead of expectation this session).

## Files

| File | From → To | What changed |
|---|---|---|
| `seg_decision_log_v7.md` | v6 → v7 | Added **DEC-016** (SHACL/Datalog boundary; test-outcome completeness is a verdict-layer `valid_outcome` check, discard-invalid). |
| `seg_composability_cbd_v7.md` | v6 → v7 | Demo refs repointed to `_v2`; §8 note that v2 realises the DEC-001 universal mode-A and DEC-016 `valid_outcome` (10/10). |
| `seg_demo_clingo_partial_discharge_v2.py` | v1 → v2 | Self-contained three-state verdict demo. Full corrected ruleset (DEC-001 universal mode-A + DEC-016 `valid_outcome`); all five v1 scenarios duplicated + five net-new (universal, waiver, incomplete outcome, enforce-if-present ×2). Runs **10/10**. **Supersedes v1.** |
| `knowledge_graph_design_summary_v6_1.md` | v5_1 → v5_2 → v6 → v6_1 | v5_2: DEC-016 framing (§4.6, §12.2). v6: **DEC-012** (§7 deep → `flat-sealed`; deep retired-not-removed). v6_1: **DEC-013/DEC-014** (v1 keeps the flat-sealed root as seal, no signature; per-node `merkleHash` dropped; configurable `fingerprint` facet → Phase C). |
| `correction-3-handoff-prompt.md` | — | Prompt for a fresh session to decide+apply **Correction 3** (claim-typing + reliance edge direction → DEC-017). |

## Decisions in play
- **DEC-016** — new this session (in the v7 log).
- **DEC-001 universal mode-A** — already in DEC-001; the demo now realises it faithfully (was existential).
- **DEC-012 / DEC-013 / DEC-014** — applied to the design summary (were pending).
- **DEC-017** — reserved for Correction 3 (deferred, see the handoff prompt).

## Known-deferred / out-of-scope here
- **Correction 3** (claim-typing + reliance direction) — deferred; blocks the summary's composability-section reconciliation. See handoff prompt.
- **AC-007 / AC-013 / AC-016** wording (DEC-012/DEC-014 also touch these) live in `seg_architecture_constraints`, a different file — not edited here.
- Demo-name versioning is mixed in the composability doc (`partial_discharge` is `_v2`, `transitive` still referenced unversioned) — a convention pass, not done.
