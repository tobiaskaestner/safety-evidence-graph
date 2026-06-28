"""
seg_demo_clingo_forward_v1.py
=============================
G9 gate -- the load-bearing composability finding.

GAPS G9: today an undischarged *inherited* condition stays `unsatisfied` and
POISONS the reliance via the sealed-condition rule

    unsatisfied(R) :- active_edge(_, covers, G, R), edge(_, assumes, G, C), unsatisfied(C).

so a mid-chain integrator that discharges *some but not all* imported assumptions
fails outright (proof_unsatisfied) instead of staying CONDITIONAL and re-publishing
the remainder -- contradicting DEC-015's re-publish intent and DEC-018's diagnostic note.

This gate HITS THE FAILURE FIRST (S1, as-is engine), then exhibits a candidate fix
for ratification (S2-S5, fixed engine). It changes NO durable artifact and logs NO
decision; it is the propose/explore step.

Ratified vocabulary (this session): the relation is `forward`; derived concept
`forwarded/1`; the affirmation gate is `forward_ok(R,C)`. The rollup keys on
`condition_of_use/1` = `residual` UNION `forwarded` (a project-chosen readable
label for the published-A_up set; the standards' verbatim term is "assumption(s)
of use"), generalizing the old residual-only `proof_has_residual`.

Candidate semantics under test
------------------------------
A forward is DELIBERATE and AFFIRMED, not a bare edge (parallel to reliance's
`seal_ok` gate). An *affirmed* forward of an inherited condition C:
  - turns C from a local gap into a discharged-as-forwarded condition (un-poisons R), and
  - surfaces C as an open condition-of-use carried onward -> proof_conditional.
A silent drop (no forward edge) or an UNAFFIRMED forward edge stays a gap (S3/S4),
and a genuine in-scope gap still dominates (S5) -- a forward can never launder a
real failure (DEC-015: unsatisfied > conditional).

Run: python seg_demo_clingo_forward_v1.py   (needs clingo; engine lifted from seg_ruleset)
"""
import clingo
import seg_ruleset as R   # the engine the demos-of-record run (AS-IS baseline)

# ----------------------------------------------------------------------------
# FIXED engine = the verbatim seg_ruleset BASE/LEAF/COMPOSITION + a FORWARD
# block + a RE-KEYED rollup. The rollup unions residual and forwarded under
# `condition_of_use/1` (option b), so a forwarded condition makes the proof
# CONDITIONAL without being mislabelled a `residual` (DEC-018 keeps forwarded
# referenced, hence not-a-residual). Inert when no forward facts are present
# (proven by the INVARIANCE check below).
# ----------------------------------------------------------------------------
FORWARD = r"""
% --- G9 candidate: forward (re-publish) of an inherited, undischarged condition ---
% forward_ok(R,C): R carries an AFFIRMED forward of inherited condition C.
%   The affirmation (`affirmed_forward`), not the bare `forward` edge, is load-bearing
%   -- mirrors reliance, where the `covers` edge alone is inert without `seal_ok`.
forward_ok(R,C) :- active_edge(_, forward, R, C), affirmed_forward(R,C).
forwarded(C)    :- forward_ok(_, C).

% A forwarded inherited condition is no longer a LOCAL gap: discharged-as-forwarded.
% Reuses `discharged_otherwise` (which already carries the structurally-published
% `residual`), so the leaf-incompleteness rules are suppressed -> unsatisfied(C)
% does not fire -> the poison rule never triggers.
discharged_otherwise(C) :- forwarded(C).

% ...and it reads as an open condition-of-use at the node level (DEC-018:
% "an inherited, re-published condition is referenced -- so not a residual --
%  yet must still read as an obligation").
obligation(C) :- forwarded(C), not unsatisfied(C).
"""

# Re-keyed rollup (option b). product/has_product/proof_unsatisfied are byte-identical
# to seg_ruleset.ROLLUP; only the published-condition middle term is generalized.
FIXED_ROLLUP = r"""
product(R)         :- node(R, requirement), not referenced(R).
has_product        :- product(_).
proof_unsatisfied  :- product(R), unsatisfied(R).
condition_of_use(C) :- residual(C).
condition_of_use(C) :- forwarded(C).
proof_has_condition_of_use :- condition_of_use(_).
proof_total        :- has_product, not proof_unsatisfied, not proof_has_condition_of_use.
proof_conditional  :- not proof_unsatisfied, proof_has_condition_of_use.
"""

FIXED_PROG = R.BASE_SHARED + R.LEAF_COMP + R.COMPOSITION + FORWARD + FIXED_ROLLUP
FIXED_DEFS = R.DEFS + "#defined forward/4. #defined affirmed_forward/2.\n"
FIXED_SHOW = (R.SHOW + "#show forwarded/1.\n#show forward_ok/2.\n"
              "#show condition_of_use/1.\n")


def solve_fixed(facts):
    ctl = clingo.Control(["0"])
    ctl.add("base", [], FIXED_DEFS + FIXED_PROG + facts + FIXED_SHOW)
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(
        frozenset(str(a) for a in m.symbols(shown=True))))
    return models


# ----------------------------------------------------------------------------
# Fixture: a mid-chain integrator.
#   d_sys   -- the integrator's top-level requirement (a product; in scope).
#   g_up    -- imported upstream guarantee, sealed under manifest m1 (DEC-017/020).
#   c_inh   -- inherited condition, referenced under m1, assumed by g_up.
#   covers(g_up, d_sys) -- the reliance; seal verifies and impl is linked, so the
#                          ONLY possible failure is the undischarged inherited c_inh.
# ----------------------------------------------------------------------------
BASE = """
node(d_sys, requirement).
node(g_up, guarantee).
node(c_inh, requirement).
edge(cv1, covers, g_up, d_sys).
edge(as1, assumes, g_up, c_inh).
referenced_under(g_up, m1).
referenced_under(c_inh, m1).
seal_ok(m1).
edge(us1, uses, impl_int, m1).
"""

FORWARD_EDGE   = "edge(fwd1, forward, d_sys, c_inh).\n"
FORWARD_AFFIRM = "affirmed_forward(d_sys, c_inh).\n"

# A genuine, independent in-scope gap on d_sys (failing verified test).
LOCAL_GAP = """
edge(vf1, verifies, ts_d, d_sys).
edge(cf1, confirms, ofail, ts_d).
edge(wf1, witnesses, ofail, impl_d).
node_field(ofail, outcome, "FAIL").
"""


def proof_state(model):
    if "proof_unsatisfied" in model: return "unsatisfied"
    if "proof_conditional" in model: return "conditional"
    if "proof_total" in model:       return "total"
    return "??"


def shown(model, pred):
    return sorted(a for a in model if a.startswith(pred))


def report(tag, model):
    st = proof_state(model)
    uns = [a[len("unsatisfied("):-1] for a in shown(model, "unsatisfied(")]
    fwd = [a[len("forwarded("):-1] for a in shown(model, "forwarded(")]
    cou = [a[len("condition_of_use("):-1] for a in shown(model, "condition_of_use(")]
    print(f"  {tag:<46} proof={st:<12} unsatisfied={uns or '(none)'}"
          f"  forwarded={fwd or '(none)'}  cou={cou or '(none)'}")
    return st


def single(models):
    assert len(models) == 1, f"determinism guardrail: expected 1 answer set, got {len(models)}"
    return models[0]


if __name__ == "__main__":
    print("G9 forward (re-publish) gate -- failure first, then candidate fix\n")

    # ---- S1: reproduce the failure on the AS-IS engine -----------------------
    m_s1 = single(R.solve(BASE))
    s1 = report("S1 as-is engine, inherited c_inh undischarged", m_s1)
    assert s1 == "unsatisfied", "S1 must reproduce the G9 poison"
    assert "unsatisfied(d_sys)" in m_s1 and "unsatisfied(c_inh)" in m_s1

    # ---- INVARIANCE: fixed engine == as-is when no forward facts present -----
    m_inv = single(solve_fixed(BASE))
    assert m_inv == m_s1, "fixed engine must be byte-identical to as-is absent forward facts"
    print("  INVARIANCE  fixed engine == as-is on BASE (forward block inert)         OK")

    # ---- S2: affirmed forward -> conditional + re-published condition-of-use --
    m_s2 = single(solve_fixed(BASE + FORWARD_EDGE + FORWARD_AFFIRM))
    s2 = report("S2 fixed, affirmed forward of c_inh", m_s2)
    assert s2 == "conditional"
    assert "forwarded(c_inh)" in m_s2
    assert "condition_of_use(c_inh)" in m_s2
    assert "obligation(c_inh)" in m_s2
    assert "unsatisfied(d_sys)" not in m_s2 and "unsatisfied(c_inh)" not in m_s2

    # ---- S3: silent drop (no forward edge) stays a gap ------------------------
    m_s3 = single(solve_fixed(BASE))
    s3 = report("S3 fixed, no forward edge (silent drop)", m_s3)
    assert s3 == "unsatisfied", "a dropped condition is NOT conditional"

    # ---- S4: forward edge present but UNAFFIRMED -> still a gap ---------------
    m_s4 = single(solve_fixed(BASE + FORWARD_EDGE))   # no affirmed_forward
    s4 = report("S4 fixed, forward edge present but UNAFFIRMED", m_s4)
    assert s4 == "unsatisfied", "the affirmation, not the bare edge, must be load-bearing"
    assert "forwarded(c_inh)" not in m_s4

    # ---- S5: affirmed forward + a genuine in-scope gap -> dominance ----------
    m_s5 = single(solve_fixed(BASE + FORWARD_EDGE + FORWARD_AFFIRM + LOCAL_GAP))
    s5 = report("S5 fixed, affirmed forward + genuine local gap", m_s5)
    assert s5 == "unsatisfied", "a forward must never launder a genuine gap"
    assert "forwarded(c_inh)" in m_s5            # the forward still holds...
    assert "proof_conditional" not in m_s5       # ...but unsatisfied dominates

    print("\nOK: 5/5. S1 reproduces G9; affirmed forward -> conditional (S2);"
          " drop (S3) and unaffirmed edge (S4) stay gaps; genuine gap dominates (S5).")
