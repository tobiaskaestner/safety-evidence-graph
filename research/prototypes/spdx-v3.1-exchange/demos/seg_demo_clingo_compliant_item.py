"""
seg_demo_clingo_compliant_item_v1.py
====================================
Compliant-item-supplier discharge via a referenced compliant-item safety manual
(BOM) + the document-root compatibility (diamond co-reference / version-pin) check.

Role (IEC 61508): the COMPLIANT-ITEM SUPPLIER (a silicon vendor in this example)
publishes a compliant item M' with its safety manual; the INTEGRATOR integrates it.

Setup (a diamond): the integrator relies on upstream M (guarantee `g_p_sys`, which
assumes the HAL condition `p_hal`) AND on a compliant-item supplier's M' (guarantee
`g_m_hal`, "STM32L4 provides a compliant HAL"). M' discharges the inherited `p_hal`
via an affirmed `covers` reliance. M' is published as an ordinary DEC-020 contract
BOM -- its compliant-item safety manual -- whose
`SpdxDocument.import` pins the EXACT upstream document it was validated against
(`ExternalMap.externalSpdxId` + `verifiedUsing` = the upstream Merkle root).

The integrator's verifier admits M' only if the vendor's pinned upstream root EQUALS
the upstream document root the integrator itself imports (document-root granularity).

  S1  M alone            -> p_hal cannot be discharged; integrator FORWARDS it  -> conditional.
  S2  M + M' (match)     -> compatible; covers(g_m_hal, p_hal) discharges it    -> total.
  S3  M + M' (mismatch)  -> vendor pinned a DIFFERENT upstream root -> REJECTED at the pin check.
      (and: bypassing the check would read a SPURIOUS total -- the check is load-bearing.)

The compatibility check is a pre-reconstruction verifier step (Python), the sibling
of consumer.py's Merkle inclusion check; the verdict engine cannot see version skew.
Verdict recomputed on the FIXED engine (DEC-022 forward + condition_of_use).

Run: python -m demos.seg_demo_clingo_compliant_item
"""
from demos import seg_demo_clingo_forward as F   # FIXED engine (forward + condition_of_use rollup)


# --- document-root compatibility (diamond co-reference / version-pin) --------
def admit_vendor(integrator_upstream_root: str, vendor_pinned_upstream_root: str):
    """SPDX import/ExternalMap pin check at document-root granularity. M''s BOM pins
    (externalSpdxId + verifiedUsing Hash) the upstream document it validated against;
    admit only if it equals the upstream the integrator imports."""
    if vendor_pinned_upstream_root == integrator_upstream_root:
        return True, "pins match (same upstream document root)"
    return False, "pin mismatch: M' validated against a different upstream root"


# --- SEG facts ---------------------------------------------------------------
# Upstream M imported under man_up; the integrator's product d_sys relies on it and
# inherits the HAL condition p_hal.
M_BASE = """
node(g_p_sys, guarantee).
referenced_under(g_p_sys, man_up).
seal_ok(man_up).
node(p_hal, requirement).
referenced_under(p_hal, man_up).
edge(asu, assumes, g_p_sys, p_hal).
node(d_sys, requirement).
node(d_req, requirement).
node(d_impl, implementation).
edge(dfr, refines, d_req, d_sys).
edge(dcv, covers, g_p_sys, d_req).
edge(duse, uses, d_impl, man_up).
"""

# The M-alone fallback: integrator forwards the inherited p_hal (affirmed).
FORWARD_PHAL = """
edge(fwd, forward, d_req, p_hal).
affirmed_forward(d_req, p_hal).
"""

# Vendor M' imported under man_vendor: guarantee g_m_hal covers p_hal; M' carries its
# own condition m_clk, discharged locally by review (the chain continues a hop).
VENDOR = """
node(g_m_hal, guarantee).
referenced_under(g_m_hal, man_vendor).
seal_ok(man_vendor).
edge(vuse, uses, d_impl, man_vendor).
node(m_clk, requirement).
referenced_under(m_clk, man_vendor).
edge(asv, assumes, g_m_hal, m_clk).
edge(dcov, covers, g_m_hal, p_hal).
node(dr_clk, designreview).
edge(rev_clk, reviews, dr_clk, m_clk).
"""


def proof_state(facts):
    ms = F.solve_fixed(facts)
    assert len(ms) == 1, f"determinism guardrail: expected 1 answer set, got {len(ms)}"
    m = ms[0]
    st = ("unsatisfied" if "proof_unsatisfied" in m else
          "conditional" if "proof_conditional" in m else
          "total" if "proof_total" in m else "??")
    return st, m


INTEGRATOR_UPSTREAM_ROOT = "ROOT_UP@v1"

if __name__ == "__main__":
    print("Silicon-vendor discharge + document-root compatibility check\n")

    # ---- S1: M alone -> integrator forwards p_hal -> conditional ----
    st, m = proof_state(M_BASE + FORWARD_PHAL)
    print(f"  S1 M alone (forward p_hal)                  proof={st}")
    assert st == "conditional" and "forwarded(p_hal)" in m

    # ---- S2: M + M', vendor pins the SAME upstream -> admit -> total ----
    ok, why = admit_vendor(INTEGRATOR_UPSTREAM_ROOT, "ROOT_UP@v1")
    print(f"  S2 vendor pin check: {why}")
    assert ok
    st, m = proof_state(M_BASE + VENDOR)            # admitted: covers(g_m_hal, p_hal) wired
    print(f"  S2 M + M' (compatible)                      proof={st}")
    assert st == "total" and "forwarded(p_hal)" not in m   # discharged, not forwarded

    # ---- S3: M + M', vendor pins a DIFFERENT upstream -> reject ----
    ok, why = admit_vendor(INTEGRATOR_UPSTREAM_ROOT, "ROOT_UP@v2")
    print(f"  S3 vendor pin check: {why}")
    assert not ok                                   # M' NOT admitted
    st, m = proof_state(M_BASE + FORWARD_PHAL)      # vendor facts withheld -> fall back to forward
    print(f"  S3 M + M' (incompatible) -> M' withheld     proof={st}  (fallback: forward p_hal)")
    assert st == "conditional"
    # The verdict engine cannot see version skew: if the check were BYPASSED and the
    # incompatible M' wired anyway, it would read a SPURIOUS total -> the pin check is
    # load-bearing and must live at the verifier, not in clingo.
    st_bypass, _ = proof_state(M_BASE + VENDOR)
    print(f"  S3 (if check bypassed: M' wired anyway)     proof={st_bypass}  <- SPURIOUS, why the check matters")
    assert st_bypass == "total"

    print("\nOK: 3/3. M alone forwards (S1); compatible M' discharges to total (S2);"
          " incompatible M' rejected at the pin check (S3) -- which clingo alone could not catch.")
