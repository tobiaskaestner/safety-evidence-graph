"""
seg_demo_clingo_forward_export_v1.py
====================================
G9, export side -- does a FORWARDED inherited condition actually land in the
integrator's re-exported A_i (the "re-publish the remainder" claim)?

The verdict-layer gate (seg_demo_clingo_forward_v1.py) makes the integrator's
proof CONDITIONAL and marks the inherited condition `forwarded` + `obligation`.
But the DEC-019 down-closure `guards/2` ranges over the `refines` subtree only
(`desc/2`), while a forwarded inherited condition is assumed by the imported
guarantee `g_up` and reachable from the integrator's root ONLY through `covers`.
So under the current rule the re-exported A_i drops the remainder -- the contract
the next hop receives would not carry it.

Candidate (DEC-022): one additive `guards` clause that reaches through a
covers-reliance in the subtree, but ONLY for `forwarded` conditions -- so the
re-published remainder is exactly the forwarded set; a locally DISCHARGED
inherited condition is correctly excluded.

  guards(R,C) :- desc(R,N), active_edge(_,covers,GUP,N), edge(_,assumes,GUP,C), forwarded(C).

INV: inert on any forward-free graph (OLD vector == NEW vector).
S1 : OLD closure on the integrator fixture -> A_i drops the forwarded remainder (the gap).
S2 : NEW closure -> A_i = {forwarded}; the discharged inherited condition is excluded.

Run: python -m demos.seg_demo_clingo_forward_export   (needs clingo)
"""
import clingo
import lib.seg_ruleset as R
from demos import seg_demo_clingo_forward as F          # ratified FORWARD block + condition_of_use rollup
from lib.seg_composition import CLOSURE, STRUCT      # DEC-019 down-closure (OLD) + structural facet

# FIXED verdict engine (forward + condition_of_use rollup), as ratified.
PROG_FIXED = R.BASE_SHARED + R.LEAF_COMP + R.COMPOSITION + F.FORWARD + F.FIXED_ROLLUP

NEW_GUARDS = r"""
% --- DEC-022 candidate: re-export the FORWARDED remainder through `covers` ---
% A forwarded inherited condition, reached via a covers-reliance anywhere in the
% guarantee's subtree, is part of the re-published A_i. `forwarded(C)` is the gate:
% a locally DISCHARGED inherited condition (not forwarded) is correctly excluded.
guards(R, C) :- desc(R, N), active_edge(_, covers, GUP, N),
                edge(_, assumes, GUP, C), forwarded(C).
"""
CLOSURE_OLD = CLOSURE
CLOSURE_NEW = CLOSURE + NEW_GUARDS

DEFS = R.DEFS + "#defined forward/4. #defined affirmed_forward/2.\n"
SHOW = ("#show guarantee/1.\n#show guards/2.\n#show obligation/1.\n"
        "#show condition_of_use/1.\n#show forwarded/1.\n"
        "#show struct_err_assumes_not_forwarded/1.\n"
        "#show proof_total/0.\n#show proof_conditional/0.\n#show proof_unsatisfied/0.\n")


def vector(facts, closure):
    ctl = clingo.Control(["0"])
    ctl.add("b", [], DEFS + PROG_FIXED + closure + STRUCT + facts + SHOW)
    ctl.ground([("b", [])])
    M = []
    ctl.solve(on_model=lambda m: M.append(frozenset(str(a) for a in m.symbols(shown=True))))
    assert len(M) == 1, f"determinism guardrail: expected 1 answer set, got {len(M)}"
    m = M[0]
    guards = {}
    for a in m:
        if a.startswith("guards("):
            L, C = a[len("guards("):-1].split(",")
            guards.setdefault(L.strip(), []).append(C.strip())
    gtees = sorted(a[len("guarantee("):-1] for a in m if a.startswith("guarantee("))
    state = ("total" if "proof_total" in m else "conditional" if "proof_conditional" in m
             else "unsatisfied" if "proof_unsatisfied" in m else "??")
    vec = {L: sorted(guards.get(L, [])) for L in gtees}
    errs = sorted(a[len("struct_err_assumes_not_forwarded("):-1]
                  for a in m if a.startswith("struct_err_assumes_not_forwarded("))
    return {"state": state, "vector": vec, "struct_errors": errs}


# --- Fixture: integrator relies on g_up, which assumes TWO inherited conditions:
#     c_fwd -- forwarded onward (affirmed);  c_dis -- discharged locally (review).
INTEGRATOR = """
node(d_sys, requirement).
node(g_up, guarantee).
node(c_fwd, requirement).
node(c_dis, requirement).
edge(cv1, covers, g_up, d_sys).
edge(asf, assumes, g_up, c_fwd).
edge(asd, assumes, g_up, c_dis).
referenced_under(g_up, m1).
referenced_under(c_fwd, m1).
referenced_under(c_dis, m1).
seal_ok(m1).
edge(us1, uses, impl_int, m1).
edge(fwd1, forward, d_sys, c_fwd).
affirmed_forward(d_sys, c_fwd).
edge(rv1, reviews, rev_d, c_dis).
"""

# --- Forward-free fixture for invariance: a root guarantee whose subtree authors
#     a LOCAL residual condition-of-use (the existing DEC-019 (a) path). No forward.
LOCAL_ONLY = """
node(p_sys, requirement).
node(p_leaf, requirement).
edge(rf1, refines, p_leaf, p_sys).
edge(im1, implements, impl_l, p_leaf).
edge(vf1, verifies, ts_l, p_leaf).
edge(cf1, confirms, ok1, ts_l).
edge(wf1, witnesses, ok1, impl_l).
node_field(ok1, outcome, "PASS").
node(c_loc, requirement).
edge(asl, assumes, p_leaf, c_loc).
"""


if __name__ == "__main__":
    print("G9 export gate -- does the forwarded remainder reach the re-exported A_i?\n")

    # ---- INVARIANCE: new clause is inert on a forward-free graph ----
    inv_old = vector(LOCAL_ONLY, CLOSURE_OLD)
    inv_new = vector(LOCAL_ONLY, CLOSURE_NEW)
    assert inv_old == inv_new, "new guards clause must be inert without forwarded conditions"
    print(f"  INVARIANCE local-only fixture: OLD == NEW   vector={inv_new['vector']}   OK")

    # ---- S1: OLD closure drops the forwarded remainder (the gap) ----
    s1 = vector(INTEGRATOR, CLOSURE_OLD)
    print(f"  S1 OLD closure   proof={s1['state']:<11} A[d_sys]={s1['vector'].get('d_sys')}")
    assert s1["state"] == "conditional"
    assert s1["vector"].get("d_sys") == [], "OLD closure should drop the forwarded c_fwd"

    # ---- S2: NEW closure re-exports forwarded only; discharged excluded ----
    s2 = vector(INTEGRATOR, CLOSURE_NEW)
    print(f"  S2 NEW closure   proof={s2['state']:<11} A[d_sys]={s2['vector'].get('d_sys')}")
    assert s2["state"] == "conditional"
    assert s2["vector"].get("d_sys") == ["c_fwd"], "NEW closure must re-export exactly the forwarded remainder"
    assert "c_dis" not in s2["vector"].get("d_sys"), "a DISCHARGED inherited condition must NOT be re-exported"
    assert s2["struct_errors"] == [], "discharging an inherited (non-residual) condition is legal"

    print("\nOK: 3/3. New clause inert without forward (INV); OLD drops the remainder (S1);"
          " NEW re-exports exactly {c_fwd}, excludes the discharged c_dis (S2).")
