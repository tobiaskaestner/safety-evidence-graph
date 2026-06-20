#!/usr/bin/env python3
"""
seg_demo_clingo_composition.py
 
Runnable check of the SEG composition extension (companion to
seg_composability_cbd.md sec 8-9), using clingo / ASP.
 
It encodes:
  - BASE rule-set (import-free): mode-1 discharge by a witness, and satisfaction by
    positive upward-failure propagation over the refines DAG (single top-level negation).
  - EXTENSION (guarded): the witness genus extended with DesignReview; mode-2 reliance
    discharge guarded by relies_on / manifest / references / assumes; and the
    version-consistency validation rule.
 
Each scenario asserts a property, so this doubles as a regression test:
  1. CONSERVATIVITY  - an import-free graph gets the SAME satisfied-set under BASE and
                       under BASE+EXTENSION (the guarded clauses are inert).
  2. MODE-2 DISCHARGE - a product requirement is satisfied by relying on an upstream
                       guarantee when seal_ok, impl-uses, and all assumed CoUs hold.
  3. RE-SEAL DRIFT    - drop seal_ok (upstream re-sealed / not verified) => the product
                       requirement is no longer satisfied (suspect).
  4. MISSING COND.    - one assumed condition of use undischarged => not satisfied
                       (the "bring every ingredient" rule; completeness via sealed assumes).
  5. VERSION CONSIST. - two manifests for one component identity => violation flagged.
  6. DETERMINISM      - a reliance cycle yields != 1 stable model => guardrail fires
                       (well-foundedness / acyclicity enforced by the single-model rule).
 
Requires: pip install clingo
Run:      python3 seg_demo_clingo_composition.py
"""
import sys
try:
    import clingo
except ImportError:
    sys.exit("clingo not installed - run: pip install clingo")
 
# ---------------------------------------------------------------- rule-sets
BASE = r"""
% witnesses: test outcomes are witnesses
witness(W) :- test_outcome(W).
% mode 1: a requirement is discharged by an ACTIVE witness edge
discharged(R) :- requirement(R), discharges(W,R), active(W,R), witness(W).
% satisfaction by positive upward-failure propagation over refines (single top-level neg)
haschild(R)  :- refines(_,R).
unmet(R) :- requirement(R), not discharged(R), not haschild(R).        % leaf, undischarged
unmet(R) :- requirement(R), not discharged(R), refines(C,R), unmet(C). % child unmet -> parent unmet
satisfied(R) :- requirement(R), not unmet(R).
"""
 
EXTENSION = r"""
% NEW: DesignReview extends the witness genus  (guarded by design_review/1)
witness(W) :- design_review(W).
% NEW: mode 2 reliance  (guarded by relies_on/2)
assume_unmet(G) :- assumes(G,C), not discharged(C).
discharged(R) :- relies_on(R,G), active(R,G),
                 references(R,M), manifest(M), seal_ok(M),
                 impl_uses(R,G),
                 not assume_unmet(G).
% NEW: version consistency (validation layer)  (guarded by manifest_component/2)
version_inconsistent(Comp) :- manifest_component(M1,Comp),
                              manifest_component(M2,Comp), M1<M2.
"""
 
SHOW = "#show satisfied/1.\n#show version_inconsistent/1.\n"
 
DEFS = """
#defined requirement/1. #defined test_outcome/1. #defined design_review/1.
#defined discharges/2. #defined active/2. #defined refines/2.
#defined relies_on/2. #defined references/2. #defined manifest/1.
#defined seal_ok/1. #defined impl_uses/2. #defined assumes/2.
#defined manifest_component/2.
"""
 
def solve(rules, facts):
    """Return list of models; each model is a set of shown-atom strings."""
    ctl = clingo.Control(["0"])          # 0 = enumerate ALL stable models
    ctl.add("base", [], DEFS + rules + facts + SHOW)
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(
        frozenset(str(a) for a in m.symbols(shown=True))))
    return models
 
def satisfied_set(model):
    return frozenset(a for a in model if a.startswith("satisfied("))
 
def report(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    return ok
 
# ---------------------------------------------------------------- scenarios
allok = True
 
# An import-free graph: r_top refines into r_a (discharged by a test outcome) and r_b
# (discharged by a test outcome). r_top is satisfied iff both children are.
IMPORT_FREE = """
requirement(r_top). requirement(r_a). requirement(r_b).
refines(r_a, r_top). refines(r_b, r_top).
test_outcome(to_a). discharges(to_a, r_a). active(to_a, r_a).
test_outcome(to_b). discharges(to_b, r_b). active(to_b, r_b).
"""
 
print("1. CONSERVATIVITY (import-free graph: BASE vs BASE+EXTENSION)")
m_base = solve(BASE, IMPORT_FREE)
m_aug  = solve(BASE + EXTENSION, IMPORT_FREE)
ok = (len(m_base) == 1 and len(m_aug) == 1
      and satisfied_set(m_base[0]) == satisfied_set(m_aug[0]))
allok &= report("identical verdicts; extension clauses inert",
                ok, f"satisfied={sorted(satisfied_set(m_aug[0]))}")
 
# Mode-2: product requirement relies on an upstream guarantee.
#   g_up assumes cou1 (single-core) and cou2 (short ISRs); both are downstream
#   requirements discharged by witnesses (cou1 by a design review, cou2 by a test).
RELIANCE_OK = """
requirement(r_prod).
requirement(cou1). requirement(cou2).
relies_on(r_prod, g_up). active(r_prod, g_up).
references(r_prod, man). manifest(man). seal_ok(man). impl_uses(r_prod, g_up).
assumes(g_up, cou1). assumes(g_up, cou2).
design_review(dr1). discharges(dr1, cou1). active(dr1, cou1).
test_outcome(to2).  discharges(to2, cou2). active(to2, cou2).
manifest_component(man, rtosx).
"""
print("2. MODE-2 DISCHARGE (reliance, all conditions met)")
m = solve(BASE + EXTENSION, RELIANCE_OK)
ok = len(m) == 1 and "satisfied(r_prod)" in m[0]
allok &= report("r_prod satisfied via reliance", ok)
 
print("3. RE-SEAL DRIFT (seal_ok dropped => suspect)")
m = solve(BASE + EXTENSION, RELIANCE_OK.replace("seal_ok(man). ", ""))
ok = len(m) == 1 and "satisfied(r_prod)" not in m[0]
allok &= report("r_prod NOT satisfied after re-seal", ok)
 
print("4. MISSING CONDITION (one assumed CoU undischarged)")
# remove cou2's discharging witness; cou2 stays assumed but undischarged
missing = RELIANCE_OK.replace("test_outcome(to2).  discharges(to2, cou2). active(to2, cou2).", "")
m = solve(BASE + EXTENSION, missing)
ok = len(m) == 1 and "satisfied(r_prod)" not in m[0]
allok &= report("r_prod NOT satisfied (ingredient missing)", ok)
 
print("5. VERSION CONSISTENCY (two manifests, one component)")
twomanif = RELIANCE_OK + "manifest(man2). manifest_component(man2, rtosx).\n"
m = solve(BASE + EXTENSION, twomanif)
ok = len(m) == 1 and any("version_inconsistent(rtosx)" in a for a in m[0])
allok &= report("violation flagged", ok)
 
print("6. DETERMINISM GUARDRAIL (reliance cycle => != 1 stable model)")
# r relies on g, and g assumes r itself: discharged(r) <-> not (not discharged(r))
CYCLE = """
requirement(r).
relies_on(r, g). active(r, g).
references(r, man). manifest(man). seal_ok(man). impl_uses(r, g).
assumes(g, r).
"""
m = solve(BASE + EXTENSION, CYCLE)
ok = len(m) != 1
allok &= report("non-determinism detected (well-foundedness violated)",
                ok, f"stable models = {len(m)}")
 
print("\n" + ("ALL PASS" if allok else "SOME FAILED"))
sys.exit(0 if allok else 1)
 