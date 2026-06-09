"""DOT format renderer for the SEG prototype graph.

Two modes:
  render(graph)         — static, type-based colours  (dump --dot)
  render(graph, state)  — state overlay: satisfaction, outcome status,
                          link states, and optional scope dimming
                          (consistency --dot, proof <pat> --dot)
"""
from __future__ import annotations

from dataclasses import dataclass

from graph_model import Edge, Graph, LinkState, Node, STRONG_EDGE_TYPES


@dataclass
class DotState:
    req_status:     dict[str, str]    # iri → "satisfied"|"unsatisfied"|"orphan"
    outcome_status: dict[str, str]    # iri → "pass"|"fail_waived"|"fail"|"stale"
    in_scope:       set[str] | None = None   # None = every node in scope
    mutated_nodes:  set[str]         = None  # iris whose node_hash changed (suspect origin)


# ── colour tables ─────────────────────────────────────────────────────────────

_STATIC: dict[str, tuple[str, str]] = {      # node_type → (fill, shape)
    "Requirement":       ('#AED6F1', 'box'),
    "Implementation":    ('#A9DFBF', 'ellipse'),
    "TestSpecification": ('#FAD7A0', 'hexagon'),
    "TestOutcome":       ('#F9E79F', 'note'),
    "Waiver":            ('#F5CBA7', 'octagon'),
}

_REQ_FILL: dict[str, str] = {
    "satisfied":   '#ABEBC6',   # green
    "unsatisfied": '#F1948A',   # red
    "orphan":      '#F9E79F',   # yellow
}

_OUTCOME_FILL: dict[str, str] = {
    "pass":        '#ABEBC6',   # green
    "fail_waived": '#F1948A',   # red (waiver shown via Excuses edge)
    "fail":        '#F1948A',   # red
    "stale":       '#BDC3C7',   # grey
}

_STRONG_COLOR: dict[str, str] = {
    "seg:Refines":    '#2980B9',
    "seg:Implements": '#27AE60',
    "seg:Verifies":   '#E67E22',
}

_SINK_COLOR: dict[str, str] = {
    "seg:Confirms":  '#7F8C8D',
    "seg:Witnesses": '#7F8C8D',
    "seg:Excuses":   '#C0392B',
}

# link_state value → (dot-style, colour-override-or-None, penwidth)
_LINK_STATE: dict[str, tuple[str, str | None, float]] = {
    "active":              ('solid',  None,      1.0),
    "pending":             ('dashed', '#95A5A6', 1.0),
    "directlyOutdated":    ('solid',  '#E74C3C', 2.5),
    "transitivelySuspect": ('dashed', '#E74C3C', 1.5),
    "doublyOutdated":      ('solid',  '#C0392B', 3.0),
    "broken":              ('solid',  '#7B241C', 3.5),
}

_DIM_FILL = '#EAECEE'
_DIM_FONT = '#95A5A6'
_DIM_EDGE = '#D5D8DC'


# ── public API ────────────────────────────────────────────────────────────────

def render(graph: Graph, state: DotState | None = None) -> str:
    lines = [
        "digraph seg {",
        '  graph [rankdir=RL, fontname="Helvetica"];',
        '  node  [fontname="Helvetica", fontsize=11];',
        '  edge  [fontname="Helvetica", fontsize=9];',
        "",
        "  // nodes",
    ]
    for node in sorted(graph.nodes.values(), key=lambda n: n.store_id):
        lines.append(f'  "{node.store_id}" [{_node_attrs(node, state)}];')
    lines.append("")
    lines.append("  // edges")
    for edge in graph.edges:
        from_sid = graph.nodes[edge.from_iri].store_id
        to_sid   = graph.nodes[edge.to_iri].store_id
        lines.append(f'  "{from_sid}" -> "{to_sid}" [{_edge_attrs(edge, state)}];')
    lines.append("}")
    return "\n".join(lines)


# ── node styling ──────────────────────────────────────────────────────────────

def _node_attrs(node: Node, state: DotState | None) -> str:
    fill_default, shape = _STATIC.get(node.node_type, ('#FFFFFF', 'ellipse'))
    label = f"{node.store_id}\\n{node.node_type}"

    if state is None:
        return (f'shape={shape}, style=filled, '
                f'fillcolor="{fill_default}", label="{label}"')

    is_mutated = state.mutated_nodes and node.iri in state.mutated_nodes

    if state.in_scope is not None and node.iri not in state.in_scope:
        extra = ', peripheries=2' if is_mutated else ''
        return (f'shape={shape}, style=filled, fillcolor="{_DIM_FILL}", '
                f'fontcolor="{_DIM_FONT}", label="{label}"{extra}')

    peripheries = ', peripheries=2' if is_mutated else ''

    if node.node_type == "Requirement":
        fill = _REQ_FILL.get(state.req_status.get(node.iri, ""), fill_default)
    elif node.node_type == "TestOutcome":
        status = state.outcome_status.get(node.iri, "")
        fill = _OUTCOME_FILL.get(status, fill_default)
        if status == "stale":
            return (f'shape={shape}, style="filled,dashed", '
                    f'fillcolor="{fill}", label="{label}"{peripheries}')
    else:
        fill = fill_default

    return f'shape={shape}, style=filled, fillcolor="{fill}", label="{label}"{peripheries}'


# ── edge styling ──────────────────────────────────────────────────────────────

def _edge_attrs(edge: Edge, state: DotState | None) -> str:
    label = edge.edge_type.split(":")[-1]

    if state is not None and state.in_scope is not None:
        if edge.from_iri not in state.in_scope and edge.to_iri not in state.in_scope:
            return (f'style=dashed, color="{_DIM_EDGE}", '
                    f'fontcolor="{_DIM_EDGE}", label="{label}"')

    if edge.edge_type in STRONG_EDGE_TYPES:
        type_color = _STRONG_COLOR[edge.edge_type]
        if state is None or edge.link_state == LinkState.ACTIVE:
            return f'color="{type_color}", fontcolor="{type_color}", label="{label}"'
        ls_val = edge.link_state.value if edge.link_state else "active"
        style, color_ov, pw = _LINK_STATE.get(ls_val, ('solid', '#E74C3C', 2.0))
        c = color_ov or type_color
        return (f'style={style}, color="{c}", fontcolor="{c}", '
                f'penwidth={pw}, label="{label}\\n[{ls_val}]"')

    c = _SINK_COLOR.get(edge.edge_type, '#7F8C8D')
    return f'style=dashed, color="{c}", fontcolor="{c}", label="{label}"'
