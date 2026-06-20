#!/usr/bin/env python3
"""
seg_demo_clingo_transitive.py

Transitive reliance A -> B -> C, and how staleness travels through the seals a proof embeds by reference.

A relies on B's guarantee (its verdict checks seal_ok(m_b) only -- the firewall: A never
re-verifies B's or C's internal graphs). B in turn relied on C, so B's sealed proof
EMBEDS C's manifest by reference: a change at C alters the embedded content hash, which
fails B's recompute, which fails A's check of seal_ok(m_b). So a two-levels-down change
reaches the top verdict through the embedded-by-reference seals, not through the verdict recursion.

The composition grammar treats seal_ok/1 as an EDB primitive (core-recomputed). This demo models that
recompute layer explicitly, as a POSITIVE staleness propagation with a single top
negation -- the same idiom the composition grammar uses for `unsatisfied`, hence syntactically stratified:

    seal_stale(M) :- manifest(M), not seal_recomputes(M).   % local Merkle recompute fails
    seal_stale(M) :- embeds(M, M2), seal_stale(M2).          % embeds a stale seal -> stale
    seal_ok(M)    :- manifest(M), not seal_stale(M).
  (the real core layer recomputes roots procedurally bottom-up; this ASP toy just shows
   the dependency, and `embeds` must be acyclic, like the verdict's structural edges.)

Verdict rules are reused verbatim from seg_example_v1_plus_composition.dsl (see seg_demo_clingo_composition_v2.py for
the annotated source). Demo conveniences: `inactive/1` = "edge_state != active";
symbolic constants for field values.

Requires: pip install clingo ;  Run: python3 seg_demo_clingo_transitive.py
"""
import sys
try:
    import clingo
except ImportError:
    sys.exit("clingo not installed - run: pip install clingo")

BASE_SHARED = r"""
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
"""
LEAF_COMP = r"""
unsatisfied(R) :- leaf(R), not has_active_verifies(R),   not discharged_otherwise(R).
unsatisfied(R) :- leaf(R), not has_active_implements(R), not discharged_otherwise(R).
"""
COMPOSITION = r"""
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
# NEW here: the seal-recompute layer (the composition grammar's EDB seal_ok), shown as staleness propagating through embedded seals.
SEAL_LAYER = r"""
seal_stale(M) :- node(M, manifest), not seal_recomputes(M).
seal_stale(M) :- embeds(M, M2), seal_stale(M2).
seal_ok(M)    :- node(M, manifest), not seal_stale(M).
"""
PROG = BASE_SHARED + LEAF_COMP + COMPOSITION + SEAL_LAYER

DEFS = """
#defined node/2. #defined edge/4. #defined node_field/3. #defined inactive/1.
#defined referenced_under/2. #defined seal_recomputes/1. #defined embeds/2.
"""
SHOW = ("#show satisfied/1.\n#show unsatisfied/1.\n#show seal_ok/1.\n#show seal_stale/1.\n")

def solve(facts):
    ctl = clingo.Control(["0"])
    ctl.add("base", [], DEFS + PROG + facts + SHOW)
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(
        frozenset(str(a) for a in m.symbols(shown=True))))
    return models

def has(model, atom): return atom in model
def report(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    return ok

allok = True

# A relies on B's guarantee g_b (sealed under m_b); B relied on C, so m_b embeds m_c.
# B published one condition cou_b, which A discharges by a DesignReview.
CHAIN = """
node(r_a, requirement). node(g_b, requirement). node(cou_b, requirement).
edge(er, relies_on, r_a, g_b).
referenced_under(g_b, m_b). referenced_under(cou_b, m_b).
node(m_b, manifest). node(m_c, manifest). node_field(m_b, component_iri, comp_b).
embeds(m_b, m_c).
seal_recomputes(m_b). seal_recomputes(m_c).
node(impl_a, implementation). edge(eu, uses, impl_a, m_b).
edge(eab, assumes, g_b, cou_b).
node(dr, designreview). edge(ev, reviews, dr, cou_b).
"""

print("1. HEALTHY CHAIN (A->B->C all seals recompute)")
m = solve(CHAIN)
ok = (len(m) == 1 and has(m[0], "seal_ok(m_b)") and has(m[0], "seal_ok(m_c)")
      and has(m[0], "satisfied(r_a)"))
allok &= report("seal_ok up the chain; r_a satisfied", ok)

print("2. C RE-SEALS  (two-hop: change at C breaks A through the embedded seals)")
m = solve(CHAIN.replace(" seal_recomputes(m_c).", ""))
ok = (len(m) == 1 and has(m[0], "seal_stale(m_c)") and has(m[0], "seal_stale(m_b)")
      and not has(m[0], "seal_ok(m_b)") and has(m[0], "unsatisfied(r_a)"))
allok &= report("staleness m_c -> m_b -> r_a unsatisfied (A never looked inside C)", ok)

print("3. B RE-SEALS  (one-hop contrast: C still fine)")
m = solve(CHAIN.replace("seal_recomputes(m_b). ", ""))
ok = (len(m) == 1 and has(m[0], "seal_stale(m_b)") and has(m[0], "seal_ok(m_c)")
      and has(m[0], "unsatisfied(r_a)"))
allok &= report("m_b stale, m_c ok; r_a unsatisfied", ok)

print("4. NO SIDEWAYS LEAK (an unrelated stale manifest does not reach A)")
m = solve(CHAIN + "node(m_d, manifest).\n")          # m_d never recomputes, embedded by nobody
ok = (len(m) == 1 and has(m[0], "seal_stale(m_d)")
      and has(m[0], "seal_ok(m_b)") and has(m[0], "satisfied(r_a)"))
allok &= report("m_d stale but off the chain; r_a still satisfied", ok)

print("\n" + ("ALL PASS" if allok else "SOME FAILED"))
sys.exit(0 if allok else 1)
