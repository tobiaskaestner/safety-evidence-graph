"""
seg_demo_clingo_contract_vector_v1.py -- gate for the DEC-019 contract vector
(root-keyed / down-closure form). Uses the CANONICAL rules in seg_composition
(no divergent inline copy).

CLEAN case  : the producer's two-subsystem graph -> two per-component contracts
              C[p_sys]   = (p_sys,   {p_entropy, p_rng_a, p_mem})
              C[p_sys_2] = (p_sys_2, {p_sha256_a, p_sha512_a, p_mem})
              p_mem double-counted across the two roots; no structural error.
VIOLATING   : a subtree that both authors an assumption and reviews it locally
              -> struct_err_assumes_not_forwarded fires.
"""
from collections import Counter
from seg_graph import Graph, Node, Edge
from seg_composition import contract_vector
from producer import build_producer


def show(label, res):
    print(f"\n[{label}]  proof = {res['proof_state']}")
    for c in res["vector"]:
        print(f"   C[{c['G']}] = ({c['G']}, {{{', '.join(c['A'])}}})")
    print(f"   struct_errors = {res['struct_errors'] or '(none)'}")
    return res


# --- CLEAN: producer graph, root-keyed ---
clean = show("clean: producer (2 subsystems)", contract_vector(build_producer().to_facts()))
got = {c["G"]: set(c["A"]) for c in clean["vector"]}
assert got == {
    "p_sys":   {"p_entropy", "p_rng_a", "p_mem", "p_hal"},
    "p_sys_2": {"p_sha256_a", "p_sha512_a", "p_mem"},
}, got
assert clean["struct_errors"] == []
shared = [o for o, n in Counter(a for c in clean["vector"] for a in c["A"]).items() if n > 1]
assert shared == ["p_mem"]
print("   -> 2 root contracts; p_mem shared across p_sys & p_sys_2. OK")


# --- VIOLATING: a subtree authors an assumption AND reviews it ---
def violating() -> Graph:
    g = Graph("https://example.org/v#", "https://example.org/c", "viol", "1.0")
    g.nodes += [
        Node("rr", "requirement", {}), Node("ll", "requirement", {}),
        Node("ts", "testspecification", {}), Node("im", "implementation", {}),
        Node("oo", "testoutcome", {"outcome": "PASS"}),
        Node("cc", "requirement", {}),            # authored condition ...
        Node("dr", "designreview", {}),           # ... that is also reviewed
    ]
    g.edges += [
        Edge("f", "refines", "ll", "rr"),
        Edge("v", "verifies", "ts", "ll"), Edge("i", "implements", "im", "ll"),
        Edge("c", "confirms", "oo", "ts"), Edge("w", "witnesses", "oo", "im"),
        Edge("a", "assumes", "ll", "cc"),         # authored
        Edge("r", "reviews", "dr", "cc"),         # handled -> incoherent
    ]
    return g


viol = show("violating: cc authored and reviewed", contract_vector(violating().to_facts()))
assert viol["struct_errors"] == ["cc"], viol["struct_errors"]
print("   -> struct_err_assumes_not_forwarded(cc) fires. OK")
