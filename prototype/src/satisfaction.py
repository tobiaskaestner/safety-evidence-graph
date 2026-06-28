"""Recursive requirement satisfaction check — DEC-001.

Satisfaction rules:
  Leaf   (no incoming seg:Refines edges):
      satisfied iff ≥1 active seg:Verifies edge
                AND ≥1 active seg:Implements edge
                AND every confirming outcome is PASS or validly waived
                AND no confirming outcome is stale (repoBSha mismatch).
  Non-leaf (≥1 incoming seg:Refines edges):
      satisfied iff every child is satisfied
                AND enforce-if-present: any direct verifies/implements
                    the parent carries must also pass.
  Orphan (no children, no coverage edges): never satisfied.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from graph_model import Graph, LinkState


@dataclass
class ReqResult:
    req_iri: str
    store_id: str
    classification: str   # "leaf" | "non-leaf" | "orphan"
    satisfied: bool
    gaps: list[str] = field(default_factory=list)


def evaluate(graph: Graph) -> dict[str, ReqResult]:
    """Return a ReqResult keyed by IRI for every Requirement node."""
    current_sha = _majority_sha(graph)
    memo: dict[str, ReqResult] = {}
    for iri, node in graph.nodes.items():
        if node.node_type == "Requirement" and iri not in memo:
            _eval(iri, graph, current_sha, memo, frozenset())
    return memo


# ── helpers ───────────────────────────────────────────────────────────────────

def _majority_sha(graph: Graph) -> str:
    """Infer the 'current' repo-B SHA as the most common value across outcomes."""
    shas = [
        n.store_item["repoBSha"]
        for n in graph.nodes.values()
        if n.node_type == "TestOutcome"
    ]
    return Counter(shas).most_common(1)[0][0] if shas else ""


def _eval(
    iri: str,
    graph: Graph,
    current_sha: str,
    memo: dict[str, ReqResult],
    stack: frozenset[str],
) -> ReqResult:
    if iri in memo:
        return memo[iri]
    if iri in stack:
        raise ValueError(f"Cycle in refines DAG at {iri}")

    node = graph.nodes[iri]
    # Children = requirement nodes that declare this one as their parent via seg:Refines.
    # Refines direction: from=child → to=parent, so incoming(parent) gives children.
    children = [e.from_iri for e in graph.incoming(iri, "seg:Refines")]
    has_verifies = bool(graph.incoming(iri, "seg:Verifies"))
    has_implements = bool(graph.incoming(iri, "seg:Implements"))

    if not children and not has_verifies and not has_implements:
        r = ReqResult(iri, node.store_id, "orphan", False,
                      ["no children and no coverage edges"])
        memo[iri] = r
        return r

    gaps: list[str] = []

    if children:
        classification = "non-leaf"
        for child_iri in children:
            child = _eval(child_iri, graph, current_sha, memo, stack | {iri})
            if not child.satisfied:
                gaps.append(f"child {child.store_id} not satisfied")
        if has_verifies or has_implements:
            # enforce-if-present: parent carries direct coverage → must also pass
            gaps.extend(_coverage_gaps(iri, graph, current_sha))
    else:
        classification = "leaf"
        gaps = _coverage_gaps(iri, graph, current_sha)

    r = ReqResult(iri, node.store_id, classification, not gaps, gaps)
    memo[iri] = r
    return r


def _coverage_gaps(req_iri: str, graph: Graph, current_sha: str) -> list[str]:
    """Return gap messages for missing/inactive edges or invalid outcomes."""
    gaps: list[str] = []

    active_v = [e for e in graph.incoming(req_iri, "seg:Verifies")
                if e.link_state == LinkState.ACTIVE]
    if not active_v:
        gaps.append("no active seg:Verifies edge")

    active_i = [e for e in graph.incoming(req_iri, "seg:Implements")
                if e.link_state == LinkState.ACTIVE]
    if not active_i:
        gaps.append("no active seg:Implements edge")

    for v_edge in graph.incoming(req_iri, "seg:Verifies"):
        ts_iri = v_edge.from_iri
        for c_edge in graph.incoming(ts_iri, "seg:Confirms"):
            outcome_node = graph.nodes[c_edge.from_iri]
            item = outcome_node.store_item
            recorded_sha = item.get("repoBSha", "")
            if current_sha and recorded_sha != current_sha:
                gaps.append(
                    f"outcome {outcome_node.store_id} is stale "
                    f"(SHA {recorded_sha[:8]}… ≠ {current_sha[:8]}…)"
                )
                continue
            if item["outcome"] != "PASS":
                excused = bool(graph.incoming(c_edge.from_iri, "seg:Excuses"))
                if not excused:
                    gaps.append(
                        f"outcome {outcome_node.store_id} is {item['outcome']} and unwaived"
                    )

    return gaps
