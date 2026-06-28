"""
seg_demo_clingo_conformsto_v1.py -- gate for DEC-024.

`conformsTo(G, A_iri)` is a producer-side DECLARATION (grounded verbatim in SPDX
Core RelationshipType `conformsTo`: "The `from` Element conforms to each `to`
Assumption or Specification"): guarantee G is offered to satisfy an external
upstream Assumption identified by IRI. It is VERDICT-INERT in the producer graph,
and is RESOLVED to a DEC-017 `covers` edge on import by matching the conformsTo
target IRI against an imported assumption's IRI -- the importer mints `covers`
only once G is referenced under the sealed manifest (so the reliance/seal checks
of DEC-017 legitimately apply). This replaces the hard-coded `covers` the
integrator used to invent (GAPS G12).

Checks:
  A. inert     -- the verdict rules never mention conformsTo, and adding a
                  conformsTo edge leaves the supplier verdict/vector identical.
  B. matched   -- a conformsTo whose target IRI is imported mints covers -> total.
  C. unmatched -- a conformsTo whose target is NOT imported mints nothing -> the
                  inherited assumption stays undischarged -> proof not total
                  (the honest forward-or-fail point, DEC-022).
"""
from lib.seg_ruleset import DEFS, PROG, solve
from lib.seg_composition import CLOSURE, STRUCT, contract_vector
from lib.seg_graph import Graph, Node, Edge
from supplier import build_supplier


def resolve_covers(conformsto, imported_assumption_iris):
    """read-match-mint. conformsto = [(g_local_id, target_iri)];
    imported_assumption_iris = {iri: local_assumption_id}. Returns the covers edges
    [(g_local_id, local_assumption_id)] for matched targets only."""
    return [(g, imported_assumption_iris[iri])
            for (g, iri) in conformsto if iri in imported_assumption_iris]


def integrator_facts(covers_edges):
    """Minimal integrator: upstream guarantee `gup` (sealed import) covers `d_req`
    and assumes the inherited `p_hal`; supplier guarantee `gsup` (sealed import)
    assumes `m_clk`; a review discharges `m_clk`. `covers_edges` is the (gsup,p_hal)
    reliance the importer MINTS from a matched conformsTo (or [] when unmatched)."""
    g = Graph("https://ex/int#", "https://ex/int", "int", "1")
    g.nodes += [Node("man_up", "manifest", {}), Node("man_sup", "manifest", {}),
                Node("d_impl", "implementation", {}),
                Node("d_sys", "requirement", {}), Node("d_req", "requirement", {}),
                Node("gup", "guarantee", {}), Node("p_hal", "requirement", {}),
                Node("gsup", "guarantee", {}), Node("m_clk", "requirement", {}),
                Node("dr", "designreview", {})]
    g.seal_ok += ["man_up", "man_sup"]
    g.referenced_under.update({"gup": "man_up", "p_hal": "man_up",
                               "gsup": "man_sup", "m_clk": "man_sup"})
    g.edges += [Edge("uu", "uses", "d_impl", "man_up"),
                Edge("us", "uses", "d_impl", "man_sup"),
                Edge("fr", "refines", "d_req", "d_sys"),
                Edge("cv", "covers", "gup", "d_req"),
                Edge("au", "assumes", "gup", "p_hal"),
                Edge("as", "assumes", "gsup", "m_clk"),
                Edge("rv", "reviews", "dr", "m_clk")]
    for i, (gid, aid) in enumerate(covers_edges):
        g.edges.append(Edge(f"mc{i}", "covers", gid, aid))
    return g.to_facts()


def _state(facts):
    m = solve(facts)[0]
    return ("total" if "proof_total" in m else "conditional" if "proof_conditional" in m
            else "unsatisfied" if "proof_unsatisfied" in m else "??")


ok = 0

# A. inert -----------------------------------------------------------------
RULES = DEFS + PROG + CLOSURE + STRUCT
assert "conformsTo" not in RULES, "verdict rules must not mention conformsTo"
base = build_supplier().to_facts()
withct = base + "edge(ct1, conformsTo, m_hal, ext_iri).\nnode(ext_iri, external).\n"
assert contract_vector(base) == contract_vector(withct), "conformsTo changed the verdict"
ok += 1
print("A inert     : rules mention conformsTo 0 times; supplier vector unchanged by it")

# B. matched -> mint covers -> total ---------------------------------------
M_IRI = "https://zephyrproject.org/seg/crypto-rng#p_hal"
imported = {M_IRI: "p_hal"}                       # integrator resolved p_hal from M
minted = resolve_covers([("gsup", M_IRI)], imported)
assert minted == [("gsup", "p_hal")], minted
sB = _state(integrator_facts(minted))
assert sB == "total", sB
ok += 1
print(f"B matched   : conformsTo target imported -> mint covers(gsup,p_hal) -> {sB}")

# C. unmatched -> mint nothing -> not total --------------------------------
minted2 = resolve_covers([("gsup", "https://other/doc#p_other")], imported)
assert minted2 == [], minted2
sC = _state(integrator_facts(minted2))
assert sC != "total", sC
ok += 1
print(f"C unmatched : conformsTo target NOT imported -> no covers -> {sC} (forward-or-fail)")

print(f"\nOK: {ok}/3. conformsTo is verdict-inert; import resolves it to covers by IRI match;")
print("an unmatched target leaves the inherited assumption undischarged (forward per DEC-022 or fail).")
