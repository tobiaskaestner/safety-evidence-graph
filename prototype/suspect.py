"""Suspect-edge classification and transitive propagation (step 6).

Public API:  classify_edges(graph, changed_node_hashes) → {edge_iri: LinkState}
"""
from __future__ import annotations

from graph_model import Graph, LinkState, STRONG_EDGE_TYPES


def classify_edges(
    graph: Graph,
    changed_node_hashes: dict[str, str],  # iri → new node_hash (changed nodes only)
) -> dict[str, LinkState]:
    """Return new link-states for every strong edge after node mutations.

    Rules:
      directlyOutdated    — one endpoint's hash changed
      doublyOutdated      — both endpoints' hashes changed
      transitivelySuspect — edge itself is unchanged but its from-node is the
                            to-end of a non-active strong edge (propagates BFS)
    """
    changed = set(changed_node_hashes)

    # Step 1: direct classification
    states: dict[str, LinkState] = {}
    for edge in graph.edges:
        if edge.edge_type not in STRONG_EDGE_TYPES:
            continue
        from_ch = edge.from_iri in changed
        to_ch   = edge.to_iri   in changed
        if from_ch and to_ch:
            states[edge.iri] = LinkState.DOUBLY_OUTDATED
        elif from_ch or to_ch:
            states[edge.iri] = LinkState.DIRECTLY_OUTDATED
        else:
            states[edge.iri] = LinkState.ACTIVE

    # Step 2: BFS transitive propagation.
    # A node is "suspect" when it is the *to* end of any non-active strong edge.
    # Any edge whose *from* end is suspect becomes transitivelySuspect, and its
    # *to* end joins the suspect set — propagating up the Refines/evidence chain.
    suspect_nodes: set[str] = {
        e.to_iri
        for e in graph.edges
        if e.edge_type in STRONG_EDGE_TYPES
        and states.get(e.iri) in (LinkState.DIRECTLY_OUTDATED, LinkState.DOUBLY_OUTDATED)
    }

    dirty = True
    while dirty:
        dirty = False
        for edge in graph.edges:
            if edge.edge_type not in STRONG_EDGE_TYPES:
                continue
            if states.get(edge.iri) != LinkState.ACTIVE:
                continue
            if edge.from_iri in suspect_nodes:
                states[edge.iri] = LinkState.TRANSITIVELY_SUSPECT
                suspect_nodes.add(edge.to_iri)
                dirty = True

    return states
