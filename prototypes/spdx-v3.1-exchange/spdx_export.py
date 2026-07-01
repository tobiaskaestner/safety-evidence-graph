"""
spdx_export.py -- step 3: project a producer SEG graph + its (G, A) contract
into a MINIMAL SPDX 3.x FunctionalSafety safety-BOM (JSON-LD).

Minimal contract BOM (Occam): SpdxDocument + Requirements (G) + Assumptions (A)
+ the reified relationships (tracedToDetail, assumes). The evidence layer
(RequirementVerification / EvaluationResult / EvidenceRelationship) is a later,
richer pass and is NOT needed to import the contract.

Mapping (verified against generated SHACL, develop tip):
  SEG Requirement (in G)      -> Core Requirement            (requirementStatement)
  SEG residual condition (A)  -> FuSa Assumption             (assumptionStatement)   [LOSSY]
  SEG refines (child->parent) -> Relationship tracedToDetail (parent->child)         [DIR FLIP]
  SEG assumes (G->C)          -> Relationship assumes        (Element->Assumption)
  whole case                  -> SpdxDocument + sha256 Hash via verifiedUsing        [IDEALIZED]

The roll-up verdict is deliberately NOT exported (it is recomputed in SEG on
import -- the thesis). See GAPS.md.
"""
import json
import hashlib
from seg_graph import Graph

CONTEXT_PATH = "/tmp/spdx_rdf/spdx-context.jsonld"
SPEC_VERSION = "3.0.1"


def _ci(agent_iri):
    return {
        "type": "CreationInfo",
        "specVersion": SPEC_VERSION,
        "created": "2026-06-23T00:00:00Z",
        "createdBy": [agent_iri],
    }


def _design_root_hash(g: Graph, contract) -> str:
    """Idealized flat commitment: sha256 over the canonical (G, A) content."""
    payload = {
        "G": [(r, g.node(r).fields.get("text", "")) for r in contract["G_discharged"]],
        "A": [(c, g.node(c).fields.get("text", "")) for c in contract["A_residual"]],
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def export(g: Graph, contract, embed_context=True) -> dict:
    ns = g.namespace
    iri = lambda lid: ns + lid
    agent = iri("agent-seg")
    ci = _ci(agent)
    elements = []

    # bootstrap Agent (so CreationInfo.createdBy -> Agent resolves to a typed node)
    elements.append({
        "type": "SoftwareAgent", "spdxId": agent,
        "creationInfo": ci, "name": "SEG projector",
    })

    g_ids, a_ids = contract["G_discharged"], contract["A_residual"]

    for rid in g_ids:                          # G -> Core Requirement
        n = g.node(rid)
        elements.append({
            "type": "Requirement", "spdxId": iri(rid), "creationInfo": ci,
            "name": rid, "requirementStatement": n.fields.get("text", rid),
        })
    for cid in a_ids:                          # A -> FuSa Assumption (lossy)
        n = g.node(cid)
        elements.append({
            "type": "functionalsafety_Assumption", "spdxId": iri(cid), "creationInfo": ci,
            "name": cid, "functionalsafety_assumptionStatement": n.fields.get("text", cid),
            # carry the SEG identity so the consumer can reconstruct it as a Requirement
            "comment": "seg:type=requirement",
        })

    # reified relationships
    rel_n = 0
    def add_rel(src, rtype, dsts):
        nonlocal rel_n
        rel_n += 1
        elements.append({
            "type": "Relationship", "spdxId": iri(f"rel-{rtype}-{rel_n}"),
            "creationInfo": ci, "from": iri(src),
            "relationshipType": rtype, "to": [iri(d) for d in dsts],
        })

    g_set, a_set = set(g_ids), set(a_ids)
    for e in g.edges:
        if e.type == "refines" and e.src in g_set and e.dst in g_set:
            add_rel(e.dst, "tracedToDetail", [e.src])      # parent -> child (flip)
        elif e.type == "assumes" and e.dst in a_set:
            add_rel(e.src, "assumes", [e.dst])             # Element -> Assumption

    # SpdxDocument with the idealized design-root commitment
    root_hash = _design_root_hash(g, contract)
    doc = {
        "type": "SpdxDocument", "spdxId": iri("document"), "creationInfo": ci,
        "name": f"{g.component_name} {g.component_version} safety case",
        "profileConformance": ["core", "functionalSafety"],
        "rootElement": [iri(r) for r in g_ids if not any(
            ed.type == "refines" and ed.src == r for ed in g.edges)],  # top requirements
        "element": [el["spdxId"] for el in elements],
        "verifiedUsing": [{"type": "Hash", "algorithm": "sha256", "hashValue": root_hash}],
    }
    graph_nodes = [doc] + elements

    out = {"@graph": graph_nodes}
    if embed_context:
        out["@context"] = json.load(open(CONTEXT_PATH))["@context"]
    else:
        out["@context"] = "https://spdx.org/rdf/3.0.1/spdx-context.jsonld"
    return out


if __name__ == "__main__":
    from producer import build_producer, verdict_and_contract
    g = build_producer()
    contract = verdict_and_contract(g)["contract"]
    bom = export(g, contract)
    with open("safety_bom.jsonld", "w") as f:
        json.dump(bom, f, indent=2, ensure_ascii=False)
    n = len(bom["@graph"])
    print(f"wrote safety_bom.jsonld  ({n} graph nodes)")
    print("  design-root sha256:", bom["@graph"][0]["verifiedUsing"][0]["hashValue"][:16], "...")
