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
from seg_graph import Graph, Node, Edge
from seg_ruleset import solve

NS = "https://zephyrproject.org/seg/crypto-rng#"


def build_producer() -> Graph:
    g = Graph(
        namespace=NS,
        component_iri="https://zephyrproject.org/components/crypto-rng",
        component_name="Zephyr Crypto RNG",
        component_version="1.0.0",
    )
    g.nodes += [
        Node("p_sys", "requirement",
             {"text": "The crypto subsystem shall provide cryptographically secure random numbers."}),
        Node("p_rng", "requirement",
             {"text": "The RNG shall pass the NIST SP 800-22 statistical test suite."}),
        # published condition of use (A_up): the host must supply entropy.
        Node("p_entropy", "requirement",
             {"text": "The host platform shall provide at least 256 bits of hardware "
                      "entropy to the RNG at boot."}),
        Node("p_ts", "testspecification",
             {"intent": "Run NIST SP 800-22 against the CSPRNG output.",
              "body": "test_sp800_22.c"}),
        Node("p_impl", "implementation",
             {"api": "int csprng_get(uint8_t *buf, size_t n);", "body": "rng_csprng.c"}),
        Node("p_out", "testoutcome",
             {"outcome": "PASS", "ran_against_sha": "deadbeef"}),
    ]
    g.edges += [
        Edge("pf", "refines", "p_rng", "p_sys"),       # p_rng refines p_sys
        Edge("pv", "verifies", "p_ts", "p_rng"),
        Edge("pi", "implements", "p_impl", "p_rng"),
        Edge("pc", "confirms", "p_out", "p_ts"),
        Edge("pw", "witnesses", "p_out", "p_impl"),
        # local authored `assumes` => A_up => residual (source p_sys is NOT referenced)
        Edge("pa", "assumes", "p_sys", "p_entropy"),
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


if __name__ == "__main__":
    g = build_producer()
    result = verdict_and_contract(g)
    print("=== producer verdict ===")
    print(json.dumps(result, indent=2))
    assert result["proof_state"] == "conditional", "producer should be conditional"
    assert result["contract"]["A_residual"] == ["p_entropy"]
    assert set(result["contract"]["G_discharged"]) == {"p_sys", "p_rng"}
    print("\nOK: conditional verdict with G={p_sys,p_rng}, A={p_entropy}")
