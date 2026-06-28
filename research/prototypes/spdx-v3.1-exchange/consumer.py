"""
consumer.py -- consume a VECTORIZED SPDX FuSa safety-BOM (the contract vector
under a flat-openable commitment).

  1. parse the BOM -> contracts {C_i=(G_i,{A_ij})}, member hashes, Merkle root
  2. OPEN a chosen subset and VERIFY each against the root (openings.json);
     a tampered bundle (dropped assumption) fails.
  3. RECONSTRUCT verified contracts into a downstream SEG graph: G_i -> Guarantee
     under a seal_ok Manifest; A_ij -> requirement conditions referenced under it
     (shared conditions deduped, one assumes edge per importing guarantee).
  4. a downstream product relies via `covers`; discharge inherited conditions by
     review; run the verdict. Builds a seg_graph.Graph so the scenario renders.
"""
import json
import re
from lib.seg_graph import Graph, Node, Edge, impl_sha1
from lib.seg_ruleset import solve
from lib.seg_commitment import member_hash, verify
from lib.seg_composition import contract_vector
from spdx_export import export, export_openings, pin_from_bom
from producer import node_states
from lib.seg_graphviz import render

_frag = lambda iri: re.split(r"[#/]", iri.rstrip("/"))[-1]
MAN = "man_up"


def _seg_type(node):
    """DEC-027: the explicit SEG node type carried in a BOM element's comment."""
    m = re.search(r"seg:type=(\w+)", node.get("comment", "") or "")
    return m.group(1) if m else None


def parse_vector_bom(path):
    bom = json.load(open(path)); g = bom["@graph"]
    by_id = {n["spdxId"]: n for n in g if "spdxId" in n}
    doc = next(n for n in g if n["type"] == "SpdxDocument")
    root = next(h["hashValue"] for h in doc["verifiedUsing"] if h.get("algorithm") == "sha256")
    contracts = []
    for b in g:
        if b.get("type") != "Bom":
            continue
        gid = b["rootElement"][0]
        # DEC-027: SEG type is READ from the explicit seg:type marker and ASSERTED
        # against structural position (rootElement => guarantee; members => requirement).
        assert _seg_type(by_id[gid]) == "guarantee", \
            f"rootElement {gid}: seg:type={_seg_type(by_id[gid])}, expected guarantee"
        for e in b["element"]:
            if e != gid and by_id[e].get("type") == "functionalsafety_Assumption":
                assert _seg_type(by_id[e]) == "requirement", \
                    f"member {e}: seg:type={_seg_type(by_id[e])}, expected requirement"
        a = [{"id": _frag(e), "statement": by_id[e]["functionalsafety_assumptionStatement"]}
             for e in b["element"] if e != gid
             and by_id[e]["type"] == "functionalsafety_Assumption"]
        # DEC-028: implementation pins carried as software_File elements
        imp = [{"id": by_id[e]["name"],
                "sha1": next(h["hashValue"] for h in by_id[e]["verifiedUsing"]
                             if h.get("algorithm") == "sha1")}
               for e in b["element"] if by_id[e].get("type") == "software_File"]
        contracts.append({
            "id": _frag(b["spdxId"]),
            "G": {"id": _frag(gid), "statement": by_id[gid]["requirementStatement"]}, "A": a,
            "I": imp,
            "member_hash": next(h["hashValue"] for h in b["verifiedUsing"]
                                if h.get("algorithm") == "sha256")})
    return {"root": root, "component_iri": doc["spdxId"], "contracts": contracts}


def verify_contract(c, openings, root):
    if member_hash({"G": c["G"], "A": c["A"], "I": c.get("I", [])}) != c["member_hash"]:
        return False, "member hash mismatch (bundle altered)"
    o = openings["openings"].get(c["id"])
    if not o:
        return False, "no opening proof supplied"
    if not verify(c["member_hash"], [tuple(p) for p in o["path"]], root):
        return False, "inclusion proof fails against root"
    return True, "verified"


def build_graph(parsed, open_ids, discharge):
    """Reconstruct opened contracts + the downstream's OWN requirement tree."""
    opened = [c for c in parsed["contracts"] if c["id"] in open_ids]
    g = Graph("https://example.org/downstream#", "https://example.org/downstream",
              "downstream consumer", "1.0.0")
    g.nodes.append(Node(MAN, "manifest", {"component_iri": parsed["component_iri"]}))
    g.seal_ok.append(MAN)
    g.nodes.append(Node("d_impl", "implementation", {}))
    g.edges.append(Edge("du", "uses", "d_impl", MAN))
    # the downstream project's own requirement tree (its product)
    g.nodes.append(Node("d_sys", "requirement", {"text": "Downstream secure-boot subsystem"}))
    conds, rel = set(), 0
    for k, c in enumerate(opened):
        gn = "g_" + c["G"]["id"]
        g.nodes.append(Node(gn, "guarantee", {}))
        g.referenced_under[gn] = MAN
        # a downstream requirement of its own, discharged by relying on the import
        drq = f"d_req_{k}"
        g.nodes.append(Node(drq, "requirement",
                            {"text": f"downstream need met by relying on {c['G']['id']}"}))
        g.edges.append(Edge(f"df_{k}", "refines", drq, "d_sys"))   # under the downstream root
        g.edges.append(Edge(f"dc_{k}", "covers", gn, drq))          # imported guarantee covers it
        for a in c["A"]:
            cid = a["id"]
            if cid not in conds:
                g.nodes.append(Node(cid, "requirement", {"text": a["statement"]}))
                g.referenced_under[cid] = MAN
                conds.add(cid)
            rel += 1
            g.edges.append(Edge(f"ea_{rel}", "assumes", gn, cid))   # one per importer
    for j, cid in enumerate(sorted(discharge)):
        g.nodes.append(Node(f"dr_{j}", "designreview", {}))
        g.edges.append(Edge(f"drv_{j}", "reviews", f"dr_{j}", cid))
    # a downstream requirement satisfied the usual way (its own TestSpec+Outcome+Impl),
    # sibling to the reliance-discharged ones under d_sys
    g.nodes += [
        Node("d_own", "requirement", {"text": "downstream requirement met by its own implementation"}),
        Node("d_ts", "testspecification", {}),
        Node("d_im2", "implementation", {"body": "d_own_impl.c", "sha1": impl_sha1("d_own_impl.c")}),
        Node("d_to", "testoutcome", {"outcome": "PASS"}),
    ]
    g.edges += [
        Edge("dfo", "refines", "d_own", "d_sys"),
        Edge("dvo", "verifies", "d_ts", "d_own"),
        Edge("dio", "implements", "d_im2", "d_own"),
        Edge("dco", "confirms", "d_to", "d_ts"),
        Edge("dwo", "witnesses", "d_to", "d_im2"),
    ]
    return g, sorted(conds)


def run(parsed, open_ids, discharge, label, render_path=None):
    g, conds = build_graph(parsed, open_ids, discharge)
    m = solve(g.to_facts())[0]
    state = ("total" if "proof_total" in m else "conditional" if "proof_conditional" in m
             else "unsatisfied" if "proof_unsatisfied" in m else "??")
    uns = sorted(a[len("unsatisfied("):-1] for a in m if a.startswith("unsatisfied("))
    print(f"\n[{label}]  opened={sorted(open_ids)}  conditions={conds}")
    print(f"   discharged={sorted(discharge)}   proof={state}   unsatisfied={uns or '(none)'}")
    if render_path:
        render(g, states=node_states(g), title=f"Consumer graph - {label}",
               path=render_path, fmt="svg")
        render(g, states=node_states(g), title=f"Consumer graph - {label}",
               path=render_path, fmt="png")
    return state


# ---------------------------------------------------------------------------
# DEC-023: compliant-item-supplier discharge over TWO imported BOMs, gated by
# the document-root compatibility (diamond co-reference / version-pin) check.
# ---------------------------------------------------------------------------
def conformsto_of_bom(path):
    """conformsTo declarations on a BOM: [(from_iri, to_iri)] (DEC-024)."""
    bom = json.load(open(path))
    out = []
    for n in bom["@graph"]:
        if n.get("type") == "Relationship" and n.get("relationshipType") == "conformsTo":
            out += [(n["from"], t) for t in n.get("to", [])]
    return out


def assumption_iris(path):
    """{spdxId: name} for every FuSa Assumption in a BOM (the match keys)."""
    bom = json.load(open(path))
    return {n["spdxId"]: n["name"] for n in bom["@graph"]
            if n.get("type") == "functionalsafety_Assumption"}


def resolve_covered(conformsto, upstream_assumption_iris):
    """read-match (DEC-024): the upstream assumption NAMES whose IRI a supplier
    conformsTo declaration targets -- i.e. the inherited assumptions M' discharges.
    The integrator mints `covers` for exactly these; an unmatched target mints none."""
    return sorted({upstream_assumption_iris[to] for (_frm, to) in conformsto
                   if to in upstream_assumption_iris})


def imports_of_bom(path):
    """Declared upstream document-root pins on a BOM: [{externalSpdxId, root}]."""
    bom = json.load(open(path))
    doc = next(n for n in bom["@graph"] if n.get("type") == "SpdxDocument")
    pins = []
    for em in doc.get("import", []):
        rh = next((h["hashValue"] for h in em.get("verifiedUsing", [])
                   if h.get("algorithm") == "sha256"), None)
        pins.append({"externalSpdxId": em["externalSpdxId"], "root": rh})
    return pins


def compatible(integrator_upstream_pin, supplier_declared_pins):
    """DEC-023 document-root check: M' must have been validated against the SAME
    upstream document the integrator imports -- equality on IRI AND root."""
    for p in supplier_declared_pins:
        if (p["externalSpdxId"] == integrator_upstream_pin["externalSpdxId"]
                and p["root"] == integrator_upstream_pin["root"]):
            return True, "supplier pinned the same upstream document root"
    return False, "supplier's pinned upstream != the upstream the integrator imports"


def build_integrator_graph(parsed_up, parsed_sup, up_id, sup_id, covered_names):
    """Reconstruct M's contract + M''s contract; rely on M for the product, discharge
    the inherited assumptions named in `covered_names` by relying on M' (`covers` =
    'use M' in addition to M', MINTED from the resolved conformsTo, DEC-024), and
    review the remaining conditions -> a total integrator proof."""
    cu = next(c for c in parsed_up["contracts"] if c["id"] == up_id)
    cs = next(c for c in parsed_sup["contracts"] if c["id"] == sup_id)
    g = Graph("https://example.org/integrator#", "https://example.org/integrator",
              "integrator secure-boot product", "1.0.0")
    g.nodes += [Node("man_up", "manifest", {"component_iri": parsed_up["component_iri"]}),
                Node("man_sup", "manifest", {"component_iri": parsed_sup["component_iri"]}),
                Node("d_impl", "implementation", {})]
    g.seal_ok += ["man_up", "man_sup"]
    g.edges += [Edge("uu", "uses", "d_impl", "man_up"),
                Edge("us", "uses", "d_impl", "man_sup")]
    g.nodes += [Node("d_sys", "requirement", {"text": "Integrator secure-boot product"}),
                Node("d_req", "requirement",
                     {"text": "downstream need met by relying on the upstream subsystem"})]
    g.edges.append(Edge("dfr", "refines", "d_req", "d_sys"))
    # upstream guarantee covers the integrator's requirement
    gup = "g_" + cu["G"]["id"]
    g.nodes.append(Node(gup, "guarantee", {})); g.referenced_under[gup] = "man_up"
    g.edges.append(Edge("dcv", "covers", gup, "d_req", kind="affirmed"))
    up_conds, rel = [], 0
    for a in cu["A"]:
        g.nodes.append(Node(a["id"], "requirement", {"text": a["statement"]}))
        g.referenced_under[a["id"]] = "man_up"; rel += 1
        g.edges.append(Edge(f"eau{rel}", "assumes", gup, a["id"])); up_conds.append(a["id"])
    # supplier guarantee + its own conditions of use
    gsup = "g_" + cs["G"]["id"]
    g.nodes.append(Node(gsup, "guarantee", {})); g.referenced_under[gsup] = "man_sup"
    sup_conds = []
    for a in cs["A"]:
        g.nodes.append(Node(a["id"], "requirement", {"text": a["statement"]}))
        g.referenced_under[a["id"]] = "man_sup"; rel += 1
        g.edges.append(Edge(f"eas{rel}", "assumes", gsup, a["id"])); sup_conds.append(a["id"])
    # THE DISCHARGE (DEC-024): mint covers(gsup, C) for each inherited assumption the
    # supplier declared conformsTo -- derived from data, not hard-coded.
    covered = set(covered_names)
    for c in sorted(covered):
        assert c in up_conds, f"{c} not among upstream conditions {up_conds}"
        g.edges.append(Edge(f"dcov_{c}", "covers", gsup, c, kind="minted"))
    # review the remaining conditions (upstream not covered by M', plus M''s own)
    for j, cid in enumerate(sorted(set([c for c in up_conds if c not in covered] + sup_conds))):
        g.nodes.append(Node(f"dr{j}", "designreview", {}))
        g.edges.append(Edge(f"drv{j}", "reviews", f"dr{j}", cid))
    return g


def _proof_state(m):
    return ("total" if "proof_total" in m else "conditional" if "proof_conditional" in m
            else "unsatisfied" if "proof_unsatisfied" in m else "??")


if __name__ == "__main__":
    parsed = parse_vector_bom("safety_bom.jsonld")
    openings = json.load(open("openings.json"))
    root = parsed["root"]

    print("=== 1. verify openings against the Merkle root ===")
    for c in parsed["contracts"]:
        ok, why = verify_contract(c, openings, root)
        print(f"   {c['id']:18} -> {why}"); assert ok
    tam = json.loads(json.dumps(next(c for c in parsed["contracts"] if c["id"] == "contract-p_sys")))
    tam["A"] = [a for a in tam["A"] if a["id"] != "p_mem"]
    ok, why = verify_contract(tam, openings, root)
    print(f"   contract-p_sys (p_mem dropped) -> {why}"); assert not ok

    print("\n=== 2. reconstruct + verdict ===")
    conds_of = lambda ids: sorted({a["id"] for c in parsed["contracts"]
                                   if c["id"] in ids for a in c["A"]})
    A_ids = {"contract-p_sys"}
    sA = run(parsed, A_ids, conds_of(A_ids),
             "A: rely on p_sys only (one contract), discharge all", render_path="consumer_graph_A")
    sB = run(parsed, A_ids, [c for c in conds_of(A_ids) if c != "p_mem"],
             "B: p_mem undischarged (G9)", render_path="consumer_graph_B")
    C_ids = {"contract-p_sys", "contract-p_sys_2"}
    sC = run(parsed, C_ids, conds_of(C_ids),
             "C: rely on both, p_mem discharged once", render_path="consumer_graph_C")
    assert sA == "total" and sB == "unsatisfied" and sC == "total"
    print("\nOK: gate holds; A total, B unsatisfied (G9), C total (p_mem discharged once for both).")
    print("wrote consumer_graph_A.* / consumer_graph_B.* / consumer_graph_C.*")

    # === 3. compliant-item supplier (DEC-023): import M + M', discharge HAL via M' ===
    print("\n=== 3. compliant-item supplier (DEC-023): import M + M' ===")
    parsed_sup = parse_vector_bom("supplier_bom.jsonld")
    sup_openings = json.load(open("supplier_openings.json"))
    for c in parsed_sup["contracts"]:
        ok, why = verify_contract(c, sup_openings, parsed_sup["root"])
        print(f"   verify M' contract {c['id']:16} -> {why}"); assert ok

    # document-root compatibility: did M' validate against the SAME M the integrator imports?
    up_pin = {"externalSpdxId": parsed["component_iri"], "root": parsed["root"]}
    sup_declared = imports_of_bom("supplier_bom.jsonld")
    okc, whyc = compatible(up_pin, sup_declared)
    print(f"   D: compatibility (M' pin vs integrator's M): {whyc}"); assert okc

    # DEC-024: resolve which inherited assumptions M' covers, from its conformsTo
    # declarations matched against M's published assumption IRIs (not hard-coded).
    cto = conformsto_of_bom("supplier_bom.jsonld")
    covered = resolve_covered(cto, assumption_iris("safety_bom.jsonld"))
    shown = [(f.split("#")[-1], t.split("#")[-1]) for f, t in cto]
    print(f"   D: conformsTo {shown} -> mint covers for {covered}"); assert covered == ["p_hal"]

    g_int = build_integrator_graph(parsed, parsed_sup, "contract-p_sys", "contract-m_hal", covered)
    state = _proof_state(solve(g_int.to_facts())[0])
    print(f"   D: integrator verdict (use M + M', review the rest): proof={state}")
    assert state == "total"

    # emit the integrator's OWN BOM, pinning both M and M'
    pins = [pin_from_bom("safety_bom.jsonld"), pin_from_bom("supplier_bom.jsonld")]
    ibom = export(g_int, imports=pins)
    with open("integrator_bom.jsonld", "w") as f:
        json.dump(ibom, f, indent=2, ensure_ascii=False)
    with open("integrator_openings.json", "w") as f:
        json.dump(export_openings(g_int), f, indent=2)
    idoc = next(n for n in ibom["@graph"] if n["type"] == "SpdxDocument")
    print(f"   D: wrote integrator_bom.jsonld; import pins = "
          f"{[p['externalSpdxId'].split('/')[-1] for p in pins]}")
    render(g_int, states=node_states(g_int), title="Integrator graph - M + M' (DEC-023)",
           path="integrator_graph", fmt="svg")
    render(g_int, states=node_states(g_int), title="Integrator graph - M + M' (DEC-023)",
           path="integrator_graph", fmt="png")

    # incompatible variant: M' validated against a DIFFERENT upstream root -> reject
    bad = [{"externalSpdxId": sup_declared[0]["externalSpdxId"], "root": "0" * 64}]
    oke, whye = compatible(up_pin, bad)
    print(f"   E: incompatible (M' pinned a different root) -> rejected={not oke}")
    assert not oke

    print("\nOK (DEC-023): M' BOM pins M; D compatible -> integrator total; E incompatible -> rejected.")
    print("wrote integrator_bom.jsonld / integrator_openings.json / integrator_graph.*")
