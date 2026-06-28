# SEG — CLI migration bundle (generated 2026-06-25)

Self-contained snapshot for continuing the SEG project in a local Claude CLI session.
It merges the **live web-session workspace** with the **project design documents**.

## Layout
```
SPDX-SEG/
  BUNDLE_CONTENTS.md        ← you are here (entry point)
  README.md                 ← environment rebuild + run order
  prototype/                ← all runtime .py + the 6 current gates (co-located: they import each other)
    seg_graph.py seg_ruleset.py seg_composition.py seg_commitment.py seg_graphviz.py
    producer.py supplier.py consumer.py spdx_export.py validate.py
    seg_demo_clingo_{obligation,contract_vector,forward,forward_export,compliant_item,conformsto}_v1.py
    demos/                  ← standalone historical clingo demos (lineage; self-contained)
    examples/               ← *.dsl example graphs
  generated/                ← reproducible outputs (snapshot of last run)
    boms/                   ← *_bom.jsonld + *openings*.json
    graphs/                 ← *.dot / *.svg / *.png renders
  notes/                    ← record + process/meta
    seg_decision_log.md   ← AUTHORITATIVE record (DEC-001 … DEC-028)
    GAPS.md HANDOFF_layerB.md correction-3-handoff-prompt.md seg_spdx_fusa_handoff_v1.md
    seg_open_threads.md seg_reconciliation_v5.md seg_glossary_v5.md MANIFEST.md CLAUDE_v5.md
  design/                   ← architecture, language, summaries
  briefs/                   ← agent briefs (prototype / re / swe / ppt_overview)
  research/                 ← paper seed, prior art, future directions
  skills/                   ← SKILL_v5.md
```

## Start here
- **`notes/seg_decision_log.md`** — the authoritative, citeable record (DEC-001 … DEC-028).
- **`README.md`** — environment rebuild + run order (also reproduced below).

## State as of this bundle
Decisions ratified in the session that produced this bundle:
- **DEC-025** — entity/role vocabulary {manufacturer, assessor, item provider} × {supplier, integrator, verifier}; `auditor` dropped; verification is universal self-verification. (vocabulary only)
- **DEC-026** — assessor certificate = a signature over the pair `(hash(case), BOM)`; safety case and Safety BOM are distinct documents, the case published-or-withheld. (design only; not yet implemented)
- **DEC-027** — explicit SEG node typing in the BOM (`seg:type=guarantee`, read + asserted against `rootElement`); supplier-side `conformsTo`-target typed `assumption`. (gated, verdict-invariant)
- **DEC-028** — implementation pin: each contract member binds the set of implementations in the guarantee's subtree by `sha1` content-ref, projected as `software_File`; swapping an implementation breaks the seal. (gated, verdict-invariant)

Edited runtime modules vs the original `SPDX-SEG_v5_wip` snapshot: `spdx_export.py`, `consumer.py`,
`seg_graph.py`, `producer.py`, `supplier.py`, `seg_composition.py`, `seg_commitment.py`. Last gate
run was green: producer `conditional`; supplier `conditional`, `C[m_hal]={m_clk,m_pwr}`; integrator
A total / B unsatisfied (G9) / C total / D total / E rejected; three BOMs CONFORM under federated
SHACL; six gates pass; pin-swap negative check fails the seal as intended. (Re-verified from this
folder layout.)

## Current vs historical (provenance)
Merge rule: **live workspace + every project document except those a workspace copy supersedes.**
- **Decision log:** only `seg_decision_log_v20.md` kept. Project `v5–v8` superseded; web-session
  intermediates `v16–v19` dropped.
- **Gates of record** are the six `prototype/seg_demo_clingo_*_v1.py`; the verdict ruleset
  (`seg_ruleset.py`) is documented as lifted from `demos/seg_demo_clingo_partial_discharge_v3.py`.
  Everything under `prototype/demos/` is historical lineage — retained, not pruned.
- **Multi-version design docs** retained as-is; latest of each: `design/seg_composability_cbd_v7.md`,
  `design/seg_definition_language_v6.md`, `design/knowledge_graph_design_summary_v6_1.md`. See
  `notes/MANIFEST.md` for the rest.
- **Stale context:** `notes/HANDOFF_layerB.md` and `notes/GAPS.md` predate DEC-025–028 (they describe
  the `v16` era — e.g. G12 closed by DEC-024, the `up_phal` fork resolved by DEC-027). Background only;
  `notes/seg_decision_log_v20.md` is authoritative.
- `generated/` is a snapshot; the pipeline writes fresh outputs into the directory you run from
  (`prototype/`), not into `generated/`.
- `notes/CLAUDE_v5.md` is the prior project context doc — you may want to copy/rename it to a root
  `CLAUDE.md` so Claude Code auto-loads it.

## Environment rebuild (CLI)
1. `pip install clingo rdflib pyshacl` (last verified: clingo 5.8.0, rdflib 7.6.0, pyshacl 0.31.0); graphviz `dot`.
2. Regenerate the FuSa SHACL/context: clone `spdx/spdx-3-model` pinned at **`1c7f1e0`** (2026-06-12) and `spdx/spec-parser`, then
   `python spec-parser/main.py -r -R /tmp/spdx_rdf -f spdx-3-model/model`.
   `validate.py` reads `/tmp/spdx_rdf/spdx-model.ttl`; `spdx_export.py` reads `/tmp/spdx_rdf/spdx-context.jsonld`.
3. **Run from `prototype/`** (paths in README/other docs predate this reorg and are cwd-relative):
   `cd prototype && python producer.py && python spdx_export.py && python supplier.py && python consumer.py`,
   then validate federated: `python validate.py safety_bom.jsonld`;
   `python validate.py supplier_bom.jsonld safety_bom.jsonld`;
   `python validate.py integrator_bom.jsonld safety_bom.jsonld supplier_bom.jsonld`.

## Backlog (carried forward)
- **Carried-open decisions:** mechanize `minted` vs `affirmed` (cosmetic today, not lowered);
  reconcile `forward`-in-core-engine vs DEC-022's "resolves G9" (`forward` lives in the gate demos,
  not `seg_ruleset.py`).
- **Deferred details:** real content-addressing for the pin (git blob/commit sha, `downloadLocation`/`purl`;
  `sha1` is a stand-in); promote the `seg:type` markers from `comment` to an SPDX `Extension`; build the
  serializable safety-case document DEC-026 calls for (the graph has only `to_facts()` + image renders).
- **Apply-steps (doc propagation, not decisions):** fold DEC-025–028 vocabulary into `design/` glossary
  + briefs/summaries; the renderer does not yet draw the impl pin.
