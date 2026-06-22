"""
spdx_export.py -- project a producer SEG graph into an SPDX 3.x FunctionalSafety
safety-BOM that IS the contract vector under a flat-openable commitment.

Each per-leaf contract C_i = (G_i, {A_ij}) becomes a `Bom` collection:
  - G_i           -> Core Requirement   (the Bom's rootElement)
  - each A_ij     -> FuSa Assumption     (lossy; carries seg:type hint)   [GAPS G3]
  - G_i assumes A -> Relationship assumes (Element -> Assumption)
  - member hash   -> the Bom's verifiedUsing Hash (sha256 over the bundle content)
The SpdxDocument lists the Boms as its rootElement and carries the Merkle ROOT
over the member hashes (DEC-012 flat-openable; the tree itself is tooling-side).

Leaf-keyed (DEC-019): parent requirements and the internal `refines` tree are
NOT exported -- they are sealed inside the producer proof. A shared assumption
(e.g. p_mem) is emitted once (shared IRI) but its content is folded into every
contract's member hash -> double-counted in the commitment, deduped in the graph.

The opening proofs are written to a sidecar (openings.json): SPDX carries the
hashes, not inclusion proofs. See GAPS.
"""
import json
from seg_graph import Graph
from seg_composition import contract_vector
from seg_commitment import member_hash, root, prove

CONTEXT_PATH = "/tmp/spdx_rdf/spdx-context.jsonld"
SPEC_VERSION = "3.0.1"


def _ci(agent_iri):
    return {"type": "CreationInfo", "specVersion": SPEC_VERSION,
            "created": "2026-06-23T00:00:00Z", "createdBy": [agent_iri]}


def contracts_with_text(g: Graph):
    """The contract vector with statements attached: [{id, G:{id,statement}, A:[...]}]."""
    out = []
    for c in contract_vector(g.to_facts())["vector"]:
        out.append({
            "id": "contract-" + c["G"],
            "G": {"id": c["G"], "statement": g.node(c["G"]).fields.get("text", c["G"])},
            "A": [{"id": a, "statement": g.node(a).fields.get("text", a)} for a in c["A"]],
            "I": [{"id": i, "sha1": g.node(i).fields["sha1"]} for i in c["I"]],
        })
    return out


def _members(cs):
    return {c["id"]: member_hash({"G": c["G"], "A": c["A"], "I": c["I"]}) for c in cs}


def pin_from_bom(path) -> dict:
    """Extract the document-root pin {externalSpdxId, root} from a published BOM file.
    This is what a downstream party records to reference THIS document (DEC-023)."""
    bom = json.load(open(path))
    doc = next(n for n in bom["@graph"] if n.get("type") == "SpdxDocument")
    root_hash = next(h["hashValue"] for h in doc["verifiedUsing"]
                     if h.get("algorithm") == "sha256")
    return {"externalSpdxId": doc["spdxId"], "root": root_hash}


def export(g: Graph, embed_context=True, imports=None) -> dict:
    ns = g.namespace
    iri = lambda lid: ns + lid
    agent = iri("agent-seg")
    ci = _ci(agent)
    cs = contracts_with_text(g)
    members = _members(cs)
    mroot = root(members)

    elements = [{"type": "SoftwareAgent", "spdxId": agent, "creationInfo": ci,
                 "name": "SEG projector"}]
    seen = set()
    rel_n = 0

    def emit(node):
        if node["spdxId"] not in seen:
            seen.add(node["spdxId"]); elements.append(node)

    bom_ids = []
    for c in cs:
        gid = iri(c["G"]["id"])
        emit({"type": "Requirement", "spdxId": gid, "creationInfo": ci,
              "name": c["G"]["id"], "requirementStatement": c["G"]["statement"],
              "comment": "seg:type=guarantee"})   # DEC-027: explicit guarantee marker
        member_iris = [gid]
        for a in c["A"]:
            aid = iri(a["id"])
            emit({"type": "functionalsafety_Assumption", "spdxId": aid, "creationInfo": ci,
                  "name": a["id"], "functionalsafety_assumptionStatement": a["statement"],
                  "comment": "seg:type=requirement"})           # G3 reconstruction hint
            member_iris.append(aid)
            rel_n += 1
            emit({"type": "Relationship", "spdxId": iri(f"rel-assumes-{rel_n}"),
                  "creationInfo": ci, "from": gid, "relationshipType": "assumes", "to": [aid]})
        # DEC-028: pin each implementation in the guarantee's subtree as a software_File
        # carrying its content-ref (sha1 stand-in); included in member_iris and in the
        # member hash, so a swapped implementation breaks the inclusion proof.
        for i in c["I"]:
            iid = iri(i["id"])
            emit({"type": "software_File", "spdxId": iid, "creationInfo": ci,
                  "name": i["id"], "comment": "seg:type=implementation",
                  "verifiedUsing": [{"type": "Hash", "algorithm": "sha1",
                                     "hashValue": i["sha1"]}]})
            member_iris.append(iid)
        # the contract bundle (the committed member)
        cid = iri(c["id"])
        bom_ids.append(cid)
        emit({"type": "Bom", "spdxId": cid, "creationInfo": ci, "name": c["id"],
              "profileConformance": ["core", "functionalSafety"],
              "rootElement": [gid], "element": member_iris,
              "verifiedUsing": [{"type": "Hash", "algorithm": "sha256",
                                 "hashValue": members[c["id"]]}]})

    # DEC-024: PROJECT each graph `conformsTo` edge (m_hal -> imported-assumption ref)
    # into an SPDX Core conformsTo Relationship whose `to` is the reference's external
    # IRI. Verdict-inert in the graph; the integrator resolves it to `covers` on import.
    for e in g.edges:
        if e.type == "conformsTo":
            target_iri = g.node(e.dst).fields.get("iri", e.dst)
            rel_n += 1
            emit({"type": "Relationship", "spdxId": iri(f"rel-conformsto-{rel_n}"),
                  "creationInfo": ci, "from": iri(e.src),
                  "relationshipType": "conformsTo", "to": [target_iri]})

    doc = {"type": "SpdxDocument", "spdxId": iri("document"), "creationInfo": ci,
           "name": f"{g.component_name} {g.component_version} safety case",
           "profileConformance": ["core", "functionalSafety"],
           "rootElement": bom_ids,
           "element": [e["spdxId"] for e in elements],
           "verifiedUsing": [{"type": "Hash", "algorithm": "sha256", "hashValue": mroot}]}

    # DEC-023: pin each referenced upstream document by (externalSpdxId, root hash).
    # An ExternalMap is a value object, nested inline like verifiedUsing/Hash.
    # DEC-023/024: PROJECT each sealed upstream manifest carrying a root into an
    # ExternalMap pin (graph as source of truth), merged with any explicit `imports`
    # the caller passes (the integrator, whose manifests carry no root). Deduped by IRI.
    graph_pins = [{"externalSpdxId": n.fields["component_iri"], "root": n.fields["root"]}
                  for n in g.nodes if n.type == "manifest"
                  and "component_iri" in n.fields and "root" in n.fields]
    merged, seen_imp = [], set()
    for im in (imports or []) + graph_pins:
        if im["externalSpdxId"] not in seen_imp:
            seen_imp.add(im["externalSpdxId"]); merged.append(im)
    if merged:
        doc["import"] = [
            {"type": "ExternalMap", "externalSpdxId": im["externalSpdxId"],
             "verifiedUsing": [{"type": "Hash", "algorithm": "sha256",
                                "hashValue": im["root"]}]}
            for im in merged
        ]

    out = {"@graph": [doc] + elements}
    out["@context"] = (json.load(open(CONTEXT_PATH))["@context"] if embed_context
                       else "https://spdx.org/rdf/3.0.1/spdx-context.jsonld")
    return out


def export_openings(g: Graph) -> dict:
    """The producer's opening data: Merkle root + per-contract inclusion proof."""
    cs = contracts_with_text(g)
    members = _members(cs)
    return {"algorithm": "sha256-merkle", "root": root(members),
            "openings": {c["id"]: {"member_hash": members[c["id"]],
                                   "path": prove(members, c["id"])} for c in cs}}


if __name__ == "__main__":
    from producer import build_producer
    g = build_producer()
    bom = export(g)
    with open("safety_bom.jsonld", "w") as f:
        json.dump(bom, f, indent=2, ensure_ascii=False)
    op = export_openings(g)
    with open("openings.json", "w") as f:
        json.dump(op, f, indent=2)

    boms = [n for n in bom["@graph"] if n["type"] == "Bom"]
    print(f"wrote safety_bom.jsonld ({len(bom['@graph'])} nodes), openings.json")
    print(f"  Merkle root: {op['root'][:16]}...  over {len(boms)} contract members")
    for b in boms:
        mem = [e.split('#')[-1] for e in b["element"]]
        print(f"  {b['name']:18} root={b['rootElement'][0].split('#')[-1]:9} "
              f"members={mem}  hash={b['verifiedUsing'][0]['hashValue'][:12]}..")
