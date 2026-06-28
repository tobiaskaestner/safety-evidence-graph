"""
seg_composition.py -- the DEC-019 composition/closure layer, on top of the
DEC-018 verdict rule-set. Canonical home for the contract-vector computation so
the producer and the demos share one definition.

  guarantee(R)  := top-level requirement, satisfied, not a child (root of a
                   discharged subtree)
  desc(R,N)     := descendant-or-self of R over refines
  guards(R,C)   := C is an obligation assumed anywhere in R's subtree  (= A_R)
  struct_err_assumes_not_forwarded(C)
                := C is authored (residual) AND locally handled    (DEC-019 forbid)
"""
import clingo
from lib.seg_ruleset import DEFS, PROG

CLOSURE = r"""
% the exported guarantee is a TOP-LEVEL satisfied requirement (the root of a
% discharged subtree); never a child, never an authored-condition node
has_parent(R) :- edge(_, refines, R, _).
guarantee(R)  :- node(R, requirement), satisfied(R), not has_parent(R).
% descendant-or-self over refines (child --refines--> parent), climbing DOWN
desc(R, R) :- guarantee(R).
desc(R, X) :- desc(R, P), edge(_, refines, X, P).
% A_i: obligations assumed anywhere in the subtree (the down-closure)
guards(R, C) :- desc(R, N), edge(_, assumes, N, C), obligation(C).
% I_i (DEC-028): implementations of any requirement in R's subtree (the pinned set)
impl_member(R, I) :- desc(R, N), edge(_, implements, I, N), node(I, implementation).
"""

STRUCT = r"""
handled(C) :- active_edge(_, reviews, _, C).
handled(C) :- active_edge(_, covers, _, C).
handled(C) :- active_edge(_, verifies, _, C).
handled(C) :- active_edge(_, implements, _, C).
% DEC-019: authored as an assumption (residual) AND locally handled => error
struct_err_assumes_not_forwarded(C) :- residual(C), handled(C).
"""

_SHOW = ("#show guarantee/1.\n#show guards/2.\n#show impl_member/2.\n#show obligation/1.\n"
         "#show struct_err_assumes_not_forwarded/1.\n"
         "#show proof_total/0.\n#show proof_conditional/0.\n#show proof_unsatisfied/0.\n")


def contract_vector(facts: str):
    """Return {'proof_state', 'vector':[{'G','A'}], 'obligations', 'struct_errors'}."""
    ctl = clingo.Control(["0"])
    ctl.add("b", [], DEFS + PROG + CLOSURE + STRUCT + facts + _SHOW)
    ctl.ground([("b", [])])
    M = []
    ctl.solve(on_model=lambda m: M.append(frozenset(str(a) for a in m.symbols(shown=True))))
    assert len(M) == 1, f"expected single stable model, got {len(M)}"
    m = M[0]

    guards = {}
    for a in m:
        if a.startswith("guards("):
            L, C = a[len("guards("):-1].split(",")
            guards.setdefault(L.strip(), []).append(C.strip())
    impls = {}
    for a in m:
        if a.startswith("impl_member("):
            L, I = a[len("impl_member("):-1].split(",")
            impls.setdefault(L.strip(), []).append(I.strip())
    guarantees = sorted(a[len("guarantee("):-1] for a in m if a.startswith("guarantee("))
    obligations = sorted(a[len("obligation("):-1] for a in m if a.startswith("obligation("))
    errs = sorted(a[len("struct_err_assumes_not_forwarded("):-1]
                  for a in m if a.startswith("struct_err_assumes_not_forwarded("))
    state = ("total" if "proof_total" in m else "conditional" if "proof_conditional" in m
             else "unsatisfied" if "proof_unsatisfied" in m else "??")
    return {
        "proof_state": state,
        "vector": [{"G": L, "A": sorted(guards.get(L, [])), "I": sorted(impls.get(L, []))}
                   for L in guarantees],
        "obligations": obligations,
        "struct_errors": errs,
    }
