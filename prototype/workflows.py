"""The three SEG prototype workflows.

  consistency()          — Workflow 1, step 4
  generate_proof(scope)  — Workflow 2, step 5
  detect_suspect()       — Workflow 3, step 6 (not yet implemented)
"""
from __future__ import annotations

from collections import Counter

import satisfaction
from graph_model import Graph, LinkState, STRONG_EDGE_TYPES
from hashing import hash_object, sha256_hex


# ── Workflow 1 ────────────────────────────────────────────────────────────────

def consistency(graph: Graph) -> dict:
    """Structural gaps, link states, and DEC-001 satisfaction over the full graph."""
    results = satisfaction.evaluate(graph)

    sat_table = {
        r.store_id: {
            "classification": r.classification,
            "satisfied": r.satisfied,
            "gaps": r.gaps,
        }
        for r in sorted(results.values(), key=lambda r: r.store_id)
    }

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

    suspect = [
        {"edgeId": e.iri, "edgeType": e.edge_type, "linkState": e.link_state.value}
        for e in graph.edges
        if e.edge_type in STRONG_EDGE_TYPES and e.link_state != LinkState.ACTIVE
    ]

    all_outcomes = [n for n in graph.nodes.values() if n.node_type == "TestOutcome"]
    current_sha = _majority_sha(graph)
    stale = [
        {"outcomeId": n.store_id, "recordedSha": n.store_item["repoBSha"],
         "currentSha": current_sha}
        for n in sorted(all_outcomes, key=lambda n: n.store_id)
        if n.store_item["repoBSha"] != current_sha
    ]

    return {
        "satisfaction": sat_table,
        "structuralGaps": struct_gaps,
        "suspectLinks": suspect,
        "staleOutcomes": stale,
    }


# ── Workflow 2 ────────────────────────────────────────────────────────────────

def generate_proof(graph: Graph, scope: list[str]) -> dict:
    """Produce a proof over a requirement scope (DEC-002).

    scope — list of requirement IRIs (already resolved from patterns by cli.py).

    Scoping a non-leaf obligates its entire refines subtree (DEC-001); the
    scope is expanded automatically. The partial-vs-total top-level scope
    signal (DEC-002) reports whether the scope covers every top-level
    requirement in the graph or just a subset.
    """
    # Expand scope to full requirement subtrees + reachable impls/test specs
    in_scope_reqs = _expand_req_scope(scope, graph)
    all_in_scope = _expand_to_impl_ts(in_scope_reqs, graph)

    # Scope roots: in-scope reqs whose parent (if any) is outside the scope
    scope_roots = _scope_roots(in_scope_reqs, graph)

    # Partial-vs-total signal (DEC-002)
    all_top_level = _top_level_reqs(graph)
    uncovered = set(all_top_level) - set(scope_roots)
    scope_signal = {
        "isTotalScope": len(uncovered) == 0,
        "topLevelInGraph": sorted(graph.nodes[i].store_id for i in all_top_level),
        "scopeRoots":      sorted(graph.nodes[i].store_id for i in scope_roots),
        "uncoveredTopLevel": sorted(graph.nodes[i].store_id for i in uncovered),
    }

    # Merkle root: SHA256 of sorted scope-root merkle hashes
    root_hashes = sorted(graph.nodes[i].merkle_hash for i in scope_roots)
    merkle_root = hash_object(sha256_hex("".join(root_hashes)))

    # Satisfaction for in-scope requirements only
    all_results = satisfaction.evaluate(graph)
    sat_table = {
        graph.nodes[i].store_id: {
            "classification": all_results[i].classification,
            "satisfied": all_results[i].satisfied,
            "gaps": all_results[i].gaps,
        }
        for i in sorted(in_scope_reqs, key=lambda i: graph.nodes[i].store_id)
    }

    # Suspect links touching in-scope nodes
    suspect = [
        {"edgeId": e.iri, "edgeType": e.edge_type, "linkState": e.link_state.value}
        for e in graph.edges
        if e.edge_type in STRONG_EDGE_TYPES
        and e.link_state != LinkState.ACTIVE
        and (e.from_iri in all_in_scope or e.to_iri in all_in_scope)
    ]

    # Stale outcomes for in-scope test specs
    current_sha = _majority_sha(graph)
    ts_in_scope = {i for i in all_in_scope
                   if graph.nodes[i].node_type == "TestSpecification"}
    stale = []
    for ts_iri in sorted(ts_in_scope, key=lambda i: graph.nodes[i].store_id):
        for c_edge in graph.incoming(ts_iri, "seg:Confirms"):
            outcome = graph.nodes[c_edge.from_iri]
            if outcome.store_item.get("repoBSha") != current_sha:
                stale.append({
                    "outcomeId": outcome.store_id,
                    "recordedSha": outcome.store_item["repoBSha"],
                    "currentSha": current_sha,
                })

    # Proof status
    all_satisfied = all(all_results[i].satisfied for i in in_scope_reqs)
    proof_status = "ready" if (all_satisfied and not suspect and not stale) else "blocked"

    # Node manifest
    manifest = [
        {
            "id": graph.nodes[i].iri,
            "storeId": graph.nodes[i].store_id,
            "nodeType": graph.nodes[i].node_type,
            "seg:nodeHash":   hash_object(graph.nodes[i].node_hash),
            "seg:merkleHash": hash_object(graph.nodes[i].merkle_hash),
        }
        for i in sorted(all_in_scope, key=lambda i: graph.nodes[i].store_id)
    ]

    # Deterministic snapshot ID from scope content
    snapshot_id = sha256_hex("".join(sorted(scope)))[:16]

    return {
        "snapshotId": snapshot_id,
        "proofStatus": proof_status,
        "scopeSignal": scope_signal,
        "merkleRoot": merkle_root,
        "satisfaction": sat_table,
        "suspectLinks": suspect,
        "staleOutcomes": stale,
        "nodeManifest": manifest,
    }


# ── Workflow 3 ────────────────────────────────────────────────────────────────

def detect_suspect(graph: Graph) -> dict:
    raise NotImplementedError("detect_suspect — step 6")


# ── shared helpers ────────────────────────────────────────────────────────────

def _majority_sha(graph: Graph) -> str:
    shas = [n.store_item["repoBSha"] for n in graph.nodes.values()
            if n.node_type == "TestOutcome"]
    return Counter(shas).most_common(1)[0][0] if shas else ""


def _expand_req_scope(initial_iris: list[str], graph: Graph) -> set[str]:
    """Expand requirement IRIs to include all children via seg:Refines."""
    in_scope: set[str] = set()
    queue = list(initial_iris)
    while queue:
        iri = queue.pop()
        if iri in in_scope:
            continue
        in_scope.add(iri)
        for e in graph.incoming(iri, "seg:Refines"):   # children point TO parent
            queue.append(e.from_iri)
    return in_scope


def _expand_to_impl_ts(in_scope_reqs: set[str], graph: Graph) -> set[str]:
    """Add implementations, test specs, outcomes, and waivers reachable from in-scope requirements."""
    all_in_scope = set(in_scope_reqs)
    for req_iri in in_scope_reqs:
        for e in graph.incoming(req_iri, "seg:Implements"):
            all_in_scope.add(e.from_iri)
        for e in graph.incoming(req_iri, "seg:Verifies"):
            ts_iri = e.from_iri
            all_in_scope.add(ts_iri)
            for ce in graph.incoming(ts_iri, "seg:Confirms"):
                outcome_iri = ce.from_iri
                all_in_scope.add(outcome_iri)
                for we in graph.incoming(outcome_iri, "seg:Excuses"):
                    all_in_scope.add(we.from_iri)
    return all_in_scope


def _scope_roots(in_scope_reqs: set[str], graph: Graph) -> list[str]:
    """In-scope reqs whose parent (if any) is outside the scope."""
    return [
        iri for iri in in_scope_reqs
        if not any(e.to_iri in in_scope_reqs
                   for e in graph.outgoing(iri, "seg:Refines"))
    ]


def _top_level_reqs(graph: Graph) -> list[str]:
    """Requirements with no outgoing seg:Refines edge (top of the hierarchy)."""
    reqs_with_parent = {e.from_iri for e in graph.edges if e.edge_type == "seg:Refines"}
    return [iri for iri, n in graph.nodes.items()
            if n.node_type == "Requirement" and iri not in reqs_with_parent]


def compute_dot_state(graph: Graph, scope_iris: list[str] | None = None):
    """Compute a DotState for dot_render.render().

    scope_iris — requirement IRIs already resolved by the CLI; None means
                 show the full graph (consistency --dot).
    """
    from dot_render import DotState

    results = satisfaction.evaluate(graph)
    current_sha = _majority_sha(graph)

    req_status: dict[str, str] = {}
    for iri, r in results.items():
        if r.classification == "orphan":
            req_status[iri] = "orphan"
        elif r.satisfied:
            req_status[iri] = "satisfied"
        else:
            req_status[iri] = "unsatisfied"

    outcome_status: dict[str, str] = {}
    for iri, node in graph.nodes.items():
        if node.node_type != "TestOutcome":
            continue
        item = node.store_item
        if current_sha and item.get("repoBSha") != current_sha:
            outcome_status[iri] = "stale"
        elif item["outcome"] == "PASS":
            outcome_status[iri] = "pass"
        elif graph.incoming(iri, "seg:Excuses"):
            outcome_status[iri] = "fail_waived"
        else:
            outcome_status[iri] = "fail"

    in_scope: set[str] | None = None
    if scope_iris is not None:
        in_scope_reqs = _expand_req_scope(scope_iris, graph)
        in_scope = _expand_to_impl_ts(in_scope_reqs, graph)

    return DotState(req_status=req_status, outcome_status=outcome_status,
                    in_scope=in_scope)
