"""
consumer.py -- step 5: a downstream "secure-boot" SEG project relies on the
imported crypto-RNG safety case (parsed from safety_bom.jsonld) via `covers`,
then runs the SAME verdict engine.

The inherited condition-of-use (entropy) becomes a referenced obligation the
downstream must DISCHARGE. Two scenarios:

  A. discharge it (a DesignReview asserting the downstream platform supplies
     the entropy) -> expect proof_total.
  B. do NOT discharge it, and additionally author a local re-published
     condition -> observe what the engine actually reports. This stresses the
     "propagate an undischarged inherited assumption downstream" path.

Run: python3 consumer.py
"""
import json
from seg_ruleset import solve
from spdx_import import parse_bom

MAN = "man_crypto"          # the downstream's Manifest for the imported component


def upstream_facts(imp):
    """The SEALED upstream structure, reconstructed from the BOM."""
    g = imp["guarantee_root"]
    f = [
        f"node({g}, guarantee).",
        f"referenced_under({g}, {MAN}).",
        f"node({MAN}, manifest).",
        f'node_field({MAN}, component_iri, "{imp["component_iri"]}").',
        f"seal_ok({MAN}).",                       # IDEALIZED (G6): seal trusted
    ]
    for i, a in enumerate(imp["assumptions"]):
        cid = a["id"]                              # reconstructed as a requirement (G3)
        f += [
            f"node({cid}, requirement).",
            f"referenced_under({cid}, {MAN}).",
            f"edge(ea_{i}, assumes, {g}, {cid}).",
        ]
    return "\n".join(f) + "\n"


def downstream_facts():
    """The downstream product: d_use relies on the imported guarantee."""
    g = "p_sys"   # guarantee_root id (set after parse); placeholder replaced below
    return ""     # built inline in scenario to keep the guarantee id explicit


def scenario(imp, discharge_inherited: bool, republish: bool):
    g = imp["guarantee_root"]
    entropy = imp["assumptions"][0]["id"]
    f = upstream_facts(imp)
    # downstream product structure
    f += f"""
node(d_sys, requirement). node(d_use, requirement).
edge(df, refines, d_use, d_sys).
edge(dc, covers, {g}, d_use).
node(d_impl, implementation). edge(du, uses, d_impl, {MAN}).
"""
    if discharge_inherited:
        f += f"node(d_rev, designreview). edge(drv, reviews, d_rev, {entropy}).\n"
    if republish:
        f += "node(d_pub, requirement). edge(dap, assumes, d_sys, d_pub).\n"
    return f


def run(imp, label, **kw):
    facts = scenario(imp, **kw)
    models = solve(facts)
    assert len(models) == 1, f"{label}: {len(models)} models"
    m = models[0]

    def atoms(pfx):
        return sorted(a[len(pfx):-1] for a in m if a.startswith(pfx))

    state = ("total" if "proof_total" in m else
             "conditional" if "proof_conditional" in m else
             "unsatisfied" if "proof_unsatisfied" in m else "??")
    print(f"\n[{label}]  proof_state = {state}")
    print(f"   product   = {atoms('product(')}")
    print(f"   satisfied = {atoms('satisfied(')}")
    print(f"   unsatisfied = {atoms('unsatisfied(')}")
    print(f"   residual  = {atoms('residual(')}")
    return state, m


if __name__ == "__main__":
    imp = parse_bom("safety_bom.jsonld")
    print("=== imported contract ===")
    print(json.dumps(imp, indent=2))

    sA, _ = run(imp, "A: inherited condition discharged by review",
                discharge_inherited=True, republish=False)
    sB, _ = run(imp, "B: inherited condition NOT discharged, local re-publish added",
                discharge_inherited=False, republish=True)

    print("\n=== river check ===")
    print(f"  A expected total       -> {sA}  {'OK' if sA=='total' else 'SURPRISE'}")
    print(f"  B (stress) reported as -> {sB}")
