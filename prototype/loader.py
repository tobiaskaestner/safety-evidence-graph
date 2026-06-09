"""store.json -> hashed in-memory graph + schema-valid emitted records.

Node records carry NO hashes (per schema design: hashes are computed transiently
and persisted only inside sealed proof documents). Hashes live in the in-memory
Graph. Edge records for strong edges carry seg:edgeHash and seg:linkState.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from graph_model import Edge, Graph, LinkState, Node, STRONG_EDGE_TYPES
from hashing import (
    compute_edge_hash,
    compute_merkle_hash,
    compute_node_hash,
    compute_sub_hashes,
    hash_object,
)

NS = "https://seg.example/proto"
_DUMMY_PY_SOURCE = "store.json"


# ── IRI builders ─────────────────────────────────────────────────────────────

def _iri(*parts: str) -> str:
    return NS + "/" + "/".join(parts)


def _req_iri(store_id: str) -> str:
    return _iri("req", store_id)


def _impl_iri(name: str) -> str:
    return _iri("impl", name)


def _ts_iri(store_id: str) -> str:
    return _iri("ts", store_id)


def _outcome_iri(run_id: str, spec_id: str) -> str:
    return _iri("outcome", run_id, spec_id)


def _waiver_iri(store_id: str) -> str:
    return _iri("waiver", store_id)


def _edge_iri(slug: str, *parts: str) -> str:
    return _iri("edge", slug, "-".join(parts))


# ── Main loader ───────────────────────────────────────────────────────────────

def load(store_path: Path) -> tuple[Graph, list[dict]]:
    """Read store.json and build the in-memory graph with all hashes computed.

    Returns (graph, items) where items is the filtered list of store entries
    (comment-only objects stripped).
    """
    raw: list[dict] = json.loads(store_path.read_text())
    items = [r for r in raw if "id" in r]
    index: dict[str, dict] = {item["id"]: item for item in items}
    graph = Graph()

    # Pass 1: nodes
    for item in items:
        store_id = item["id"]
        node_type = item["type"]
        sub = compute_sub_hashes(item["to_hash"])
        nh = compute_node_hash(sub)

        match node_type:
            case "Requirement":
                iri = _req_iri(store_id)
            case "Implementation":
                iri = _impl_iri(item["name"])
            case "TestSpecification":
                iri = _ts_iri(store_id)
            case "TestOutcome":
                iri = _outcome_iri(item["runId"], item["specId"])
            case "Waiver":
                iri = _waiver_iri(store_id)
            case _:
                raise ValueError(f"Unknown node type: {node_type!r}")

        graph.nodes[iri] = Node(
            iri=iri,
            store_id=store_id,
            node_type=node_type,
            sub_hashes=sub,
            node_hash=nh,
            store_item=item,
        )
        graph.store_to_iri[store_id] = iri

    # Pass 2: edges
    for item in items:
        store_id = item["id"]
        from_iri = graph.store_to_iri[store_id]
        from_nh = graph.nodes[from_iri].node_hash

        for parent_id in item.get("refines", []):
            to_iri = graph.store_to_iri[parent_id]
            to_nh = graph.nodes[to_iri].node_hash
            graph.edges.append(Edge(
                iri=_edge_iri("refines", store_id, parent_id),
                edge_type="seg:Refines",
                from_iri=from_iri,
                to_iri=to_iri,
                edge_hash=compute_edge_hash(from_iri, to_iri, "seg:Refines", from_nh, to_nh),
                link_state=LinkState.ACTIVE,
            ))

        for req_id in item.get("implements", []):
            to_iri = graph.store_to_iri[req_id]
            to_nh = graph.nodes[to_iri].node_hash
            graph.edges.append(Edge(
                iri=_edge_iri("implements", item["name"], req_id),
                edge_type="seg:Implements",
                from_iri=from_iri,
                to_iri=to_iri,
                edge_hash=compute_edge_hash(from_iri, to_iri, "seg:Implements", from_nh, to_nh),
                link_state=LinkState.ACTIVE,
            ))

        for req_id in item.get("verifies", []):
            to_iri = graph.store_to_iri[req_id]
            to_nh = graph.nodes[to_iri].node_hash
            graph.edges.append(Edge(
                iri=_edge_iri("verifies", store_id, req_id),
                edge_type="seg:Verifies",
                from_iri=from_iri,
                to_iri=to_iri,
                edge_hash=compute_edge_hash(from_iri, to_iri, "seg:Verifies", from_nh, to_nh),
                link_state=LinkState.ACTIVE,
            ))

        if "specId" in item:
            spec_id = item["specId"]
            run_id = item["runId"]
            graph.edges.append(Edge(
                iri=_edge_iri("confirms", run_id, spec_id),
                edge_type="seg:Confirms",
                from_iri=from_iri,
                to_iri=graph.store_to_iri[spec_id],
            ))

        if "implId" in item:
            impl_id = item["implId"]
            impl_name = index[impl_id]["name"]
            spec_id = item["specId"]
            run_id = item["runId"]
            graph.edges.append(Edge(
                iri=_edge_iri("witnesses", run_id, spec_id, impl_name),
                edge_type="seg:Witnesses",
                from_iri=from_iri,
                to_iri=graph.store_to_iri[impl_id],
            ))

        if "excuses" in item:
            outcome_id = item["excuses"]
            run_id, spec_id = outcome_id.split("/")
            graph.edges.append(Edge(
                iri=_edge_iri("excuses", store_id, run_id, spec_id),
                edge_type="seg:Excuses",
                from_iri=from_iri,
                to_iri=graph.store_to_iri[outcome_id],
            ))

    # Pass 3: Merkle hashes (DAG traversal; raises on cycle)
    _fill_merkle(graph)
    return graph, items


def _fill_merkle(graph: Graph) -> None:
    """Compute merkle_hash for every node.

    A node's merkle hash = H(nodeHash || sorted(merkle hashes of nodes that
    point TO it via strong edges)). Leaf nodes (no incoming strong edges) get
    merkle_hash = sha256(node_hash + []) = sha256(node_hash).
    """
    memo: dict[str, str] = {}

    def _merkle(iri: str, stack: frozenset[str]) -> str:
        if iri in memo:
            return memo[iri]
        if iri in stack:
            raise ValueError(f"Cycle in refines DAG at {iri}")
        deps = [
            e.from_iri for e in graph.edges
            if e.to_iri == iri and e.edge_type in STRONG_EDGE_TYPES
        ]
        mh = compute_merkle_hash(
            graph.nodes[iri].node_hash,
            [_merkle(d, stack | {iri}) for d in deps],
        )
        memo[iri] = mh
        graph.nodes[iri].merkle_hash = mh
        return mh

    for iri in graph.nodes:
        _merkle(iri, frozenset())


# ── Record emitters (schema-valid, no hashes) ─────────────────────────────────

def emit_node_record(node: Node, graph: Graph) -> dict[str, Any]:
    item = node.store_item
    match node.node_type:
        case "Requirement":
            return {
                "id": node.iri,
                "type": "seg:Requirement",
                "name": item["id"],
                "description": item["to_hash"]["nodeHash"],
                "seg:sourceRepo": "repoA",
                "seg:sourcePath": _DUMMY_PY_SOURCE,
            }
        case "Implementation":
            return {
                "id": node.iri,
                "type": "seg:Implementation",
                "name": item["name"],
                "seg:sourceRepo": "repoB",
                # Dummy paths satisfy the .h/.c schema pattern; real paths would
                # be .py — a Python/C schema mismatch to surface (see NOTES.md).
                "seg:sourcePath": {"header": "prototype/store.h", "body": "prototype/store.c"},
            }
        case "TestSpecification":
            return {
                "id": node.iri,
                "type": "seg:TestSpecification",
                "name": item["id"],
                "description": item["to_hash"]["specHash"],
                "seg:sourceRepo": "repoB",
                "seg:sourcePath": _DUMMY_PY_SOURCE,
            }
        case "TestOutcome":
            return {
                "id": node.iri,
                "type": "seg:TestOutcome",
                "name": item["name"],
                "seg:runId": item["runId"],
                "seg:specId": graph.store_to_iri[item["specId"]],
                "seg:repoBSha": item["repoBSha"],
                "seg:outcome": item["outcome"],
                "seg:sourceRepo": "repoC",
                "seg:sourcePath": _DUMMY_PY_SOURCE,
            }
        case "Waiver":
            return {
                "id": node.iri,
                "type": "seg:Waiver",
                "name": item["id"],
                "seg:outcomeId": graph.store_to_iri[item["excuses"]],
                "seg:justification": item["reason"],
                "seg:expiry": item["expiry"],
                "seg:sourceRepo": "repoG",
                "seg:sourcePath": _DUMMY_PY_SOURCE,
            }
        case _:
            raise ValueError(f"Unknown node type: {node.node_type!r}")


def emit_edge_record(edge: Edge) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "id": edge.iri,
        "type": edge.edge_type,
        "seg:from": edge.from_iri,
        "seg:to": edge.to_iri,
    }
    if edge.edge_type in STRONG_EDGE_TYPES:
        rec["seg:edgeHash"] = hash_object(edge.edge_hash)
        rec["seg:linkState"] = edge.link_state.value
    return rec


def emit_all_records(graph: Graph) -> dict[str, list[dict]]:
    """Return schema-valid records grouped by type, ready for validation and display."""
    by_type: dict[str, list[Node]] = {}
    for node in graph.nodes.values():
        by_type.setdefault(node.node_type, []).append(node)

    def node_records(node_type: str) -> list[dict]:
        return [emit_node_record(n, graph) for n in by_type.get(node_type, [])]

    def edge_records(edge_type: str) -> list[dict]:
        return [emit_edge_record(e) for e in graph.edges_of_type(edge_type)]

    return {
        "requirement_nodes": node_records("Requirement"),
        "implementation_nodes": node_records("Implementation"),
        "ts_nodes": node_records("TestSpecification"),
        "outcome_nodes": node_records("TestOutcome"),
        "waiver_nodes": node_records("Waiver"),
        "refines_edges": edge_records("seg:Refines"),
        "implements_edges": edge_records("seg:Implements"),
        "verifies_edges": edge_records("seg:Verifies"),
        "confirms_edges": edge_records("seg:Confirms"),
        "witnesses_edges": edge_records("seg:Witnesses"),
        "excuses_edges": edge_records("seg:Excuses"),
    }
