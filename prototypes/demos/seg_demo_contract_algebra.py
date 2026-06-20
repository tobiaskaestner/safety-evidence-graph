#!/usr/bin/env python3
"""
seg_demo_contract_algebra.py
 
Worked examples of the A/G contract algebra (Benveniste et al. 2018, Def 5.4)
over a tiny finite RTOS behaviour universe, so every operation is real set
arithmetic rather than assertion. Contracts are (A, G) with A, G subsets of a
12-element universe, represented as 12-bit masks; intersection/union/complement
are &, |, ~. Everything is kept in SATURATED form (G = G | ¬A), so Def 5.4's
formulas apply directly.
 
Scenario:
  - A scheduler core, a HAL/driver, and the app's required "slot" contract.
  - Shows: satisfaction, refinement (incl. why the scheduler ALONE fails the
    slot), parallel composition (the driver discharging the scheduler's
    assumption), conjunction (two viewpoints), and the quotient (what must fill
    the slot), with brute-force verification of the algebraic laws.
 
Runtime: the quotient and adjoint checks brute-force all 3^12 = 531441 saturated
contracts; expect a couple of seconds.
 
MODEL SCOPE / CAVEAT. The behaviour universe B here is a set of FLAT ABSTRACT
OUTCOMES -- triples like (single, short, M) that summarise a whole run by a few
end-of-run observations. They have no internal time order, so there is nothing to
take a "prefix" of, and this model CANNOT express temporal properties (e.g.
"eventually dispatched within 50us", "never deadlocks"). The monograph's Section-4
prefix / receptiveness / Moore-interface (input-output port partition) machinery
belongs to a richer B of timed traces; that is also why composition here yields
saturation artifacts in the assumption (the shared coordinate `isr` appears on both
the A and G sides, since this toy has no port partition). The ALGEBRA is exact and
prefix-independent -- it is powerset Boolean algebra over B for any B, and every law
below verifies -- but a faithful RTOS model would use timed traces, which sharpens
the refinement-decidability question (see seg_composability_cbd.md sec 7).
"""
from itertools import product
 
# ----------------------------------------------------------------------------
# Universe: a behaviour is one valuation of (core, isr, lat).
# ----------------------------------------------------------------------------
CORES = ['single', 'multi']
ISRS  = ['short', 'long']          # short = ISR masks interrupts <= 10us
LATS  = ['F', 'M', 'S']            # dispatch latency: F <=50us, M (50,100], S >100us
 
BEHAVIOURS = list(product(CORES, ISRS, LATS))     # 12 behaviours
N = len(BEHAVIOURS)
FULL = (1 << N) - 1
IDX = {b: i for i, b in enumerate(BEHAVIOURS)}
 
def pred(fn):
    """Build the behaviour set (bitmask) of all behaviours satisfying fn."""
    m = 0
    for b, i in IDX.items():
        if fn(*b):
            m |= (1 << i)
    return m
 
def NOT(s):          return FULL & ~s
def names(s):        return [f"{c}/{i}/{l}" for (c, i, l), k in IDX.items() if (s >> k) & 1]
 
# atomic predicates as behaviour sets
sc      = pred(lambda c, i, l: c == 'single')          # single-core
mask_ok = pred(lambda c, i, l: i == 'short')           # short ISRs
disp50  = pred(lambda c, i, l: l == 'F')               # dispatch <= 50us
disp100 = pred(lambda c, i, l: l in ('F', 'M'))        # dispatch <= 100us
 
# ----------------------------------------------------------------------------
# Contracts (always stored saturated: G := G | ¬A)
# ----------------------------------------------------------------------------
class C:
    __slots__ = ('A', 'G')
    def __init__(self, A, G, saturate=True):
        self.A = A
        self.G = (G | NOT(A)) if saturate else G
    def __repr__(self):
        return f"C(|A|={bin(self.A).count('1'):2d}, |G|={bin(self.G).count('1'):2d})"
 
def refines(x, y):   # x ⪯ y  iff  A_x ⊇ A_y  and  G_x ⊆ G_y      (Def 5.4.1)
    return (y.A & ~x.A) == 0 and (x.G & ~y.G) == 0
def equiv(x, y):     # same canonical (saturated) form
    return x.A == y.A and x.G == y.G
def conj(c1, c2):    # C1 ∧ C2 = (A1∪A2, G1∩G2)                    (Def 5.4.2)
    return C(c1.A | c2.A, c1.G & c2.G)
def comp(c1, c2):    # C1 ∥ C2 = ((A1∩A2) ∪ ¬(G1∩G2), G1∩G2)      (Def 5.4.3 / eq 5.7)
    G = c1.G & c2.G
    A = (c1.A & c2.A) | NOT(G)
    return C(A, G)
def satisfies(M, c): # M ⊨ C  iff  M ∩ A ⊆ G   (== M ⊆ G_sat)     (eq 5.5)
    return (M & c.A & ~c.G) == 0
 
def all_saturated():
    """Yield every saturated contract: A any subset, G = ¬A ∪ (subset of A)."""
    for A in range(FULL + 1):
        base = NOT(A)
        sub = A
        while True:
            yield C(A, base | sub, saturate=False)
            if sub == 0:
                break
            sub = (sub - 1) & A
 
def quotient(target, divisor):
    """target / divisor = max{ X | divisor ∥ X ⪯ target } (join of all feasible X)."""
    A_acc, G_acc, n = FULL, 0, 0
    for X in all_saturated():
        if refines(comp(divisor, X), target):
            A_acc &= X.A          # join: assumption = ∩ A_X
            G_acc |= X.G          # join: guarantee = ∪ G_X
            n += 1
    return (C(A_acc, G_acc), n) if n else (None, 0)
 
def show(label, c):
    print(f"  {label:14s} {c}")
    print(f"       A (legal envs) = {names(c.A)}")
    print(f"       G (guaranteed) = {names(c.G)}")
 
# ----------------------------------------------------------------------------
# The contracts
# ----------------------------------------------------------------------------
SCHED  = C(mask_ok, disp50)     # scheduler:  guarantees <=50us, assuming short ISRs
DRIVER = C(sc,      mask_ok)    # HAL/driver: guarantees short ISRs, assuming single-core
SLOT   = C(sc,      disp100)    # app's required contract: needs <=100us, provides single-core
 
TIMING = C(mask_ok, disp100)    # viewpoint 1: <=100us assuming short ISRs
TIGHT  = C(sc,      disp50)     # viewpoint 2: <=50us assuming single-core
 
print("=" * 72)
print("CONTRACTS (saturated)")
print("=" * 72)
show("SCHED",  SCHED)
show("DRIVER", DRIVER)
show("SLOT",   SLOT)
 
# ----------------------------------------------------------------------------
# 1. SATISFACTION  (M ⊨ C)
# ----------------------------------------------------------------------------
print("\n" + "=" * 72)
print("1. SATISFACTION   M ⊨ C  iff  M ∩ A ⊆ G")
print("=" * 72)
M_good = NOT(mask_ok) | disp50         # "short ISRs ⟹ <=50us": a correct scheduler
M_bad  = disp100                       # only ever achieves <=100us (sometimes 50<lat<=100)
print(f"  M_good ⊨ SCHED ? {satisfies(M_good, SCHED)}   (correct scheduler)")
print(f"  M_bad  ⊨ SCHED ? {satisfies(M_bad,  SCHED)}   (too slow when ISRs are short)")
 
# ----------------------------------------------------------------------------
# 2. REFINEMENT  — scheduler ALONE does not fill the slot
# ----------------------------------------------------------------------------
print("\n" + "=" * 72)
print("2. REFINEMENT   X ⪯ Y  iff  A_X ⊇ A_Y and G_X ⊆ G_Y")
print("=" * 72)
print(f"  SCHED ⪯ SLOT ? {refines(SCHED, SLOT)}")
print("     why: SLOT only promises single-core; SCHED still ASSUMES short ISRs,")
print("     so SCHED's assumption is NOT ⊇ SLOT's. The scheduler alone is insufficient.")
 
# ----------------------------------------------------------------------------
# 3. COMPOSITION  — the driver discharges the scheduler's assumption
# ----------------------------------------------------------------------------
print("\n" + "=" * 72)
print("3. COMPOSITION   C1 ∥ C2 = ((A1∩A2) ∪ ¬(G1∩G2), G1∩G2)")
print("=" * 72)
SUBSYS = comp(SCHED, DRIVER)
show("SCHED∥DRIVER", SUBSYS)
print(f"     single-core env always legal for the composite? {(sc & ~SUBSYS.A) == 0}")
print( "     -> the driver's guarantee (short ISRs) discharged the scheduler's")
print( "        assumption; the composite no longer needs the ENV to supply it.")
 
# ----------------------------------------------------------------------------
# 4. REFINEMENT again — the COMPOSED subsystem does fill the slot
# ----------------------------------------------------------------------------
print("\n" + "=" * 72)
print("4. REFINEMENT (the payoff)")
print("=" * 72)
print(f"  (SCHED ∥ DRIVER) ⪯ SLOT ? {refines(SUBSYS, SLOT)}")
print("     scheduler alone: FAILS;  scheduler ∥ driver: REFINES the slot -> import sound.")
 
# ----------------------------------------------------------------------------
# 5. CONJUNCTION  — fusing two viewpoints on one artifact
# ----------------------------------------------------------------------------
print("\n" + "=" * 72)
print("5. CONJUNCTION   C1 ∧ C2 = (A1∪A2, G1∩G2)  (greatest lower bound)")
print("=" * 72)
CONJ = conj(TIMING, TIGHT)
show("TIMING∧TIGHT", CONJ)
print(f"     CONJ ⪯ TIMING ? {refines(CONJ, TIMING)}    CONJ ⪯ TIGHT ? {refines(CONJ, TIGHT)}")
 
# ----------------------------------------------------------------------------
# 6. QUOTIENT  — what must fill the slot, given we already have the scheduler
# ----------------------------------------------------------------------------
print("\n" + "=" * 72)
print("6. QUOTIENT   SLOT / SCHED = max{ X | SCHED ∥ X ⪯ SLOT }   (brute force)")
print("=" * 72)
Q, nfeasible = quotient(SLOT, SCHED)
show("SLOT/SCHED", Q)
print(f"     feasible fillers found: {nfeasible}")
print(f"     SCHED ∥ (SLOT/SCHED) ⪯ SLOT ? {refines(comp(SCHED, Q), SLOT)}   (quotient is feasible)")
print(f"     DRIVER ⪯ (SLOT/SCHED) ? {refines(DRIVER, Q)}   (our real driver is an adequate filler)")
 
# ----------------------------------------------------------------------------
# LAW CHECKS
# ----------------------------------------------------------------------------
print("\n" + "=" * 72)
print("ALGEBRAIC LAWS (verified)")
print("=" * 72)
 
# commutativity & associativity of ∥
A_, B_, C_ = SCHED, DRIVER, C(disp100, sc)
print(f"  ∥ commutative ?  {equiv(comp(A_, B_), comp(B_, A_))}")
print(f"  ∥ associative ?  {equiv(comp(comp(A_, B_), C_), comp(A_, comp(B_, C_)))}")
 
# congruence: refine a part -> refine the whole (two-sided form)
A2 = C(SCHED.A, SCHED.G & disp100)        # strengthen SCHED's guarantee a touch -> A2 ⪯ SCHED
print(f"  A2 ⪯ SCHED ?     {refines(A2, SCHED)}")
print(f"  congruence: A2 ∥ DRIVER ⪯ SCHED ∥ DRIVER ? {refines(comp(A2, DRIVER), comp(SCHED, DRIVER))}")
 
# conjunction is the GLB (brute force over all saturated X)
glb_ok = True
for X in all_saturated():
    if refines(X, TIMING) and refines(X, TIGHT) and not refines(X, CONJ):
        glb_ok = False
        break
print(f"  ∧ is the GLB (∀X: X⪯C1 ∧ X⪯C2 ⟹ X⪯C1∧C2) ? {glb_ok}")
 
# quotient adjoint, Property 7: X ⪯ (C/D) ⟺ D ∥ X ⪯ C   (brute force)
adj_ok = True
for X in all_saturated():
    if refines(X, Q) != refines(comp(SCHED, X), SLOT):
        adj_ok = False
        break
print(f"  quotient adjoint (Property 7) holds ∀X ? {adj_ok}")
print("\nDone.")