# SPDX ↔ SEG safety-BOM round-trip (v1)

A minimal, runnable battle-test of the "a safety BOM is a contract" idea: a SEG
safety case is computed, projected to an SPDX 3.x FunctionalSafety (FuSa) JSON-LD
BOM, validated against the FuSa SHACL shapes, and re-imported into a *separate*
downstream SEG project that recomputes a verdict over it.

Status: prototype. Several parts are deliberately idealized — see `GAPS.md`.
Generated against the SPDX `spdx-3-model` `develop` tip **`1c7f1e0`** (2026-06-12).

## The crossing

```
producer.py  --(G,A) contract-->  spdx_export.py  -->  safety_bom.jsonld
                                                            |
                                                       validate.py  (pyshacl, FuSa SHACL)
                                                            |
                                          spdx_import.py  <-- safety_bom.jsonld
                                                            |
                                                       consumer.py  (covers-reliance, verdict)
```

The verdict roll-up is NOT carried in the BOM; it is recomputed in SEG on import
(the thesis: SEG is the verdict engine the SPDX profile lacks). See GAPS G5.

## Files

| File | Role |
|---|---|
| `seg_ruleset.py` | The SEG stratified-Datalog verdict ruleset, lifted verbatim from `seg_demo_clingo_partial_discharge_v3.py` (DEC-001/016/017). The single engine both sides run. |
| `seg_graph.py` | Minimal in-memory SEG graph (`Node`/`Edge`/`Graph`) + lowering to clingo facts. |
| `producer.py` | Synthesizes a conditional crypto-RNG safety case, runs the verdict, extracts the (G, A) contract. |
| `spdx_export.py` | Projects the contract to a minimal SPDX 3.x FuSa JSON-LD BOM (Requirements + Assumption + reified relationships + a `sha256` design-root on the `SpdxDocument`). |
| `validate.py` | Runs pyshacl against the generated FuSa SHACL shapes (`inference="none"`). |
| `spdx_import.py` | Parses a BOM back into the upstream sealed structure (Guarantee + referenced conditions + manifest seal). |
| `consumer.py` | Downstream project relies on the imported guarantee via `covers`, re-runs the verdict (scenario A → total, scenario B → the G9 stress). |
| `GAPS.md` | Ledger of 9 logged idealizations to return to. |
| `safety_bom.jsonld` | The generated artifact (output of `spdx_export.py`); included so the import side runs without regenerating. |

## Reproduce locally (Fedora, Python 3.12)

```bash
pip install clingo rdflib pyshacl     # used: clingo 5.8.0, rdflib 7.6.0, pyshacl 0.31.0

# 1. Generate the SPDX FuSa SHACL shapes + JSON-LD context from the develop model
git clone https://github.com/spdx/spdx-3-model.git /tmp/spdx-3-model
git -C /tmp/spdx-3-model checkout 1c7f1e0          # pin the exact tip
git clone https://github.com/spdx/spec-parser.git /tmp/spec-parser
pip install -r /tmp/spec-parser/requirements.txt   # Jinja2, jsonpickle, rdflib
python /tmp/spec-parser/main.py -r -R /tmp/spdx_rdf -f /tmp/spdx-3-model/model
#  -> produces /tmp/spdx_rdf/spdx-model.ttl  and  /tmp/spdx_rdf/spdx-context.jsonld

# 2. Run the pipeline (from the folder holding the .py files)
python producer.py        # conditional verdict, G={p_sys,p_rng}, A={p_entropy}
python spdx_export.py     # writes safety_bom.jsonld
python validate.py        # CONFORMS
python consumer.py        # A -> total ; B -> unsatisfied (G9)
```

### Environment coupling

`validate.py` and `spdx_export.py` hardcode two paths — `SHAPES` and
`CONTEXT_PATH`, both under `/tmp/spdx_rdf/`. If you generate the shapes
elsewhere, edit those two constants. Everything else is self-contained.

### Validation note (not a SEG gap, but easy to trip on)

pyshacl must run with `inference="none"`. Turning on rdfs/owlrl materializes
`rdf:type Element` onto every instance and trips SPDX's "Element is an abstract
class, do not instantiate directly" guard with false positives. The Element-level
constraints (e.g. `creationInfo`) still fire on subclasses because pyshacl's
targetClass selection is subclass-aware via the ontology graph — confirmed by
negative probe.
