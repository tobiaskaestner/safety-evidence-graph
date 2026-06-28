"""
supplier.py -- the COMPLIANT-ITEM SUPPLIER (DEC-023).

A silicon vendor that supplies M' (an STM32L4 compliant HAL) developed as a
compliant item per IEC 61508. Its published SPDX safety BOM *is* its compliant-item
safety manual: a DEC-020 contract whose guarantee G_M' = "the HAL provides what a
compliant HAL must" and whose conditions of use {m_clk, m_pwr} are its A_up.

The supplier validated M' against a SPECIFIC upstream M (it re-ran M's tests on the
STM32L4 and sealed the proof), so its document PINS that upstream by document root
via SpdxDocument.import -> ExternalMap (DEC-023). The integrator later checks this pin
equals the upstream it imports.

Pipeline: run `python producer.py` and `python spdx_export.py` first (writes M's
safety_bom.jsonld); this reads M's published pin and writes supplier_bom.jsonld.

Run: python3 supplier.py
"""
import json
from lib.seg_graph import Graph, Node, Edge, impl_sha1
from lib.seg_composition import contract_vector
from lib.seg_commitment import member_hash, root, prove
from spdx_export import export, contracts_with_text, _members, pin_from_bom

NS = "https://st.example/seg/stm32l4-hal#"
UPSTREAM_BOM = "safety_bom.jsonld"
UPSTREAM_DOC = "https://zephyrproject.org/seg/crypto-rng#document"   # M's document IRI
UPSTREAM_PHAL = "https://zephyrproject.org/seg/crypto-rng#p_hal"     # M's HAL assumption IRI


def build_supplier(upstream_pin=None) -> Graph:
    g = Graph(
        namespace=NS,
        component_iri="https://st.example/components/stm32l4-hal",
        component_name="STM32L4 Compliant HAL",
        component_version="2.1.0",
    )
    g.nodes += [
        # G_M': the supplier's public guarantee (a satisfied refines-root)
        Node("m_hal", "requirement",
             {"text": "The STM32L4 HAL shall provide the timing and IO guarantees a compliant HAL requires."}),
        Node("m_ts", "testspecification",
             {"intent": "HAL conformance suite re-run on the STM32L4 target.", "body": "test_hal_conformance.c"}),
        Node("m_impl", "implementation", {"api": "STM32L4 HAL", "body": "stm32l4_hal.c",
                                           "sha1": impl_sha1("stm32l4_hal.c")}),
        Node("m_out", "testoutcome", {"outcome": "PASS"}),
        # the supplier's OWN conditions of use (its A_up, published in the safety manual)
        Node("m_clk", "requirement",
             {"text": "The clock tree shall be configured per ST AN-4013."}),
        Node("m_pwr", "requirement",
             {"text": "The board shall be powered within datasheet operating limits."}),
    ]
    g.edges += [
        Edge("mv", "verifies", "m_ts", "m_hal"),
        Edge("mi", "implements", "m_impl", "m_hal"),
        Edge("mc", "confirms", "m_out", "m_ts"),
        Edge("mw", "witnesses", "m_out", "m_impl"),
        Edge("am_clk", "assumes", "m_hal", "m_clk"),
        Edge("am_pwr", "assumes", "m_hal", "m_pwr"),
    ]
    # the upstream M the supplier validated against (sealed import) and the specific
    # upstream Assumption m_hal is offered to satisfy. Both are SOURCE-OF-TRUTH graph
    # facts; the BOM's import pin and conformsTo relationship are PROJECTED from them.
    # `up_phal` is an imported reference -> verdict-inert (no verdict rule keys on
    # `assumption`); `conformsTo` is the pre-import form of `covers` (DEC-024).
    man_fields = {"component_iri": UPSTREAM_DOC}
    if upstream_pin:
        man_fields["root"] = upstream_pin["root"]
    g.nodes += [Node("man_up", "manifest", man_fields),
                Node("up_phal", "assumption", {"iri": UPSTREAM_PHAL})]
    g.seal_ok += ["man_up"]
    g.referenced_under["up_phal"] = "man_up"
    g.edges.append(Edge("ct_hal", "conformsTo", "m_hal", "up_phal"))
    return g


def export_openings(g: Graph) -> dict:
    cs = contracts_with_text(g)
    members = _members(cs)
    return {"algorithm": "sha256-merkle", "root": root(members),
            "openings": {c["id"]: {"member_hash": members[c["id"]],
                                   "path": prove(members, c["id"])} for c in cs}}


if __name__ == "__main__":
    g = build_supplier()
    vec = contract_vector(g.to_facts())
    print("=== compliant-item supplier (M') verdict ===")
    print(f"  proof_state = {vec['proof_state']}")
    for c in vec["vector"]:
        print(f"  C[{c['G']}] = ({c['G']}, {{{', '.join(c['A'])}}})")
    assert vec["proof_state"] == "conditional"
    assert {c["G"]: set(c["A"]) for c in vec["vector"]} == {"m_hal": {"m_clk", "m_pwr"}}

    # pin the upstream M the supplier validated against (read its published BOM)
    upstream_pin = pin_from_bom(UPSTREAM_BOM)
    print(f"\n  pinning upstream M: {upstream_pin['externalSpdxId']}")
    print(f"                root: {upstream_pin['root'][:16]}...")

    # rebuild the graph carrying the pin root, so the manifest/conformsTo are graph
    # facts; export projects the import pin and conformsTo FROM the graph (DEC-024).
    g = build_supplier(upstream_pin=upstream_pin)
    ct = [(e.src, g.node(e.dst).fields["iri"]) for e in g.edges if e.type == "conformsTo"]
    print(f"  conformsTo (from graph): {[(s, t) for s, t in ct]}")

    bom = export(g)
    with open("supplier_bom.jsonld", "w") as f:
        json.dump(bom, f, indent=2, ensure_ascii=False)
    with open("supplier_openings.json", "w") as f:
        json.dump(export_openings(g), f, indent=2)

    docn = next(n for n in bom["@graph"] if n["type"] == "SpdxDocument")
    boms = [n for n in bom["@graph"] if n["type"] == "Bom"]
    print(f"\nwrote supplier_bom.jsonld ({len(bom['@graph'])} nodes), supplier_openings.json")
    print(f"  Merkle root: {docn['verifiedUsing'][0]['hashValue'][:16]}...  over {len(boms)} contract member(s)")
    print(f"  import pins: {[im['externalSpdxId'] for im in docn.get('import', [])]}")

    # --- visualization (parity with producer_graph / integrator_graph) ---
    from producer import node_states
    from lib.seg_graphviz import render
    states = node_states(g)
    render(g, states=states, title="SEG compliant-item supplier graph (STM32L4 HAL, M')",
           path="supplier_graph", fmt="svg")
    render(g, states=states, title="SEG compliant-item supplier graph (STM32L4 HAL, M')",
           path="supplier_graph", fmt="png")
    print("wrote supplier_graph.dot / .svg / .png")
