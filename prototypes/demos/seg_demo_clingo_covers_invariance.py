#!/usr/bin/env python3
"""
seg_demo_clingo_covers_invariance_v1.py

DEC-017 VALIDATION GATE (run before any doc/grammar edit).

Proves the Correction-3 re-wire is VERDICT-PRESERVING. The re-wire is three linked
changes:
  (M1) re-type the imported upstream guarantee  node(g_up, requirement) -> node(g_up, guarantee)
  (M2) flip the reliance edge                    relies_on(R, G_up)      -> covers(G_up, R)
  (rename) the concept predicate                 reliance/1              -> covered/1
and the four verdict clauses that join on the edge are re-keyed accordingly
(`relies_on, R, G` -> `covers, G, R`).

CLAIM under test: every three-state verdict is unchanged, the ONLY intended
difference being that the spurious `unsatisfied(g_up)` atom -- previously derived
(g_up was a leaf Requirement with no coverage) and then masked by the
product/referenced scope split -- DISAPPEARS at the source, because a `guarantee`
node is not in the domain of the satisfaction recursion.

METHOD (side-by-side): for each scenario, run the OLD ruleset on the OLD facts and
the NEW ruleset on the NEW facts (facts transformed by M1+M2), then assert the shown
verdict atoms are identical after removing atoms that mention the re-typed guarantee
node(s) -- AND that the guarantee delta is exactly as predicted (OLD derives
`unsatisfied(<g>)`; NEW derives no verdict atom about <g>).

SCOPE: mirrors BOTH authoritative demos under their OWN conventions, so it re-proves
10/10 + 9/9 hold under the new rules and that each is byte-equal (mod the g delta):
  - partial_discharge_v2 convention: DEC-016 `valid_outcome` + DEC-001 universal; 10 scenarios.
  - composition_v2 convention:      symbolic-field base + the acyclic-facet STRUCT check; 9 scenarios.
Both baselines were confirmed (10/10, 9/9) immediately before this gate was written.

>>> FINDING surfaced by this gate (NOT in DEC-017 consequence #2 as first drafted):
    the edge flip forces a FIFTH change, in the structural acyclic-facet check (STRUCT),
    not among the four verdict clauses. STRUCT must re-key its reliance clause so the
    DEPENDENCY-graph orientation is preserved:
        OLD  struct_edge(F,To) :- edge(_, relies_on, F, To).   % relies_on(R,G):  R -> G
        NEW  struct_edge(R,G)  :- edge(_, covers,    G, R).    % covers(G,R): same R -> G
    Rationale: the struct graph encodes "R's discharge depends on G". With the surface
    edge flipped to covers(G,R), a NAIVE `struct_edge(F,To) :- covers F To` would make
    `covers` and `assumes` BOTH point G->R, collapsing the reliance 2-cycle to a single
    direction so cycle detection silently fails. Scenario C9b demonstrates that break;
    C9 shows the corrected rule restores byte-identical STRUCT output.
    (Demo convention: lowercase symbolic node types; the .dsl/SHACL uses the string
    "Guarantee". `inactive/1` is shorthand for edge_state != active.)

Requires: pip install clingo ;  Run: python3 seg_demo_clingo_covers_invariance_v1.py
"""
import sys, re
try:
    import clingo
except ImportError:
    sys.exit("clingo not installed - run: pip install clingo")

# =================== fact transform: OLD facts -> NEW facts ===================
def to_new(facts, guarantees):
    """M1: re-type each named guarantee node requirement->guarantee.
       M2: flip every relies_on(R,G) edge to covers(G,R)."""
    out = facts
    for g in guarantees:
        out = re.sub(rf"node\(\s*{g}\s*,\s*requirement\s*\)", f"node({g}, guarantee)", out)
    out = re.sub(r"relies_on,\s*(\w+),\s*(\w+)", r"covers, \2, \1", out)   # edge(E, relies_on, R, G) -> edge(E, covers, G, R)
    return out

# ============================ partial_discharge convention ====================
PD_BASE = r"""
active_edge(E,T,F,To) :- edge(E,T,F,To), not inactive(E).
is_parent(R) :- edge(_, refines, _, R).
leaf(R)      :- node(R, requirement), not is_parent(R).
has_active_verifies(R)   :- active_edge(_, verifies,   _, R).
has_active_implements(R) :- active_edge(_, implements, _, R).
valid_outcome(O) :- active_edge(_, confirms, O, _), active_edge(_, witnesses, O, _).
waived(O)      :- active_edge(_, excuses, _, O).
spec_fails(TS) :- active_edge(_, confirms, O, TS), valid_outcome(O),
                  node_field(O, outcome, V), V != "PASS", not waived(O).
spec_ok(TS)    :- active_edge(_, confirms, O, TS), valid_outcome(O), not spec_fails(TS).
has_unmet_spec(R) :- active_edge(_, verifies, TS, R), not spec_ok(TS).
unsatisfied(R) :- node(R, requirement), has_unmet_spec(R).
unsatisfied(R) :- is_parent(R), active_edge(_, refines, C, R), unsatisfied(C).
unsatisfied(R) :- is_parent(R), edge(E, refines, _, R), inactive(E).
satisfied(R)   :- node(R, requirement), not unsatisfied(R).
unsatisfied(R) :- leaf(R), not has_active_verifies(R),   not discharged_otherwise(R).
unsatisfied(R) :- leaf(R), not has_active_implements(R), not discharged_otherwise(R).
"""
PD_ROLLUP = r"""
product(R)         :- node(R, requirement), not referenced(R).
has_product        :- product(_).
proof_unsatisfied  :- product(R), unsatisfied(R).
proof_has_residual :- residual(_).
proof_total        :- has_product, not proof_unsatisfied, not proof_has_residual.
proof_conditional  :- not proof_unsatisfied, proof_has_residual.
"""
PD_COMP_OLD = r"""
discharged_by_review(R) :- active_edge(_, reviews, _, R).
reliance(R)         :- active_edge(_, relies_on, R, _).
referenced(N)       :- referenced_under(N, _).
reliance_seal_ok(R) :- active_edge(_, relies_on, R, G), referenced_under(G, M), seal_ok(M).
impl_uses(M)        :- active_edge(_, uses, _, M).
reliance_uses_ok(R) :- active_edge(_, relies_on, R, G), referenced_under(G, M), impl_uses(M).
residual(C) :- edge(_, assumes, G, C), not referenced(G).
discharged_otherwise(R) :- discharged_by_review(R).
discharged_otherwise(R) :- reliance(R).
discharged_otherwise(R) :- residual(R).
unsatisfied(R) :- reliance(R), not reliance_seal_ok(R).
unsatisfied(R) :- reliance(R), not reliance_uses_ok(R).
unsatisfied(R) :- active_edge(_, relies_on, R, G), edge(_, assumes, G, C), unsatisfied(C).
"""
PD_COMP_NEW = r"""
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
PD_SHOW = ("#show satisfied/1.\n#show unsatisfied/1.\n#show residual/1.\n#show product/1.\n"
           "#show proof_total/0.\n#show proof_conditional/0.\n#show proof_unsatisfied/0.\n")
PD_OLD = PD_BASE + PD_COMP_OLD + PD_ROLLUP
PD_NEW = PD_BASE + PD_COMP_NEW + PD_ROLLUP

# ============================ composition convention ==========================
C_BASE = r"""
active_edge(E,T,F,To) :- edge(E,T,F,To), not inactive(E).
is_parent(R) :- edge(_, refines, _, R).
leaf(R)      :- node(R, requirement), not is_parent(R).
has_active_verifies(R)   :- active_edge(_, verifies,   _, R).
has_active_implements(R) :- active_edge(_, implements, _, R).
spec_ok(TS) :- active_edge(_, confirms, O, TS), node_field(O, result, pass).
has_unmet_spec(R) :- active_edge(_, verifies, TS, R), not spec_ok(TS).
unsatisfied(R) :- node(R, requirement), has_unmet_spec(R).
unsatisfied(R) :- is_parent(R), active_edge(_, refines, C, R), unsatisfied(C).
unsatisfied(R) :- is_parent(R), edge(E, refines, _, R), inactive(E).
satisfied(R) :- node(R, requirement), not unsatisfied(R).
unsatisfied(R) :- leaf(R), not has_active_verifies(R),   not discharged_otherwise(R).
unsatisfied(R) :- leaf(R), not has_active_implements(R), not discharged_otherwise(R).
"""
C_COMP_OLD = r"""
discharged_by_review(R) :- active_edge(_, reviews, _, R).
reliance(R)         :- active_edge(_, relies_on, R, _).
referenced(N)       :- referenced_under(N, _).
reliance_seal_ok(R) :- active_edge(_, relies_on, R, G), referenced_under(G, M), seal_ok(M).
impl_uses(M)        :- active_edge(_, uses, _, M).
reliance_uses_ok(R) :- active_edge(_, relies_on, R, G), referenced_under(G, M), impl_uses(M).
residual(C) :- edge(_, assumes, G, C), not referenced(G).
discharged_otherwise(R) :- discharged_by_review(R).
discharged_otherwise(R) :- reliance(R).
discharged_otherwise(R) :- residual(R).
unsatisfied(R) :- reliance(R), not reliance_seal_ok(R).
unsatisfied(R) :- reliance(R), not reliance_uses_ok(R).
unsatisfied(R) :- active_edge(_, relies_on, R, G), edge(_, assumes, G, C), unsatisfied(C).
conditional_proof :- residual(_).
manifest_conflict(I) :- node(M1, manifest), node_field(M1, component_iri, I),
                        node(M2, manifest), node_field(M2, component_iri, I), M1 != M2.
ill_formed_reliance(R) :- reliance(R), is_parent(R).
"""
C_COMP_NEW = r"""
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
conditional_proof :- residual(_).
manifest_conflict(I) :- node(M1, manifest), node_field(M1, component_iri, I),
                        node(M2, manifest), node_field(M2, component_iri, I), M1 != M2.
ill_formed_reliance(R) :- covered(R), is_parent(R).
"""
C_SHOW = ("#show satisfied/1.\n#show unsatisfied/1.\n#show residual/1.\n"
          "#show conditional_proof/0.\n#show manifest_conflict/1.\n#show ill_formed_reliance/1.\n")
C_OLD = C_BASE + C_COMP_OLD
C_NEW = C_BASE + C_COMP_NEW

# acyclic-facet STRUCT check: OLD, NEW (corrected, orientation-preserving), NEW (naive, broken)
STRUCT_OLD = r"""
struct_edge(F,To) :- edge(_, refines,   F, To).
struct_edge(F,To) :- edge(_, relies_on, F, To).
struct_edge(F,To) :- edge(_, assumes,   F, To).
reach(X,Y) :- struct_edge(X,Y).
reach(X,Z) :- struct_edge(X,Y), reach(Y,Z).
cycle(X)   :- reach(X,X).
"""
STRUCT_NEW_OK = r"""
struct_edge(F,To) :- edge(_, refines, F, To).
struct_edge(R,G)  :- edge(_, covers,  G, R).        % orientation-preserving: covers(G,R) keeps R->G
struct_edge(F,To) :- edge(_, assumes, F, To).
reach(X,Y) :- struct_edge(X,Y).
reach(X,Z) :- struct_edge(X,Y), reach(Y,Z).
cycle(X)   :- reach(X,X).
"""
STRUCT_NEW_NAIVE = r"""
struct_edge(F,To) :- edge(_, refines, F, To).
struct_edge(F,To) :- edge(_, covers,  F, To).        % NAIVE: surface direction -> collapses the cycle
struct_edge(F,To) :- edge(_, assumes, F, To).
reach(X,Y) :- struct_edge(X,Y).
reach(X,Z) :- struct_edge(X,Y), reach(Y,Z).
cycle(X)   :- reach(X,X).
"""
STRUCT_SHOW = "#show cycle/1.\n"

DEFS = ("#defined node/2. #defined edge/4. #defined node_field/3. #defined inactive/1.\n"
        "#defined referenced_under/2. #defined seal_ok/1.\n")

def solve(rules, facts, show):
    ctl = clingo.Control(["0"])
    ctl.add("base", [], DEFS + rules + facts + show)
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(
        frozenset(str(a) for a in m.symbols(shown=True))))
    return models

def strip(atoms, nodes):
    """drop shown atoms that mention any of `nodes` (the re-typed guarantees)."""
    return frozenset(a for a in atoms
                     if not any(re.search(rf"\b{re.escape(n)}\b", a) for n in nodes))

def report(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    return ok

allok = True

def invariance(label, rules_old, rules_new, facts_old, guarantees, show):
    """Assert OLD(old facts) and NEW(new facts) give one model each, equal after
    stripping the guarantee nodes, and the predicted g-delta holds."""
    global allok
    facts_new = to_new(facts_old, guarantees)
    mo, mn = solve(rules_old, facts_old, show), solve(rules_new, facts_new, show)
    one = (len(mo) == 1 and len(mn) == 1)
    if not one:
        allok &= report(label, False, f"model counts old={len(mo)} new={len(mn)}")
        return
    so, sn = strip(mo[0], guarantees), strip(mn[0], guarantees)
    equal = (so == sn)
    # predicted delta: OLD derives unsatisfied(<g>) for each guarantee; NEW derives no atom about <g>
    delta_ok = True
    for g in guarantees:
        old_has = (f"unsatisfied({g})" in mo[0])
        new_none = not any(re.search(rf"\b{re.escape(g)}\b", a) for a in mn[0])
        delta_ok &= (old_has and new_none)
    detail = ""
    if not equal:
        detail = f"DIFF old\\new={sorted(so-sn)} new\\old={sorted(sn-so)}"
    elif guarantees:
        detail = f"identical mod {guarantees}; old had unsatisfied{tuple(guarantees)}, new clean"
    else:
        detail = "identical (import-free / no guarantee node)"
    allok &= report(label, equal and delta_ok, detail)

# ============================ FIXTURES (verbatim from the two demos) ==========
PARTIAL_BASE = """
node(r_sys, requirement). node(r_drv, requirement). node(r_app, requirement).
edge(fd, refines, r_drv, r_sys). edge(fa, refines, r_app, r_sys).
node(g_up, requirement). node(cou1, requirement). node(cou2, requirement).
edge(er, relies_on, r_drv, g_up).
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
PUBLISHED = "node(c_pub, requirement). edge(eap, assumes, r_sys, c_pub).\n"

UNIVERSAL = """
node(r_x, requirement).
node(ts_x, testspecification). node(im_x, implementation).
edge(vx, verifies, ts_x, r_x). edge(ix, implements, im_x, r_x).
node(to_pass, testoutcome). edge(cp, confirms, to_pass, ts_x). edge(wp, witnesses, to_pass, im_x).
node(to_fail, testoutcome). edge(cf, confirms, to_fail, ts_x). edge(wf, witnesses, to_fail, im_x).
""" + 'node_field(to_pass, outcome, "PASS"). node_field(to_fail, outcome, "FAIL").\n'
WAIVED = UNIVERSAL + "node(wv_x, waiver). edge(ex, excuses, wv_x, to_fail).\n"
INCOMPLETE = """
node(r_y, requirement).
node(ts_y, testspecification). node(im_y, implementation).
edge(vy, verifies, ts_y, r_y). edge(iy, implements, im_y, r_y).
node(to_y, testoutcome). edge(cy, confirms, to_y, ts_y).
""" + 'node_field(to_y, outcome, "PASS").\n'
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
EMPTY = 'node(g_only, requirement). referenced_under(g_only, mx). node(mx, manifest). seal_ok(mx).\n'

# composition-convention fixtures
IMPORT_FREE = """
node(r_top, requirement). node(r_a, requirement). node(r_b, requirement).
edge(efa, refines, r_a, r_top). edge(efb, refines, r_b, r_top).
node(tsa, testspecification). node(ima, implementation). node(toa, testoutcome).
edge(va, verifies, tsa, r_a). edge(ia, implements, ima, r_a).
edge(ca, confirms, toa, tsa). node_field(toa, result, pass).
node(tsb, testspecification). node(imb, implementation). node(tob, testoutcome).
edge(vb, verifies, tsb, r_b). edge(ib, implements, imb, r_b).
edge(cb, confirms, tob, tsb). node_field(tob, result, pass).
"""
RELIANCE_OK = """
node(r_prod, requirement).
node(g_up, requirement). node(cou1, requirement). node(cou2, requirement).
edge(er, relies_on, r_prod, g_up).
referenced_under(g_up, man). referenced_under(cou1, man). referenced_under(cou2, man).
node(man, manifest). node_field(man, component_iri, rtosx). seal_ok(man).
node(impl1, implementation). edge(eu, uses, impl1, man).
edge(ea1, assumes, g_up, cou1). edge(ea2, assumes, g_up, cou2).
node(dr1, designreview). edge(ev1, reviews, dr1, cou1).
node(dr2, designreview). edge(ev2, reviews, dr2, cou2).
"""
PUBLISH = """
node(r_pub, requirement). node(c_pub, requirement).
edge(eap, assumes, r_pub, c_pub).
node(tsp, testspecification). node(imp, implementation). node(top, testoutcome).
edge(vp, verifies, tsp, r_pub). edge(ip, implements, imp, r_pub).
edge(cp, confirms, top, tsp). node_field(top, result, pass).
"""
ILL = """
node(r_x, requirement). node(r_c, requirement). node(g2, requirement).
edge(efx, refines, r_c, r_x). edge(erx, relies_on, r_x, g2).
referenced_under(g2, m2). node(m2, manifest). seal_ok(m2).
node(ix, implementation). edge(eux, uses, ix, m2).
"""
CYCLE = """
node(r1, requirement). node(g1, requirement).
edge(erc, relies_on, r1, g1). edge(eac, assumes, g1, r1).
referenced_under(g1, manc). node(manc, manifest). seal_ok(manc).
node(implc, implementation). edge(euc, uses, implc, manc).
"""

# ================================ RUN =========================================
print("== partial_discharge convention (10 scenarios; verdict invariance mod g_up) ==")
invariance("P1  TOTAL",                 PD_OLD, PD_NEW, PARTIAL_BASE + TOA_PASS,             ["g_up"],   PD_SHOW)
invariance("P2  CONDITIONAL",           PD_OLD, PD_NEW, PARTIAL_BASE + TOA_PASS + PUBLISHED, ["g_up"],   PD_SHOW)
invariance("P3  UNSATISFIED DOMINATES", PD_OLD, PD_NEW, PARTIAL_BASE + TOA_FAIL + PUBLISHED, ["g_up"],   PD_SHOW)
invariance("P4  SCOPE (g_up delta)",    PD_OLD, PD_NEW, PARTIAL_BASE + TOA_PASS,             ["g_up"],   PD_SHOW)
invariance("P5  EMPTY-SCOPE GUARD",     PD_OLD, PD_NEW, EMPTY,                               ["g_only"], PD_SHOW)
invariance("P6  UNIVERSAL",             PD_OLD, PD_NEW, UNIVERSAL,                           [],         PD_SHOW)
invariance("P7  WAIVER",                PD_OLD, PD_NEW, WAIVED,                              [],         PD_SHOW)
invariance("P8  INCOMPLETE OUTCOME",    PD_OLD, PD_NEW, INCOMPLETE,                          [],         PD_SHOW)
invariance("P9  ENFORCE-IF-PRESENT A",  PD_OLD, PD_NEW, EIP_A,                               [],         PD_SHOW)
invariance("P10 ENFORCE-IF-PRESENT B",  PD_OLD, PD_NEW, EIP_B,                               [],         PD_SHOW)

print("\n== composition convention (9 scenarios; verdict invariance mod g_up) ==")
invariance("C1  CONSERVATIVITY",        C_OLD, C_NEW, IMPORT_FREE,                                   [],      C_SHOW)
invariance("C2  MODE-2 DISCHARGE",      C_OLD, C_NEW, RELIANCE_OK,                                   ["g_up"],C_SHOW)
invariance("C3  RE-SEAL DRIFT",         C_OLD, C_NEW, RELIANCE_OK.replace(" seal_ok(man).", ""),     ["g_up"],C_SHOW)
invariance("C4  MISSING CONDITION",     C_OLD, C_NEW,
           RELIANCE_OK.replace("node(dr2, designreview). edge(ev2, reviews, dr2, cou2).", ""),       ["g_up"],C_SHOW)
invariance("C5  IMPL-USE MISSING",      C_OLD, C_NEW,
           RELIANCE_OK.replace("node(impl1, implementation). edge(eu, uses, impl1, man).", ""),      ["g_up"],C_SHOW)
invariance("C6  PUBLISHED RESIDUAL",    C_OLD, C_NEW, PUBLISH,                                       [],      C_SHOW)
invariance("C7  VERSION CONSISTENCY",   C_OLD, C_NEW,
           RELIANCE_OK + "node(man2, manifest). node_field(man2, component_iri, rtosx).\n",          ["g_up"],C_SHOW)
invariance("C8  ILL-FORMED RELIANCE",   C_OLD, C_NEW, ILL,                                           ["g2"],  C_SHOW)
invariance("C9  WELL-FOUNDEDNESS (verdict: 1 model, mod g1)", C_OLD, C_NEW, CYCLE,                   ["g1"],  C_SHOW)

# ---- the FIFTH-change finding: structural acyclic-facet check under the flip ----
print("\n== acyclic-facet STRUCT check on the reliance cycle (the fifth-change finding) ==")
CYCLE_NEW = to_new(CYCLE, ["g1"])
mo  = solve(STRUCT_OLD,       CYCLE,     STRUCT_SHOW)
mok = solve(STRUCT_NEW_OK,    CYCLE_NEW, STRUCT_SHOW)
mnv = solve(STRUCT_NEW_NAIVE, CYCLE_NEW, STRUCT_SHOW)
old_cyc = mo  and any("cycle(r1)" in a for a in mo[0])
ok_cyc  = mok and any("cycle(r1)" in a for a in mok[0])
nv_cyc  = mnv and any("cycle(r1)" in a for a in mnv[0])
allok &= report("S-OLD   relies_on form flags cycle(r1)", old_cyc)
allok &= report("S-NEWok orientation-preserving covers form ALSO flags cycle(r1)", ok_cyc,
                "struct graph byte-identical to OLD")
allok &= report("S-NAIVE surface-direction covers form FAILS to flag (why the 5th change is needed)",
                (not nv_cyc), "cycle silently undetected -> must NOT ship this form")

print("\n" + ("ALL PASS  (re-wire is verdict-preserving; STRUCT needs the 5th-change fix)"
              if allok else "SOME FAILED"))
sys.exit(0 if allok else 1)
