# SPDX ↔ SEG safety-BOM round-trip (v4)

A runnable battle-test of "a safety BOM is a contract", across a **three-party
supply chain** (a diamond): an upstream component **M**, a **compliant-item supplier**
**M′** (IEC 61508), and an **integrator** that consumes both and re-publishes its own
safety case. Each party's SEG safety case is projected to an SPDX 3.x FunctionalSafety
(FuSa) JSON-LD BOM as a vector of per-component contracts under a Merkle commitment,
validated against the FuSa SHACL, and re-imported downstream.

Prototype. Idealizations are logged in `GAPS.md` (G9 and G12 resolved). Generated
against the SPDX `spdx-3-model` `develop` tip **`1c7f1e0`** (2026-06-12). Decisions of
record: `seg_decision_log_v16.md` — DEC-018 (obligation), DEC-019 (contract vector),
DEC-020 (SPDX representation + commitment), DEC-021 (witness environment), DEC-022
(`forward` re-publish, G9), DEC-023 (compliant-item-supplier discharge + document-root
compatibility), DEC-024 (`conformsTo` targeting, resolved to `covers` on import, G12).

## The crossing (three parties, a diamond)

```
producer.py  ── M's contract vector ──>  spdx_export.py ─> safety_bom.jsonld (+ openings.json)
                                                                 │
supplier.py  ── M′'s contract ──> spdx_export.py ─> supplier_bom.jsonld
                 │  SpdxDocument.import → ExternalMap pins M's document root (DEC-023)
                 │  conformsTo(m_hal → ⟨M⟩#p_hal): declares which upstream assumption
                 │  m_hal is offered to satisfy (DEC-024)
                 ▼
consumer.py (the INTEGRATOR):
   parse M + M′  →  verify Merkle roots  →  document-root COMPATIBILITY check (DEC-023)
   →  read M′'s conformsTo, MATCH target IRI against M's assumption IRIs,
      MINT covers(g_m_hal, p_hal)  [derived from data, not hard-coded]  (DEC-024)
   →  review the rest  →  recompute verdict (total)
   →  integrator_bom.jsonld  (import-pins BOTH M and M′)
```

The roll-up verdict is never carried in any BOM; each consumer recomputes it (the
thesis). The integrator's reliance edge is **derived**: `conformsTo` is a producer-side
declaration (verdict-inert), resolved to a DEC-017 `covers` only once M′'s guarantee is
imported under the sealed manifest. The **document-root compatibility check** lives at
the verifier; the Datalog layer is blind to version skew.

## Files

| File | Role |
|---|---|
| `seg_ruleset.py` | DEC-001/016/017/018 verdict rule-set (the engine all parties run). |
| `seg_graph.py` | In-memory SEG graph + lowering to clingo facts. |
| `seg_composition.py` | DEC-019 composition: `guarantee`, `desc`, `guards`, structural check; `contract_vector()`. |
| `seg_commitment.py` | DEC-012 flat-openable seal: sha256 Merkle vector commitment. |
| `seg_graphviz.py` | Graphviz renderers (`render` / `render_bom`). |
| `producer.py` | **M** — the upstream crypto-RNG component; computes its contract vector. |
| `supplier.py` | **M′** — the compliant-item supplier (STM32L4 HAL); pins the upstream M (`import`/`ExternalMap`) and declares `conformsTo(m_hal → ⟨M⟩#p_hal)` resolved from M's published assumptions. |
| `spdx_export.py` | Projects a contract vector to SPDX (a `Bom` per contract + Merkle root); emits `import`→`ExternalMap` pins and `conformsTo` relationships; `pin_from_bom()`. |
| `validate.py` | pyshacl against the generated FuSa shapes (`inference="none"`); takes a BOM path plus optional imports to resolve (federated validation for cross-document `conformsTo`). |
| `consumer.py` | The **integrator** — imports M + M′, verifies, runs the document-root compatibility check, **reads `conformsTo` and mints `covers`** for matched targets, reviews the rest, recomputes the verdict, and emits its own BOM pinning M and M′. Scenarios A/B/C kept; D (compatible → total) and E (incompatible → rejected). |
| `seg_demo_clingo_obligation_v1.py` | DEC-018 gate. |
| `seg_demo_clingo_contract_vector_v1.py` | DEC-019 gate. |
| `seg_demo_clingo_forward_v1.py` | DEC-022 G9 verdict-layer gate (5/5). |
| `seg_demo_clingo_forward_export_v1.py` | DEC-022 export-layer gate (3/3). |
| `seg_demo_clingo_compliant_item_v1.py` | DEC-023 compliant-item-supplier + compatibility gate (3/3). |
| `seg_demo_clingo_conformsto_v1.py` | DEC-024 gate (3/3): `conformsTo` inert; matched → mint covers → total; unmatched → forward-or-fail. |
| `seg_decision_log_v16.md`, `GAPS.md` | Decisions of record; idealization ledger. |
| `safety_bom.jsonld` / `openings.json` | M's BOM + opening proofs. |
| `supplier_bom.jsonld` / `supplier_openings.json` | M′'s BOM (pins M, declares `conformsTo`) + openings. |
| `integrator_bom.jsonld` / `integrator_openings.json` | The integrator's BOM (pins M and M′) + openings. |
| `producer_graph.* / supplier_graph.* / bom_graph.* / consumer_graph_A|B|C.* / integrator_graph.*` | Visualizations (SVG + PNG). |

## Reproduce locally (Python 3.12)

```bash
pip install clingo rdflib pyshacl          # clingo 5.8.0, rdflib 7.6.0, pyshacl 0.31.0
# graphviz `dot` for the visualizations (e.g. dnf install graphviz)

# 1. Generate the SPDX FuSa SHACL shapes + JSON-LD context from the develop model
git clone https://github.com/spdx/spdx-3-model.git /tmp/spdx-3-model
git -C /tmp/spdx-3-model checkout 1c7f1e0
git clone https://github.com/spdx/spec-parser.git /tmp/spec-parser
pip install -r /tmp/spec-parser/requirements.txt
python /tmp/spec-parser/main.py -r -R /tmp/spdx_rdf -f /tmp/spdx-3-model/model

# 2. Run the three-party pipeline
python producer.py        # M: 2 root contracts; p_hal in C[p_sys]
python spdx_export.py      # M's BOM + Merkle root -> safety_bom.jsonld, openings.json
python supplier.py         # M′'s BOM, pins M, declares conformsTo -> supplier_bom.jsonld
python consumer.py         # integrator: A/B/C + D (derive covers from conformsTo → total) / E (reject)

# 3. Validate (federated where a BOM references an imported document)
python validate.py safety_bom.jsonld                          # CONFORMS (self-contained)
python validate.py supplier_bom.jsonld safety_bom.jsonld      # CONFORMS (conformsTo target resolves in M)
python validate.py integrator_bom.jsonld safety_bom.jsonld supplier_bom.jsonld   # CONFORMS

# 4. (optional) the model-level gates
python seg_demo_clingo_forward_v1.py            # DEC-022 (5/5)
python seg_demo_clingo_forward_export_v1.py     # DEC-022 export (3/3)
python seg_demo_clingo_compliant_item_v1.py     # DEC-023 (3/3)
python seg_demo_clingo_conformsto_v1.py         # DEC-024 (3/3)
```

`validate.py` / `spdx_export.py` reference `/tmp/spdx_rdf/...` (`SHAPES`, `CONTEXT_PATH`);
edit if you generate the shapes elsewhere. A `conformsTo` whose `to` is an external
(imported) element only satisfies the SHACL `to sh:class Element` constraint against the
federated graph, hence the resolved imports on the `supplier_bom` / `integrator_bom`
validation lines.
