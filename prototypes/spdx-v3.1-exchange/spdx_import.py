"""
spdx_import.py -- step 5 (consume side): parse an SPDX FuSa safety BOM and
reconstruct the upstream proof as the SEALED structure a downstream SEG project
relies on.

What the consumer reconstructs from the BOM:
  - the upstream guarantee  -> a single `Guarantee` node (the BOM rootElement),
                               referenced_under a Manifest, seal_ok (idealized)
  - each FuSa Assumption    -> a SEG `requirement` (via the G3 seg:type hint),
                               referenced_under the same Manifest, with an
                               `assumes` edge from the Guarantee (the inherited
                               conditions-of-use the downstream must discharge)
  - the design-root Hash    -> recorded; seal authenticity is stubbed (G6)

Modeling choice (logged G8): the internal G refinement subtree (e.g. p_sys
refines p_rng) is NOT re-imported as separate downstream nodes. It is sealed
inside the upstream proof; the downstream references only the guarantee ROOT
identity + the manifest digest. The BOM still carries the full tree for audit.
"""
import json
import re


def _frag(iri):
    return re.split(r"[#/]", iri.rstrip("/"))[-1]


def parse_bom(path):
    doc = json.load(open(path))
    graph = doc["@graph"]
    by_id = {n["spdxId"]: n for n in graph if "spdxId" in n}
    spdxdoc = next(n for n in graph if n["type"] == "SpdxDocument")

    reqs = {n["spdxId"]: n for n in graph if n["type"] == "Requirement"}
    assumptions = {n["spdxId"]: n for n in graph
                   if n["type"] == "functionalsafety_Assumption"}

    root_iris = spdxdoc.get("rootElement", [])
    guarantee_root = root_iris[0] if root_iris else next(iter(reqs))

    design_hash = None
    for vu in spdxdoc.get("verifiedUsing", []):
        if vu.get("type") == "Hash" and vu.get("algorithm") == "sha256":
            design_hash = vu["hashValue"]

    out = {
        "component_iri": spdxdoc["spdxId"],
        "component_name": spdxdoc.get("name", ""),
        "guarantee_root": _frag(guarantee_root),
        "g_members": sorted(_frag(i) for i in reqs),
        "assumptions": [
            {"id": _frag(i),
             "statement": a.get("functionalsafety_assumptionStatement", ""),
             "seg_type_hint": a.get("comment", "")}
            for i, a in assumptions.items()
        ],
        "design_root_hash": design_hash,
    }
    return out


if __name__ == "__main__":
    import sys
    print(json.dumps(parse_bom(sys.argv[1] if len(sys.argv) > 1
                               else "safety_bom.jsonld"), indent=2))
