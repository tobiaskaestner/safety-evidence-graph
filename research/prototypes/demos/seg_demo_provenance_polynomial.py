# ------------------------------------------------------------
# Provenance polynomial for a minimal SEG verdict — constructed
# symbolically over N[X], then evaluated in several semirings.
# The runnable companion to seg_tsf_duality.md §6.8 (and §6.2's
# "triangle": the polynomial is the universal object; verdict,
# score, counting, why-provenance are its semiring evaluations).
#
# Graph: the worked fragment + a second covering test.
#   ground facts (committed layer -> indeterminates):
#     r  = affirmed refines(REQ001, SYS001)
#     e1 = affirmed covers(TST001, REQ001)   o1 = passed(TST001)
#     e2 = affirmed covers(TST002, REQ001)   o2 = passed(TST002)
#   ruleset:
#     sat(R) :- covers(T,R), passed(T).
#     ok(S)  :- refines(R,S), sat(R).
#     redundant(R) :- covers(T1,R), passed(T1),
#                     covers(T2,R), passed(T2)[, T1 != T2].
#
# What it demonstrates (each assert is one claim from §6.8):
#   - monomial  = one derivation's joint bill of materials (products);
#   - sum       = alternative discharge legs ("multi-legged" = >1 monomial);
#   - exponent  = same fact reused within one proof — the unguarded
#                 redundancy rule is EXPOSED by its square terms;
#   - coefficient = number of distinct proofs over the same leaf multiset;
#   - drift/suspicion = a VALUATION event (gate a leaf to 0); the
#                 polynomial itself never changes — structure/judgement split;
#   - evaluations: Boolean verdict, proof counting, Viterbi confidence.
# Self-checking: asserts fail loudly if the algebra is wrong.
# Run: python3 seg_demo_provenance_polynomial.py
# ------------------------------------------------------------
from collections import Counter

# A polynomial in N[X]: dict {monomial: coeff};
# a monomial is a tuple(sorted((variable, exponent))).


def mono_mul(m1, m2):
    c = Counter(dict(m1))
    c.update(dict(m2))
    return tuple(sorted(c.items()))


def p_add(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            out[m] = out.get(m, 0) + c
    return out


def p_mul(p, q):
    out = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = mono_mul(m1, m2)
            out[m] = out.get(m, 0) + c1 * c2
    return out


def var(x):
    return {((x, 1),): 1}


def show(p):
    def mstr(m):
        return "*".join(f"{v}^{e}" if e > 1 else v for v, e in m) or "1"
    return " + ".join(
        f"{c}*{mstr(m)}" if c > 1 else mstr(m)
        for m, c in sorted(p.items(), key=lambda kv: kv[0])
    )


def evaluate(p, val, add, mul, zero, one):
    """The unique semiring homomorphism N[X] -> K extending the valuation."""
    total = zero
    for m, c in p.items():
        term = one
        for v, e in m:
            for _ in range(e):
                term = mul(term, val[v])
        acc = zero
        for _ in range(c):          # coefficient = c-fold addition
            acc = add(acc, term)
        total = add(total, acc)
    return total


# ---- the ground layer (each committed fact = one indeterminate) ----
r, e1, e2, o1, o2 = map(var, ["r", "e1", "e2", "o1", "o2"])

# ---- the ruleset, run symbolically bottom-up (acyclic: one pass) ----
sat_req = p_add(p_mul(e1, o1), p_mul(e2, o2))       # two discharge legs
ok_sys = p_mul(r, sat_req)                          # roll-up to the system claim
red_bad = p_mul(sat_req, sat_req)                   # redundancy, guard FORGOTTEN
red_good = p_add(                                   # ordered pairs, T1 != T2
    p_mul(p_mul(e1, o1), p_mul(e2, o2)),
    p_mul(p_mul(e2, o2), p_mul(e1, o1)),
)

print("sat(REQ001)         =", show(sat_req))
print("ok(SYS001)          =", show(ok_sys))
print("redundant, no guard =", show(red_bad))
print("redundant, guarded  =", show(red_good))

# the polynomial is a function of topology + ruleset ONLY (no judgements yet)
assert show(ok_sys) == "e1*o1*r + e2*o2*r"
# unguarded redundancy exposed by its square terms + coefficient 2 cross term
assert show(red_bad) == "2*e1*e2*o1*o2 + e1^2*o1^2 + e2^2*o2^2"
assert show(red_good) == "2*e1*e2*o1*o2"

# ---- evaluations: one object, many semantics ----
B = dict(add=lambda a, b: a or b, mul=lambda a, b: a and b, zero=False, one=True)
N = dict(add=lambda a, b: a + b, mul=lambda a, b: a * b, zero=0, one=1)
VITERBI = dict(add=max, mul=lambda a, b: a * b, zero=0.0, one=1.0)

all_affirmed = dict(r=True, e1=True, e2=True, o1=True, o2=True)
e1_suspect = dict(all_affirmed, e1=False)      # drift gate: suspect leaf -> 0
both_suspect = dict(all_affirmed, e1=False, e2=False)
ones = dict(r=1, e1=1, e2=1, o1=1, o2=1)
confidences = dict(r=1.0, e1=1.0, e2=1.0, o1=0.9, o2=0.6)

checks = [
    # (label, polynomial, valuation, semiring, expected)
    ("Boolean, all affirmed:  ok", ok_sys, all_affirmed, B, True),
    ("Boolean, e1 suspect:    ok", ok_sys, e1_suspect, B, True),   # 2nd leg carries
    ("Boolean, both suspect:  ok", ok_sys, both_suspect, B, False),
    ("Counting:               ok", ok_sys, ones, N, 2),            # two proofs
    ("Viterbi confidence:     ok", ok_sys, confidences, VITERBI, 0.9),
    ("Counting, unguarded redundant", red_bad, ones, N, 4),        # incl. T1=T2!
    ("Counting, guarded redundant  ", red_good, ones, N, 2),
    # redundancy is the predicate that DOES fail when one leg drifts:
    ("Boolean, e1 suspect, guarded redundant", red_good, e1_suspect, B, False),
]
print()
for label, poly, valuation, semiring, expected in checks:
    got = evaluate(poly, valuation, **semiring)
    print(f"{label} = {got}")
    assert got == expected, (label, got, expected)

print("\nAll assertions hold: the polynomial is fixed by topology+ruleset;")
print("verdict/count/confidence/drift-gating are evaluations of it.")
