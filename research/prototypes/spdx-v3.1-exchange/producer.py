"""
producer.py -- step 1 & 2 of the round-trip.

Synthesizes a small SELF-CONTAINED producer safety case (a Zephyr crypto-RNG
component) that comes out CONDITIONAL: every in-scope (product) requirement is
satisfied, but the product publishes ONE condition of use as A_up, which the
verdict engine reports as a residual. The exported contract is therefore:

  G (guarantee / discharged scope) = satisfied product requirements that are
      NOT themselves residual conditions
  A (assumptions / residual)       = residual conditions published as A_up

Run: python3 producer.py
"""
import json
from lib.seg_graph import Graph, Node, Edge, impl_sha1
from lib.seg_ruleset import solve

NS = "https://zephyrproject.org/seg/crypto-rng#"


def build_producer() -> Graph:
    g = Graph(
        namespace=NS,
        component_iri="https://zephyrproject.org/components/crypto-rng",
        component_name="Zephyr Crypto RNG",
        component_version="1.0.0",
    )
    g.nodes += [
        # --- subsystem 1: RNG (root p_sys, leaf p_rng) ---
        Node("p_sys", "requirement",
             {"text": "The crypto subsystem shall provide cryptographically secure random numbers."}),
        Node("p_rng", "requirement",
             {"text": "The RNG shall pass the NIST SP 800-22 statistical test suite."}),
        Node("p_ts", "testspecification",
             {"intent": "Run NIST SP 800-22 against the CSPRNG output.", "body": "test_sp800_22.c"}),
        Node("p_impl", "implementation",
             {"api": "int csprng_get(uint8_t *buf, size_t n);", "body": "rng_csprng.c",
              "sha1": impl_sha1("rng_csprng.c")}),
        Node("p_out", "testoutcome", {"outcome": "PASS", "ran_against_sha": "deadbeef"}),

        # --- subsystem 2: hashing (root p_sys_2, leaves p_sha256, p_sha512) ---
        Node("p_sys_2", "requirement",
             {"text": "The crypto subsystem shall provide collision-resistant hashing."}),
        Node("p_sha256", "requirement", {"text": "Provide a conformant SHA-256 implementation."}),
        Node("p_sha512", "requirement", {"text": "Provide a conformant SHA-512 implementation."}),
        Node("p_ts256", "testspecification", {"body": "test_sha256_kat.c"}),
        Node("p_im256", "implementation", {"body": "sha256.c", "sha1": impl_sha1("sha256.c")}),
        Node("p_o256", "testoutcome", {"outcome": "PASS"}),
        Node("p_ts512", "testspecification", {"body": "test_sha512_kat.c"}),
        Node("p_im512", "implementation", {"body": "sha512.c", "sha1": impl_sha1("sha512.c")}),
        Node("p_o512", "testoutcome", {"outcome": "PASS"}),

        # --- published conditions of use (obligations) ---
        Node("p_entropy", "requirement",
             {"text": "The host shall provide >=256 bits of hardware entropy at boot."}),  # p_sys ancestor
        Node("p_rng_a", "requirement",
             {"text": "The RNG API shall be called from a single thread."}),               # p_rng local
        Node("p_sha256_a", "requirement",
             {"text": "Input buffers to SHA-256 shall not alias the output."}),            # p_sha256 local
        Node("p_sha512_a", "requirement",
             {"text": "SHA-512 shall run only on a 64-bit word architecture."}),           # p_sha512 local
        Node("p_mem", "requirement",
             {"text": "The caller shall provide DMA-incoherent scratch memory."}),         # shared
        Node("p_hal", "requirement",
             {"text": "A compliant hardware abstraction layer (HAL) shall be present."}),   # p_rng deployment cond
        # --- witness-side environment (sealed; NOT exported) ---
        Node("p_qemu", "environment",
             {"text": "QEMU emulating the target board; HAL surrogate used for verification."}),
    ]
    g.edges += [
        # subsystem 1
        Edge("pf", "refines", "p_rng", "p_sys"),
        Edge("pv", "verifies", "p_ts", "p_rng"),
        Edge("pi", "implements", "p_impl", "p_rng"),
        Edge("pc", "confirms", "p_out", "p_ts"),
        Edge("pw", "witnesses", "p_out", "p_impl"),
        # subsystem 2
        Edge("f256", "refines", "p_sha256", "p_sys_2"),
        Edge("f512", "refines", "p_sha512", "p_sys_2"),
        Edge("v256", "verifies", "p_ts256", "p_sha256"),
        Edge("i256", "implements", "p_im256", "p_sha256"),
        Edge("c256", "confirms", "p_o256", "p_ts256"),
        Edge("w256", "witnesses", "p_o256", "p_im256"),
        Edge("v512", "verifies", "p_ts512", "p_sha512"),
        Edge("i512", "implements", "p_im512", "p_sha512"),
        Edge("c512", "confirms", "p_o512", "p_ts512"),
        Edge("w512", "witnesses", "p_o512", "p_im512"),
        # assumptions (authored, local => obligations)
        Edge("pa", "assumes", "p_sys", "p_entropy"),       # ancestor obligation for p_rng
        Edge("ar", "assumes", "p_rng", "p_rng_a"),         # p_rng local
        Edge("a256", "assumes", "p_sha256", "p_sha256_a"), # p_sha256 local
        Edge("a512", "assumes", "p_sha512", "p_sha512_a"), # p_sha512 local
        Edge("am_r", "assumes", "p_rng", "p_mem"),         # shared: p_rng ...
        Edge("am_5", "assumes", "p_sha512", "p_mem"),      # ... and p_sha512
        Edge("ahal", "assumes", "p_rng", "p_hal"),         # HAL deployment condition -> flows into A_i
        # witness-side (sealed, NOT exported): QEMU surrogate + outcome provenance
        Edge("sfq", "surrogate_for", "p_qemu", "p_hal"),   # QEMU stands in for the HAL while testing
        Edge("roq", "ran_on", "p_out", "p_qemu"),          # the RNG outcome was produced on QEMU
    ]
    return g


def verdict_and_contract(g: Graph):
    models = solve(g.to_facts())
    assert len(models) == 1, f"expected single stable model, got {len(models)}"
    m = models[0]

    def atoms(pfx):
        return sorted(a[len(pfx):-1] for a in m if a.startswith(pfx))

    satisfied = atoms("satisfied(")
    residual = atoms("residual(")
    product = atoms("product(")
    state = ("total" if "proof_total" in m else
             "conditional" if "proof_conditional" in m else
             "unsatisfied" if "proof_unsatisfied" in m else "??")

    # Contract split: G = satisfied product reqs that are not residual; A = residual.
    guarantee = [r for r in satisfied if r in product and r not in residual]
    assumptions = residual
    return {
        "proof_state": state,
        "product": product,
        "satisfied": satisfied,
        "residual": residual,
        "contract": {"G_discharged": sorted(guarantee), "A_residual": sorted(assumptions)},
    }


def node_states(g: Graph):
    """Map each requirement id -> 'satisfied' | 'obligation' | 'unsatisfied'."""
    m = solve(g.to_facts())[0]

    def atoms(pfx):
        return set(a[len(pfx):-1] for a in m if a.startswith(pfx))

    sat, obl, uns = atoms("satisfied("), atoms("obligation("), atoms("unsatisfied(")
    states = {}
    for n in g.nodes:
        if n.type == "requirement":
            states[n.id] = ("unsatisfied" if n.id in uns else
                            "obligation" if n.id in obl else
                            "satisfied" if n.id in sat else "?")
    return states


if __name__ == "__main__":
    from lib.seg_composition import contract_vector
    g = build_producer()
    result = verdict_and_contract(g)
    vec = contract_vector(g.to_facts())

    print("=== producer verdict ===")
    print(f"  proof_state = {result['proof_state']}")
    print(f"  obligations = {vec['obligations']}")
    print(f"  struct_errors = {vec['struct_errors'] or '(none)'}")
    print("\n=== contract vector  C_i = (G_i, {A_i}) ===")
    for c in vec["vector"]:
        print(f"  C[{c['G']}] = ({c['G']}, {{{', '.join(c['A'])}}})")

    # shared-obligation report
    from collections import Counter
    shared = sorted(o for o, n in Counter(
        a for c in vec["vector"] for a in c["A"]).items() if n > 1)
    print(f"\n  shared obligations (in >1 contract): {shared}")

    # --- checks ---
    assert result["proof_state"] == "conditional"
    assert vec["struct_errors"] == []
    got = {c["G"]: set(c["A"]) for c in vec["vector"]}
    assert got == {
        "p_sys":   {"p_entropy", "p_rng_a", "p_mem", "p_hal"},
        "p_sys_2": {"p_sha256_a", "p_sha512_a", "p_mem"},
    }, got
    assert shared == ["p_mem"]
    print("\nOK: 2 root contracts; p_hal flows into C[p_sys]; p_mem shared across subsystems.")

    # --- visualization ---
    from lib.seg_graphviz import render
    states = node_states(g)
    render(g, states=states, title="SEG producer graph (crypto: RNG + hashing)",
           path="producer_graph", fmt="svg")
    render(g, states=states, title="SEG producer graph (crypto: RNG + hashing)",
           path="producer_graph", fmt="png")
    print("wrote producer_graph.dot / .svg / .png")
