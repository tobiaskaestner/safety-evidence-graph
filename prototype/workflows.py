"""The three SEG prototype workflows.

  consistency()          — Workflow 1, step 4
  generate_proof(scope)  — Workflow 2, step 5 (not yet implemented)
  detect_suspect()       — Workflow 3, step 6 (not yet implemented)
"""
from __future__ import annotations

from collections import Counter

import satisfaction
from graph_model import Graph, LinkState, STRONG_EDGE_TYPES


def consistency(graph: Graph) -> dict:
    """Workflow 1: structural gaps, link states, and DEC-001 satisfaction.

    Returns a dict with four sections:
      satisfaction   — per-requirement classification + satisfied flag + gap list
      structuralGaps — leaf reqs with no edge of a given type at all
      suspectLinks   — strong edges whose linkState is not active
      staleOutcomes  — outcomes whose repoBSha differs from the majority SHA
    """
    results = satisfaction.evaluate(graph)

    # ── satisfaction table ────────────────────────────────────────────────────
    sat_table = {
        r.store_id: {
            "classification": r.classification,
            "satisfied": r.satisfied,
            "gaps": r.gaps,
        }
        for r in sorted(results.values(), key=lambda r: r.store_id)
    }

    # ── structural gaps (edge type absent entirely, not just non-active) ──────
    struct_gaps = []
    for r in sorted(results.values(), key=lambda r: r.store_id):
        if r.classification == "leaf":
            missing = []
            if not graph.incoming(r.req_iri, "seg:Verifies"):
                missing.append("seg:Verifies")
            if not graph.incoming(r.req_iri, "seg:Implements"):
                missing.append("seg:Implements")
            if missing:
                struct_gaps.append({
                    "requirementId": r.req_iri,
                    "missingEdgeTypes": missing,
                })

    # ── suspect links (strong edges not in ACTIVE state) ─────────────────────
    suspect = [
        {
            "edgeId": e.iri,
            "edgeType": e.edge_type,
            "linkState": e.link_state.value,
        }
        for e in graph.edges
        if e.edge_type in STRONG_EDGE_TYPES and e.link_state != LinkState.ACTIVE
    ]

    # ── stale outcomes ────────────────────────────────────────────────────────
    all_outcomes = [n for n in graph.nodes.values() if n.node_type == "TestOutcome"]
    current_sha = (
        Counter(n.store_item["repoBSha"] for n in all_outcomes).most_common(1)[0][0]
        if all_outcomes else ""
    )
    stale = [
        {
            "outcomeId": n.store_id,
            "recordedSha": n.store_item["repoBSha"],
            "currentSha": current_sha,
        }
        for n in sorted(all_outcomes, key=lambda n: n.store_id)
        if n.store_item["repoBSha"] != current_sha
    ]

    return {
        "satisfaction": sat_table,
        "structuralGaps": struct_gaps,
        "suspectLinks": suspect,
        "staleOutcomes": stale,
    }


def generate_proof(graph: Graph, scope: list[str]) -> dict:
    raise NotImplementedError("generate_proof — step 5")


def detect_suspect(graph: Graph) -> dict:
    raise NotImplementedError("detect_suspect — step 6")
