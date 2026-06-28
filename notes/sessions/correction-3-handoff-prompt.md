# Handoff prompt — Correction 3 (next session)

Paste the block below into a new chat. First move this bundle's files into the
project workspace and discard `seg_demo_clingo_partial_discharge_v1.py`, so the
new session reads current state. The session reaches the files by reading their
project paths, not by URL.

---

**Task: decide and apply Correction 3 (claim-typing + reliance edge direction) to the SEG composability model.**

Context: SEG binds requirements/tests/code into a hash-anchored graph; verdicts are computed in stratified Datalog (clingo), structure in SHACL. There is a working three-state verdict (satisfied / conditional / unsatisfied) and a residual/scope layer that is *tested and passing*. Correction 3 is a deferred redesign of how an imported upstream guarantee is modeled.

What Correction 3 proposes, in two linked moves:
1. **Re-type `G_up`** from `requirement` (current: `node(g_up, requirement)`) to a distinct node type (candidate name: `claim`), so the satisfaction engine does not try to decompose/discharge something that is not ours to discharge.
2. **Flip the reliance edge** from outward (`relies_on(R, G_up)`) to flowing *into* R via the witness/`discharges` mechanism (the `discharged_otherwise/1` union), with the upstream claim as a third witness kind alongside test outcomes and design reviews.

Why it is non-trivial (the reason it was deferred): `G_up` typing and `relies_on` direction are load-bearing for rules that already work — `residual(C) :- assumes(G,C), not referenced(G)`, `reliance_seal_ok`/`reliance_uses_ok`, and the `product`/`referenced` scope split. Re-wiring them touches **DEC-015** (residual definition). So this is a re-wire of the conditional-vs-unsatisfied logic, not a rename.

The open question to resolve first: **is edge-direction/typing consistency worth re-touching the tested residual/scope rules, or does the current `relies_on`-into-`requirement` model stay?** Decide this before editing anything.

How I work (please follow):
- Strictly iterative — propose, let me ratify, then edit. No bulk rewrites.
- Record the decision (next free number is **DEC-017**; the log currently tops at DEC-016) *before* documentation edits, so edits cite it.
- Devil's-advocate by default; flag load-bearing assumptions; prefer the smallest solution that works; do not introduce coined terms without asking.
- Prefer a runnable clingo demo against fixtures to validate before doc edits.
- Versioning rule: when you pull a file from the read-only project into your workspace, take its highest version suffix and bump by one; the edited copy must carry a different version number than what you read.

Suggested first step: read the files below, then show me the two models (current vs Correction 3) side by side, listing **exactly which rules change** under Correction 3 and what each does to the residual/scope/three-state behavior.

Relevant files (read these first):
- `seg_composability_cbd_v7.md` — §8 (residual/three-state) and §9 (conservative extension); the import/reliance model lives here.
- `seg_decision_log_v7.md` — DEC-010 (compositional proof), DEC-015 (residual = authored A_up; broken reliance = unsatisfied), DEC-016 (SHACL/Datalog boundary). DEC-017 will be this decision.
- `seg_demo_clingo_partial_discharge_v2.py` — the running three-state verdict + residual/scope rules that Correction 3 would re-wire (`reliance`, `referenced`, `reliance_seal_ok`, `reliance_uses_ok`, `residual`, `product`).
- `seg_demo_clingo_composition_v2.py` — the annotated composition rule-set (mode-2 reliance, `assumes`).
- `seg_example_v1_plus_composition_v1.dsl` — the composition fixture/grammar the demos mirror.
- `knowledge_graph_design_summary_v6_1.md` — once Correction 3 is settled, its stale composability section (old `dependsOn`/imported-requirement model) is the downstream doc to reconcile (deliberately left for after this decision).
- `seg_glossary_v5.md` / `seg_definition_language_v5.md` — check existing terms before naming the new node type; do not coin `claim` (or any name) without confirming against these.
