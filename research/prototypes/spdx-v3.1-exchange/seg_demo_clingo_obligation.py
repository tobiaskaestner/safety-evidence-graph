"""
seg_demo_clingo_obligation_v1.py -- validation gate for DEC-018.

Confirms that introducing `obligation/1` and tightening `satisfied/1` leaves
every proof VERDICT invariant (proof_* read residual/unsatisfied/product, never
satisfied/obligation) and that satisfied / obligation / unsatisfied form a
mutually-exclusive partition. Self-contained: covers all three proof states.
"""
import clingo
from seg_ruleset import DEFS, PROG
from producer import build_producer

# OLD = applied PROG with every `obligation` line removed and `satisfied` reverted
NEW_PROG = PROG
OLD_PROG = "\n".join(l for l in PROG.splitlines() if "obligation" not in l)
OLD_PROG += "\nsatisfied(R) :- node(R, requirement), not unsatisfied(R).\n"
assert "obligation" not in OLD_PROG

SHOW_OLD = ("#show satisfied/1.\n#show unsatisfied/1.\n#show residual/1.\n"
            "#show proof_total/0.\n#show proof_conditional/0.\n#show proof_unsatisfied/0.\n")
SHOW_NEW = SHOW_OLD + "#show obligation/1.\n"

TOTAL = """
node(r,requirement). node(l,requirement). edge(f,refines,l,r).
node(ts,testspecification). node(im,implementation).
node(o,testoutcome). node_field(o,outcome,"PASS").
edge(v,verifies,ts,l). edge(i,implements,im,l).
edge(c,confirms,o,ts). edge(w,witnesses,o,im).
"""
UNSAT = "node(r,requirement). node(l,requirement). edge(f,refines,l,r).\n"

FIXTURES = {
    "producer (conditional)": build_producer().to_facts(),
    "total":                  TOTAL,
    "unsatisfied":            UNSAT,
}


def _solve(prog, facts, show):
    ctl = clingo.Control(["0"]); ctl.add("b", [], DEFS + prog + facts + show); ctl.ground([("b", [])])
    M = []; ctl.solve(on_model=lambda m: M.append(frozenset(str(a) for a in m.symbols(shown=True))))
    assert len(M) == 1
    return M[0]


def _state(m):
    return ("total" if "proof_total" in m else "conditional" if "proof_conditional" in m
            else "unsatisfied" if "proof_unsatisfied" in m else "??")


def _part(m, pfx):
    return set(a[len(pfx):-1] for a in m if a.startswith(pfx))


passed = 0
for name, facts in FIXTURES.items():
    old, new = _solve(OLD_PROG, facts, SHOW_OLD), _solve(NEW_PROG, facts, SHOW_NEW)
    so, sn = _state(old), _state(new)
    sat, obl, uns = _part(new, "satisfied("), _part(new, "obligation("), _part(new, "unsatisfied(")
    print(f"  {name:24} verdict old={so} new={sn}  obligation={sorted(obl) or '[]'}")
    assert so == sn, f"{name}: verdict changed"
    assert not (sat & obl) and not (sat & uns) and not (obl & uns), f"{name}: buckets overlap"
    passed += 1
print(f"\n{passed}/{len(FIXTURES)} fixtures: verdict-invariant, three buckets disjoint.")
