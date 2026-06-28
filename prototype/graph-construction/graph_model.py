from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LinkState(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DIRECTLY_OUTDATED = "directlyOutdated"
    TRANSITIVELY_SUSPECT = "transitivelySuspect"
    DOUBLY_OUTDATED = "doublyOutdated"
    BROKEN = "broken"


STRONG_EDGE_TYPES: frozenset[str] = frozenset(
    {"seg:Refines", "seg:Implements", "seg:Verifies"}
)


@dataclass
class Node:
    iri: str
    store_id: str
    node_type: str
    sub_hashes: dict[str, str]
    node_hash: str
    merkle_hash: str = ""
    store_item: dict = field(default_factory=dict)


@dataclass
class Edge:
    iri: str
    edge_type: str
    from_iri: str
    to_iri: str
    edge_hash: str = ""
    link_state: LinkState | None = None


@dataclass
class Graph:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    store_to_iri: dict[str, str] = field(default_factory=dict)

    def node_by_store_id(self, store_id: str) -> Node | None:
        return self.nodes.get(self.store_to_iri.get(store_id, ""))

    def edges_of_type(self, edge_type: str) -> list[Edge]:
        return [e for e in self.edges if e.edge_type == edge_type]

    def incoming(self, to_iri: str, edge_type: str | None = None) -> list[Edge]:
        return [
            e for e in self.edges
            if e.to_iri == to_iri and (edge_type is None or e.edge_type == edge_type)
        ]

    def outgoing(self, from_iri: str, edge_type: str | None = None) -> list[Edge]:
        return [
            e for e in self.edges
            if e.from_iri == from_iri and (edge_type is None or e.edge_type == edge_type)
        ]
