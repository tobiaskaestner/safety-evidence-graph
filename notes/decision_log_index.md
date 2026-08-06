# SEG Decision Log — Master Index

The SEG decision log is split into two stage-slices (pipeline migration, 2026-06-27).
**DEC-IDs are globally unique and stable** — cite `DEC-0NN` regardless of which slice
holds it. This index is the cross-cutting map.

- **Development slice** → [`development/notes/decision_log.md`](../development/notes/decision_log.md) — core-engine decisions.
- **Research slice** → [`research/notes/decision_log.md`](../research/notes/decision_log.md) — composability/SPDX + directions.
- **DEC-003 is split** across both slices: the language-agnostic hashing *principle* → research; the Python/marker *binding* → development.
- **DEC-011 is intentionally vacant** — the projection-core ADR, [`research/notes/seg_adr_projection_core.md`](../research/notes/seg_adr_projection_core.md).

| DEC | Slice | Summary |
|---|---|---|
| 001 | dev | Hierarchical requirement coverage by transitive closure (leaf/non-leaf satisfaction) |
| 002 | dev | Single repo, four branches as worktrees; integrity-vs-safety trust boundary |
| 003 (principle) | research | Raw-byte hashing, parser-as-locator (language-agnostic) |
| 003 (binding) | dev | Python node + marker dialect (docstring-field markers) |
| 004 | dev | Engine ownership; build-sequencing bootstrap; agents never affirm |
| 005 | dev | Transitive suspicion is derived; auto-clears on descendant re-affirmation |
| 006 | dev | Capture the affirmation anchor now; defer the diff feature |
| 007 | research | Graph-type meta-model & configurable satisfaction (stratified Datalog); v1 seams |
| 008 | research | Additional interfaces (REST) future; engine-as-library now |
| 009 | research | Configurable repo topology (source-binding facet of the meta-model) |
| 010 | research | Compositional (assume-guarantee) proof |
| 011 | *(vacant)* | Projection-core ADR — `research/notes/seg_adr_projection_core.md` |
| 012 | research | Retire `deep` fingerprint; flat set-commitment; `flat-openable` reserved |
| 013 | research | v1 drops the global commitment layer *(superseded by 014)* |
| 014 | research | v1 keeps a `flat-sealed` design root *(supersedes 013's removal clause)* |
| 015 | research | `residual` = product's authored `A_up`; a broken reliance is `unsatisfied` |
| 016 | research | SHACL/Datalog responsibility boundary; outcome completeness is a verdict check |
| 017 | research | Re-type imported guarantee to `Guarantee`; reliance edge becomes `covers` |
| 018 | research | `obligation` node-state, distinct from structural `residual` |
| 019 | research | Per-component contract vector; `A_i` = obligation down-closure |
| 020 | research | SPDX representation + `flat-openable` commitment for the contract vector |
| 021 | research | `environment` + `surrogate_for`/`ran_on`; surrogacy is not a discharge |
| 022 | research | `forward` re-publishes an undischarged inherited condition (resolves G9) |
| 023 | research | Compliant-item-supplier discharge; document-root (version-pin) check |
| 024 | research | `conformsTo` producer declaration, resolved to `covers` on import (closes G12) |
| 025 | research | Entity/role vocabulary; `auditor` dropped; universal self-verification |
| 026 | research | Assessor certificate = signature over `(hash(case), BOM)`; case ≠ Safety BOM |
| 027 | research | Explicit SEG node typing in the BOM (`seg:type=guarantee`) |
| 028 | research | Implementation pin folded into the contract member (`sha1` stand-in) |
| 029 | research | Project name: **affirmatrix**; "SEG/safety evidence graph" stays the artifact term |
| 030 | dev | Affirmatrix repo = mono-repo (orphan branch `tool`); four-branch topology demoted to conformance fixture (refines 002) |
| 031 | research | Canonical content form — extractor-produced reproducible IRs admissible as hash substrate (refines 003 principle) |
| 032 | dev | Test markers split identity from relation: `:test-id: SEG-TS-nnn` beside `:verifies: SEG-SREQ-nnn` (refines 003 Python binding) |

## Supersession & cross-stream links

- **012 → 013 → 014** (commitment layer): 012 supersedes the v4.1 §7 deep-Merkle design
  and refines the DEC-007 `fingerprint` facet; 013 superseded 012's v1-scope clause; 014
  supersedes 013's removal clause (v1 keeps a `flat-sealed` root).
- **017** refines **010 + 015** and retires the `relies_on` form.
- **031** refines **003 (principle)**: canonical content form generalizes the raw-byte-span
  rule to admit deterministic, source-reproducible extractor exports (e.g. `needs.json`).
- **032** refines **003 (Python binding)**: adds `:test-id:` so a test states the
  specification it realizes, and restores `:verifies:` to the requirement target DEC-003
  named — the agent briefs had drifted to `:verifies: SEG-TS-nnn`.
- **022** resolves GAPS **G9** (builds on 010/015/017/018/019); **024** closes GAPS **G12**.
- **Cross-stream:** **010** (research) extends **001** (development) with a third discharge
  case (satisfied-by-external-proof) — the one citation that crosses the two slices.
- **AC footprints** (binding form in `development/design/seg_architecture_constraints.md`):
  003(principle)→AC-004 · 007→AC-001/002/011/013 · 008→AC-014 · 009→AC-015 · 010→AC-016.
