"""
seg_ruleset.py -- the SEG stratified-Datalog verdict ruleset, lifted VERBATIM
from seg_demo_clingo_partial_discharge_v3.py (DEC-001 universal, DEC-016
valid_outcome, DEC-017 covers/guarantee). Single source of truth so the
producer and consumer tooling run the *same* engine the project's demos do.

If the project ruleset changes, re-lift this constant; do not edit it here to
diverge from the demo of record.
"""
import clingo

BASE_SHARED = r"""
active_edge(E,T,F,To) :- edge(E,T,F,To), not inactive(E).
is_parent(R) :- edge(_, refines, _, R).
leaf(R)      :- node(R, requirement), not is_parent(R).
has_active_verifies(R)   :- active_edge(_, verifies,   _, R).
has_active_implements(R) :- active_edge(_, implements, _, R).

% --- DEC-016: an outcome is valid evidence only with BOTH edges ---
valid_outcome(O) :- active_edge(_, confirms, O, _), active_edge(_, witnesses, O, _).

% --- DEC-001 universal: spec ok iff >=1 valid confirming outcome AND
%     no valid confirming outcome is an unwaived non-PASS ---
waived(O)      :- active_edge(_, excuses, _, O).
spec_fails(TS) :- active_edge(_, confirms, O, TS), valid_outcome(O),
                  node_field(O, outcome, V), V != "PASS", not waived(O).
spec_ok(TS)    :- active_edge(_, confirms, O, TS), valid_outcome(O), not spec_fails(TS).

has_unmet_spec(R) :- active_edge(_, verifies, TS, R), not spec_ok(TS).
unsatisfied(R) :- node(R, requirement), has_unmet_spec(R).
unsatisfied(R) :- is_parent(R), active_edge(_, refines, C, R), unsatisfied(C).
unsatisfied(R) :- is_parent(R), edge(E, refines, _, R), inactive(E).
satisfied(R)   :- node(R, requirement), not unsatisfied(R), not obligation(R).

% --- DEC-018: `obligation` is the node-level verdict state for an open
%     condition-of-use, distinct from the structural `residual`. Precedence
%     unsatisfied > obligation > satisfied (a failing test is a gap regardless
%     of how the node was published). `obligation`/`satisfied` are reported-only
%     -- no rule body reads them, so the proof verdict is unchanged. ---
obligation(R)  :- residual(R), not unsatisfied(R).
"""
LEAF_COMP = r"""
unsatisfied(R) :- leaf(R), not has_active_verifies(R),   not discharged_otherwise(R).
unsatisfied(R) :- leaf(R), not has_active_implements(R), not discharged_otherwise(R).
"""
COMPOSITION = r"""
discharged_by_review(R) :- active_edge(_, reviews, _, R).
covered(R)          :- active_edge(_, covers, _, R).
referenced(N)       :- referenced_under(N, _).
reliance_seal_ok(R) :- active_edge(_, covers, G, R), referenced_under(G, M), seal_ok(M).
impl_uses(M)        :- active_edge(_, uses, _, M).
reliance_uses_ok(R) :- active_edge(_, covers, G, R), referenced_under(G, M), impl_uses(M).
residual(C) :- edge(_, assumes, G, C), not referenced(G).
discharged_otherwise(R) :- discharged_by_review(R).
discharged_otherwise(R) :- covered(R).
discharged_otherwise(R) :- residual(R).
unsatisfied(R) :- covered(R), not reliance_seal_ok(R).
unsatisfied(R) :- covered(R), not reliance_uses_ok(R).
unsatisfied(R) :- active_edge(_, covers, G, R), edge(_, assumes, G, C), unsatisfied(C).
"""
ROLLUP = r"""
product(R)         :- node(R, requirement), not referenced(R).
has_product        :- product(_).
proof_unsatisfied  :- product(R), unsatisfied(R).
proof_has_residual :- residual(_).
proof_total        :- has_product, not proof_unsatisfied, not proof_has_residual.
proof_conditional  :- not proof_unsatisfied, proof_has_residual.
"""
PROG = BASE_SHARED + LEAF_COMP + COMPOSITION + ROLLUP

DEFS = """
#defined node/2. #defined edge/4. #defined node_field/3. #defined inactive/1.
#defined referenced_under/2. #defined seal_ok/1.
"""
SHOW = ("#show satisfied/1.\n#show unsatisfied/1.\n#show residual/1.\n#show obligation/1.\n#show product/1.\n"
        "#show proof_total/0.\n#show proof_conditional/0.\n#show proof_unsatisfied/0.\n")


def solve(facts):
    """Return the list of stable models (each a frozenset of shown-atom strings)."""
    ctl = clingo.Control(["0"])
    ctl.add("base", [], DEFS + PROG + facts + SHOW)
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(
        frozenset(str(a) for a in m.symbols(shown=True))))
    return models
