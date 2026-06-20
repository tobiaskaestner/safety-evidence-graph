#!/usr/bin/env python3
"""
seg_demo_clingo_partial_discharge_v2.py

SELF-CONTAINED three-state proof-verdict demo. Supersedes
seg_demo_clingo_partial_discharge_v1.py (which may now be discarded): every
scenario it tested is duplicated here, plus the scenarios that exercise this
session's two ruleset corrections.

Verdict states (scope-aware rollup over PRODUCT / in-scope requirements):
  product(R)        := local requirement (not embedded by reference)
  proof_unsatisfied := some product requirement is unsatisfied (a genuine gap)
  proof_total       := no product gap AND nothing published as A_up
  proof_conditional := no product gap BUT some residual published as A_up

Ruleset corrections folded in vs v1:
  [DEC-001 universal]  spec_ok was EXISTENTIAL ("some confirming outcome PASS").
                       It is now the DEC-001 UNIVERSAL: a spec is ok iff it has
                       >=1 valid confirming outcome AND no valid confirming
                       outcome is an unwaived non-PASS. Adds waiver (`excuses`)
                       handling, absent in v1.
  [DEC-016 valid_outcome] a Test Outcome counts as evidence only if it carries
                       BOTH a `confirms` and a `witnesses` edge. Incomplete
                       outcomes are DISCARDED (treated as absent), mirroring the
                       projection-time discard of stale outcomes. This is a
                       VERDICT-layer check, not SHACL (SHACL enforces no node
                       mandatory-edge-presence).

Correction 3 (DEC-017) APPLIED in this file: G_up is re-typed `requirement` ->
`guarantee`, the reliance edge is flipped `relies_on(R,G)` -> `covers(G,R)`, and the
concept predicate `reliance/1` is renamed `covered/1`. The four verdict clauses are
re-keyed `relies_on, R, G` -> `covers, G, R`; the `reliance_*_ok` helpers keep their
stem (they name the check on a reliance). Because `guarantee` is outside the
satisfaction domain (every rule head is `node(R, requirement)`), the spurious
`unsatisfied(g_up)` of the v2 file is gone -- see scenario 4. Verdict-invariance vs the
v2 (`relies_on`) form was proven side-by-side in
seg_demo_clingo_covers_invariance_v1.py (19/19).

Field convention: outcome result is `node_field(O, outcome, "PASS"|"FAIL"|...)`,
matching design-summary 2.4. NOTE the value is a STRING ("PASS") because a bare
uppercase PASS is a clingo VARIABLE, not a constant.

A malformed outcome that lacks its `outcome` field is out of scope here: node
well-formedness (required fields) is SHACL's job per DEC-016. Every fixture
outcome below carries its field.

Requires: pip install clingo ;  Run: python3 seg_demo_clingo_partial_discharge_v2.py
"""
import sys
try:
    import clingo
except ImportError:
    sys.exit("clingo not installed - run: pip install clingo")

# ============================ THE RULESET ===================================
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
satisfied(R)   :- node(R, requirement), not unsatisfied(R).
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
SHOW = ("#show satisfied/1.\n#show unsatisfied/1.\n#show residual/1.\n#show product/1.\n"
        "#show proof_total/0.\n#show proof_conditional/0.\n#show proof_unsatisfied/0.\n")

def solve(facts):
    ctl = clingo.Control(["0"])           # 0 = enumerate ALL stable models
    ctl.add("base", [], DEFS + PROG + facts + SHOW)
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(
        frozenset(str(a) for a in m.symbols(shown=True))))
    return models

def has(model, atom): return atom in model
def pick(model, pfx):  return sorted(a for a in model if a.startswith(pfx))
def report(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    return ok

allok = True

# ============================ FIXTURES ======================================
# Product r_sys refines into r_drv (mode-2 reliance, both CoUs reviewed) and
# r_app (mode-1 by test). g_up/cou1/cou2 are referenced (sealed upstream).
# toa carries BOTH confirms and witnesses (DEC-016); its result is appended
# separately so a scenario can flip PASS<->FAIL.
PARTIAL_BASE = """
node(r_sys, requirement). node(r_drv, requirement). node(r_app, requirement).
edge(fd, refines, r_drv, r_sys). edge(fa, refines, r_app, r_sys).
node(g_up, guarantee). node(cou1, requirement). node(cou2, requirement).
edge(er, covers, g_up, r_drv).
referenced_under(g_up, man). referenced_under(cou1, man). referenced_under(cou2, man).
node(man, manifest). node_field(man, component_iri, rtosx). seal_ok(man).
node(impl1, implementation). edge(eu, uses, impl1, man).
edge(ea1, assumes, g_up, cou1). edge(ea2, assumes, g_up, cou2).
node(dr1, designreview). edge(ev1, reviews, dr1, cou1).
node(dr2, designreview). edge(ev2, reviews, dr2, cou2).
node(tsa, testspecification). node(ima, implementation). node(toa, testoutcome).
edge(va, verifies, tsa, r_app). edge(ia, implements, ima, r_app).
edge(ca, confirms, toa, tsa). edge(wa, witnesses, toa, ima).
"""
TOA_PASS = 'node_field(toa, outcome, "PASS").\n'
TOA_FAIL = 'node_field(toa, outcome, "FAIL").\n'
# The product publishes its OWN condition of use (local authored assumes) = A_up.
PUBLISHED = "node(c_pub, requirement). edge(eap, assumes, r_sys, c_pub).\n"

# ---- carried-over scenarios (were in v1) ----------------------------------
print("1. TOTAL (everything discharged, nothing published)   [carried]")
m = solve(PARTIAL_BASE + TOA_PASS)
ok = (len(m) == 1 and has(m[0], "proof_total")
      and not has(m[0], "proof_conditional") and not has(m[0], "proof_unsatisfied")
      and not pick(m[0], "residual("))
allok &= report("proof = total", ok, f"product={[a[8:-1] for a in pick(m[0],'product(')]}")

print("2. CONDITIONAL (one condition published as A_up)       [carried]")
m = solve(PARTIAL_BASE + TOA_PASS + PUBLISHED)
ok = (len(m) == 1 and has(m[0], "proof_conditional")
      and not has(m[0], "proof_total") and not has(m[0], "proof_unsatisfied")
      and has(m[0], "residual(c_pub)") and has(m[0], "satisfied(c_pub)"))
allok &= report("proof = conditional; residual={c_pub}; product all satisfied", ok)

print("3. UNSATISFIED DOMINATES (a real gap + a published condition)  [carried]")
m = solve(PARTIAL_BASE + TOA_FAIL + PUBLISHED)   # r_app's spec FAILs => r_sys unsatisfied
ok = (len(m) == 1 and has(m[0], "proof_unsatisfied")
      and not has(m[0], "proof_conditional") and not has(m[0], "proof_total"))
allok &= report("a residual cannot hide a genuine gap -> unsatisfied", ok)

print("4. SCOPE (G_up is a Guarantee -> outside the satisfaction domain)  [DEC-017]")
m = solve(PARTIAL_BASE + TOA_PASS)
ok = (len(m) == 1
      and not has(m[0], "unsatisfied(g_up)")     # the v2 spurious atom is gone at the source
      and not has(m[0], "satisfied(g_up)")
      and not has(m[0], "product(g_up)")
      and has(m[0], "proof_total"))
allok &= report("g_up carries no verdict atom (typed Guarantee); proof still total", ok)

print("5. EMPTY SCOPE GUARD (no product requirements -> NOT vacuously total)  [carried]")
EMPTY = 'node(g_only, guarantee). referenced_under(g_only, mx). node(mx, manifest). seal_ok(mx).\n'
m = solve(EMPTY)
ok = len(m) == 1 and not has(m[0], "proof_total") and not has(m[0], "proof_conditional")
allok &= report("no false 'total' on an all-referenced graph", ok)

# ---- net-new scenarios (exercise the two corrections) ---------------------
# 6 & 7: DEC-001 universal + waiver. ts_x has one PASS and one FAIL outcome,
# both VALID (each has confirms + witnesses), so the validity gate is not what's
# being tested -- the universal is.
UNIVERSAL = """
node(r_x, requirement).
node(ts_x, testspecification). node(im_x, implementation).
edge(vx, verifies, ts_x, r_x). edge(ix, implements, im_x, r_x).
node(to_pass, testoutcome). edge(cp, confirms, to_pass, ts_x). edge(wp, witnesses, to_pass, im_x).
node(to_fail, testoutcome). edge(cf, confirms, to_fail, ts_x). edge(wf, witnesses, to_fail, im_x).
""" + 'node_field(to_pass, outcome, "PASS"). node_field(to_fail, outcome, "FAIL").\n'

print("6. UNIVERSAL (one PASS + one unwaived FAIL -> unsatisfied)   [net-new: DEC-001]")
m = solve(UNIVERSAL)
ok = (len(m) == 1 and has(m[0], "unsatisfied(r_x)") and not has(m[0], "satisfied(r_x)")
      and has(m[0], "proof_unsatisfied"))
allok &= report("existential would wrongly pass; universal fails it", ok)

print("7. WAIVER (the FAIL is validly waived -> satisfied)          [net-new: DEC-001]")
WAIVED = UNIVERSAL + "node(wv_x, waiver). edge(ex, excuses, wv_x, to_fail).\n"
m = solve(WAIVED)
ok = (len(m) == 1 and has(m[0], "satisfied(r_x)") and not has(m[0], "unsatisfied(r_x)")
      and has(m[0], "proof_total"))
allok &= report("excused FAIL no longer blocks; proof total", ok)

print("8. INCOMPLETE OUTCOME (confirms but no witnesses -> unsatisfied)  [net-new: DEC-016]")
INCOMPLETE = """
node(r_y, requirement).
node(ts_y, testspecification). node(im_y, implementation).
edge(vy, verifies, ts_y, r_y). edge(iy, implements, im_y, r_y).
node(to_y, testoutcome). edge(cy, confirms, to_y, ts_y).
""" + 'node_field(to_y, outcome, "PASS").\n'   # NO witnesses edge => not valid_outcome
m = solve(INCOMPLETE)
ok = (len(m) == 1 and has(m[0], "unsatisfied(r_y)") and has(m[0], "proof_unsatisfied"))
allok &= report("incomplete evidence discarded -> coverage gap", ok)

print("9. ENFORCE-IF-PRESENT A (non-leaf's own failing spec blocks it)  [net-new]")
# r_par's child r_ch is fully satisfied, but r_par carries a direct verifies to a FAILing spec.
EIP_A = """
node(r_par, requirement). node(r_ch, requirement).
edge(fp, refines, r_ch, r_par).
node(ts_c, testspecification). node(im_c, implementation). node(to_c, testoutcome).
edge(vc, verifies, ts_c, r_ch). edge(ic, implements, im_c, r_ch).
edge(cc, confirms, to_c, ts_c). edge(wc, witnesses, to_c, im_c).
node(ts_p, testspecification). node(im_p, implementation). node(to_p, testoutcome).
edge(vp, verifies, ts_p, r_par). edge(ip, implements, im_p, r_par).
edge(cpp, confirms, to_p, ts_p). edge(wpp, witnesses, to_p, im_p).
""" + 'node_field(to_c, outcome, "PASS"). node_field(to_p, outcome, "FAIL").\n'
m = solve(EIP_A)
ok = (len(m) == 1 and has(m[0], "satisfied(r_ch)")
      and has(m[0], "unsatisfied(r_par)") and has(m[0], "proof_unsatisfied"))
allok &= report("present failing direct edge on a non-leaf is enforced", ok)

print("10. ENFORCE-IF-PRESENT B (passing own coverage does NOT override a failing child)  [net-new]")
# r_par2 has its OWN passing coverage, child r_ok satisfied, child r_bad unsatisfied.
EIP_B = """
node(r_par2, requirement). node(r_ok, requirement). node(r_bad, requirement).
edge(fo, refines, r_ok, r_par2). edge(fb, refines, r_bad, r_par2).
node(ts_o, testspecification). node(im_o, implementation). node(to_o, testoutcome).
edge(vo, verifies, ts_o, r_ok). edge(io, implements, im_o, r_ok).
edge(co, confirms, to_o, ts_o). edge(wo, witnesses, to_o, im_o).
node(ts_b, testspecification). node(im_b, implementation). node(to_b, testoutcome).
edge(vb, verifies, ts_b, r_bad). edge(ib, implements, im_b, r_bad).
edge(cb, confirms, to_b, ts_b). edge(wb, witnesses, to_b, im_b).
node(ts_p2, testspecification). node(im_p2, implementation). node(to_p2, testoutcome).
edge(vp2, verifies, ts_p2, r_par2). edge(ip2, implements, im_p2, r_par2).
edge(cp2, confirms, to_p2, ts_p2). edge(wp2, witnesses, to_p2, im_p2).
""" + ('node_field(to_o, outcome, "PASS"). node_field(to_b, outcome, "FAIL"). '
       'node_field(to_p2, outcome, "PASS").\n')
m = solve(EIP_B)
ok = (len(m) == 1 and has(m[0], "satisfied(r_ok)") and has(m[0], "unsatisfied(r_bad)")
      and has(m[0], "unsatisfied(r_par2)") and has(m[0], "proof_unsatisfied"))
allok &= report("discharge does not override children", ok)

print("\n" + ("ALL PASS" if allok else "SOME FAILED"))
sys.exit(0 if allok else 1)
