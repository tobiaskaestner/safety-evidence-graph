# SEG Layer B — session handoff (continue here)

Working snapshot: `SPDX-SEG_v5_wip.zip`. Re-upload it next session (the container
filesystem resets; `/mnt/project` is a read-only snapshot that will NOT reflect this
work). Decision log of record: `seg_decision_log_v16.md` (DEC-024 latest).

## Committed and green (the round-trip)
Three-party diamond — upstream **M**, compliant-item supplier **M′** (IEC 61508),
**integrator** — projects each SEG safety case to an SPDX 3.x FuSa BOM and re-imports
downstream. Verified this session:
- All three BOMs CONFORM under **federated** SHACL validation (a cross-document
  `conformsTo` only types up against the imported doc): `safety_bom` alone;
  `supplier_bom + M`; `integrator_bom + M + M′`.
- Six gates pass: obligation, contract_vector, forward (5/5), forward_export (3/3),
  compliant_item (3/3), **conformsto (3/3)**.

## DEC-024 (logged this session, v16): `conformsTo`
- A producer-side declaration that a guarantee is offered to satisfy an upstream
  Assumption (verbatim SPDX Core `RelationshipType`). **Verdict-inert** in the producer;
  resolved to a DEC-017 `covers` on import by **matching the target IRI** against an
  imported assumption's IRI (read-match-mint). Closes GAPS **G12** — the integrator no
  longer hard-codes `covers(g_m_hal, p_hal)`; the `HAL` literal is gone.

## Implemented this session but NOT yet logged (the WIP delta vs v4)
The supplier SEG graph is now the **source of truth** for its upstream provenance:
- `build_supplier()` carries `man_up` (upstream manifest, pinned to M), `up_phal`
  (imported-assumption reference, `iri = …crypto-rng#p_hal`), and a
  `conformsTo(m_hal → up_phal)` edge.
- `spdx_export.py` now **projects** the `import`/`ExternalMap` pin (from manifest nodes
  carrying a root) and the `conformsTo` relationship (from `conformsTo` edges) — they are
  no longer invented at export time from parameters. (`conforms_to` param removed.)
- Renderer additions: `assumption` node type; `conformsTo` edge style; `referenced_under`
  drawn as a light dotted provenance edge (so imports connect to their manifest in every
  graph); **minted vs affirmed `covers`** distinguished — open arrowhead + `(minted)` for
  edges derived from a resolved `conformsTo`, filled + `(affirmed)` for hand-authored
  reliances. `seg_graph.Edge` gained an optional `kind` field (not lowered to clingo).
- Verified verdict-inert: supplier verdict unchanged (`conditional`,
  `C[m_hal]={m_clk,m_pwr}`); all BOMs still CONFORM; conformsto gate still 3/3.

## THE open decision (blocks DEC-025 + a clean v5)
Type of the supplier-side imported-assumption reference node (`up_phal`). Tom asked to
compare against the integrator graph (where imported assumptions are `requirement
[satisfied]` because the integrator *discharges* them) and then deferred. Options:
1. **`assumption`** (SPDX FuSa `Assumption` class, verbatim) — verdict-inert, renders
   neutral, no rule change; BUT a second way to model assumptions, diverging from SEG's
   requirement-convention (G3's `seg:type=requirement`) and from the integrator graph.
2. **`requirement`** (consistent everywhere) — BUT an undischarged referenced requirement
   renders unsatisfied (red), misleading; avoiding red needs a verdict-rule tweak (treat a
   `conformsTo`-only referenced requirement as inert) — an engine change, must be gated.
3. **presentation-only** — keep it `requirement` but exclude `conformsTo`-target refs from
   `to_facts` (never lowered) — inert by construction, but a special-case in lowering.

Current WIP uses option 1 (`assumption`), unratified. Next step: pick 1/2/3 → log DEC-025
→ cut v5.

## Settled understandings (record)
- **Naming across graphs.** Local node ids are re-minted per graph from each BOM's element
  `name`: reconstructed *guarantees* get a `g_` prefix (`m_hal`→`g_m_hal`, `p_sys`→
  `g_p_sys`); *assumptions* keep their name (`p_hal`→`p_hal`). The robust cross-graph key
  is the **SPDX IRI**, not the local id — names round-trip only because `spdx_export`
  writes the producer's local id into `name`. So: `up_phal`(supplier)↔`p_hal`(integrator);
  `m_hal`(supplier)↔`g_m_hal`(integrator); `conformsTo(src,tgt)` → `covers(src,tgt)`,
  source→source / target→target.
- **Drift vs entailment (minted covers).** Drift is fully handled by the dual-end Merkle
  pins + the document-root compatibility check (DEC-023): neither end can silently drift; an
  IRI/root change → no-match (forward-or-fail) or reject. Pinning does NOT check the
  *entailment* (does m_hal actually satisfy p_hal?) — SEG treats guarantee/assumption text
  as opaque. So affirmation was never about drift; it's a **trust-model/policy** choice:
  auto-accept a certified compliant-item supplier's sealed `conformsTo` (minted), or require
  the integrator to endorse the entailment (affirmed). The open/filled arrowhead exposes
  this. Lean: keep visually distinct; let policy — not the engine — decide whether minted
  must be promoted to affirmed.

## Still pending (carried, in rough priority)
1. **DEC-023 honest-note reconciliation** — the note says the SPDX round-trip is "pending";
   it's been real since v3 (import/ExternalMap) and v4 (conformsTo). Amend, or add a
   realization DEC.
2. **Middleware actor role** — second Layer-B role: consumes upstream guarantees, offers its
   own conditional on them, re-publishes residuals via `forward`. Name from CBD/SPDX
   literature, not coined.
3. **Propagation pass** — fold DEC-022/023/024 vocabulary into `seg_glossary`
   (`forward`/`forwarded`/`forward_ok`, `condition_of_use`, compliant-item supplier /
   integrator / compliant-item safety manual, `conformsTo`, and the chosen node-type term)
   and `seg_composability_cbd` §9; reconcile §9's positive-`discharged` stratification sketch
   against the composition grammar's `unsatisfied`-recursion idiom.

## Environment to rebuild next session
- `pip install clingo rdflib pyshacl`; graphviz `dot`.
- Regenerate the FuSa SHACL/context from `spdx/spdx-3-model` `develop` **pinned `1c7f1e0`**
  (2026-06-12) + `spdx/spec-parser`: `python spec-parser/main.py -r -R /tmp/spdx_rdf -f
  /tmp/spdx-3-model/model`. `validate.py` / `spdx_export.py` read `/tmp/spdx_rdf/...`.
- Run order: `producer → spdx_export → supplier → consumer`; validate federated.
