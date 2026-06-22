"""
seg_graphviz.py -- render a SEG `Graph` to Graphviz DOT (and SVG/PNG if `dot`
is installed). Reusable across producer / consumer / multi-leaf graphs.

Encodes, visually:
  - node TYPE   -> shape   (requirement=box, testspec=ellipse, impl=component,
                            outcome=note, guarantee=doubleoctagon,
                            manifest=folder, designreview=diamond, waiver=trapezium)
  - node STATE  -> fill    (requirement: satisfied=green, obligation=amber,
                            unsatisfied=red; outcome: PASS=green / non-PASS=red)
  - edge TYPE   -> colour + label (assumes/covers highlighted; witnesses/uses dashed)
  - inactive edge -> grey dashed (capability shown even if unused by a fixture)

`states` maps a requirement id -> 'satisfied'|'obligation'|'unsatisfied'.
"""
import subprocess
import shutil
import html

SHAPE = {
    "requirement": "box", "testspecification": "ellipse",
    "implementation": "component", "testoutcome": "note",
    "guarantee": "doubleoctagon", "manifest": "folder",
    "designreview": "diamond", "waiver": "trapezium",
    "environment": "box3d", "assumption": "note",
}
STATE_FILL = {"satisfied": "#b7e4c7", "obligation": "#ffe08a", "unsatisfied": "#f4a3a3"}
TYPE_FILL = {
    "testspecification": "#d0e6fb", "implementation": "#e6dcf5",
    "guarantee": "#cdb4db", "manifest": "#ffd6a5",
    "designreview": "#caffbf", "waiver": "#ffadad", "environment": "#c3fae8",
    "assumption": "#fff3bf",
}
EDGE = {  # type -> (color, style, penwidth)
    "refines": ("#333333", "solid", 1.4),
    "verifies": ("#1d6fb8", "solid", 1.2),
    "implements": ("#7048e8", "solid", 1.2),
    "confirms": ("#2f9e44", "solid", 1.2),
    "witnesses": ("#2f9e44", "dashed", 1.2),
    "assumes": ("#e8590c", "solid", 2.2),     # the obligation-publishing edge
    "covers": ("#9c36b5", "solid", 2.2),       # reliance
    "conformsTo": ("#9c36b5", "dashed", 1.8),  # pre-import declaration: resolves to covers
    "reviews": ("#0c8599", "solid", 1.2),
    "uses": ("#868e96", "dashed", 1.0),
    "excuses": ("#e03131", "dotted", 1.2),
    "surrogate_for": ("#0ca678", "dashed", 1.6),   # witness env stands in for an assumption
    "ran_on": ("#495057", "dotted", 1.2),           # outcome provenance: which env produced it
}


def _esc(s):
    return html.escape(str(s)).replace("\n", "<br/>")


def _node_fill(n, states):
    if n.type == "requirement":
        return STATE_FILL.get(states.get(n.id, ""), "#ffffff")
    if n.type == "testoutcome":
        return "#b7e4c7" if n.fields.get("outcome") == "PASS" else "#f4a3a3"
    return TYPE_FILL.get(n.type, "#f1f3f5")


def _node_label(n, states):
    extra = ""
    if n.type == "requirement" and n.id in states:
        extra = f'<br/><font point-size="9">[{states[n.id]}]</font>'
    elif n.type == "testoutcome" and "outcome" in n.fields:
        extra = f'<br/><font point-size="9">{_esc(n.fields["outcome"])}</font>'
    return (f'<<b>{_esc(n.id)}</b>'
            f'<br/><font point-size="8" color="#555555">{_esc(n.type)}</font>{extra}>')


def _legend():
    # a compact legend cluster: node shapes/states + edge types
    rows = []
    rows.append('subgraph cluster_legend {')
    rows.append('  label="legend"; fontsize=11; color="#adb5bd"; style="rounded";')
    # node-type/state samples
    samples = [
        ("L_req_sat", "requirement\\n(satisfied)", "box", "#b7e4c7"),
        ("L_req_obl", "requirement\\n(obligation)", "box", "#ffe08a"),
        ("L_req_uns", "requirement\\n(unsatisfied)", "box", "#f4a3a3"),
        ("L_ts", "testspecification", "ellipse", "#d0e6fb"),
        ("L_impl", "implementation", "component", "#e6dcf5"),
        ("L_out", "testoutcome", "note", "#b7e4c7"),
        ("L_guar", "guarantee", "doubleoctagon", "#cdb4db"),
        ("L_man", "manifest", "folder", "#ffd6a5"),
        ("L_dr", "designreview", "diamond", "#caffbf"),
        ("L_env", "environment", "box3d", "#c3fae8"),
        ("L_asm", "assumption\\n(imported)", "note", "#fff3bf"),
    ]
    for nid, lab, shape, fill in samples:
        rows.append(f'  {nid} [label="{lab}", shape={shape}, style=filled, '
                    f'fillcolor="{fill}", fontsize=9];')
    # invisible chain to keep legend compact
    rows.append("  " + " -> ".join(s[0] for s in samples) + " [style=invis];")
    # edge-type samples
    rows.append('  subgraph cluster_edges {')
    rows.append('    label="edge types"; fontsize=10; color="#ced4da";')
    prev = None
    for i, (etype, (color, style, pw)) in enumerate(EDGE.items()):
        a, b = f"E{i}a", f"E{i}b"
        rows.append(f'    {a} [shape=point, width=0.02, color="#888888"];')
        rows.append(f'    {b} [shape=point, width=0.02, color="#888888"];')
        rows.append(f'    {a} -> {b} [label="{etype}", color="{color}", '
                    f'style={style}, penwidth={pw}, fontsize=9, fontcolor="{color}"];')
        if prev:
            rows.append(f'    {prev} -> {a} [style=invis];')
        prev = b
    rows.append('  }')
    rows.append('}')
    return "\n".join(rows)


def to_dot(graph, states=None, inactive=None, title=None):
    states = states or {}
    inactive = set(inactive or [])
    out = ['digraph SEG {', '  rankdir=BT; bgcolor="white";',
           '  node [fontname="Helvetica", fontsize=11];',
           '  edge [fontname="Helvetica"];']
    if title:
        out.append(f'  labelloc="t"; fontsize=14; label="{title}";')
    for n in graph.nodes:
        out.append(f'  {n.id} [label={_node_label(n, states)}, '
                   f'shape={SHAPE.get(n.type, "oval")}, style=filled, '
                   f'fillcolor="{_node_fill(n, states)}", color="#495057"];')
    for e in graph.edges:
        color, style, pw = EDGE.get(e.type, ("#868e96", "solid", 1.0))
        label, arrow = e.type, "normal"
        kind = getattr(e, "kind", "")
        if e.type == "covers" and kind:                 # provenance of a reliance
            label = f"covers ({kind})"
            arrow = "onormal" if kind == "minted" else "normal"   # open = derived
        if e.id in inactive:
            color, style = "#adb5bd", "dashed"
        out.append(f'  {e.src} -> {e.dst} [label="{label}", color="{color}", '
                   f'style={style}, penwidth={pw}, arrowhead={arrow}, '
                   f'fontsize=9, fontcolor="{color}"];')
    # provenance: an imported node sits sealed UNDER its manifest (not an Edge object)
    for nid, man in graph.referenced_under.items():
        out.append(f'  {nid} -> {man} [label="referenced_under", color="#adb5bd", '
                   f'style=dotted, penwidth=1.0, fontsize=8, fontcolor="#868e96"];')
    out.append(_legend())
    out.append('}')
    return "\n".join(out)


def render(graph, states=None, inactive=None, title=None, path="seg_graph", fmt="svg"):
    dot = to_dot(graph, states, inactive, title)
    dot_path = f"{path}.dot"
    with open(dot_path, "w") as f:
        f.write(dot)
    rendered = None
    if shutil.which("dot"):
        rendered = f"{path}.{fmt}"
        subprocess.run(["dot", f"-T{fmt}", dot_path, "-o", rendered], check=True)
    return dot_path, rendered


def render_bom(bom_path, path="bom_graph", fmt="svg"):
    """Render an SPDX vectorized safety-BOM: SpdxDocument -> Boms -> G/A, with
    the Merkle root, per-Bom member hashes, and assumes relationships."""
    import json as _json
    import re as _re
    import shutil as _sh
    import subprocess as _sp
    g = _json.load(open(bom_path))["@graph"]
    did = lambda iri: "n_" + _re.sub(r"[^0-9A-Za-z]", "_", iri.split("#")[-1])
    short = lambda h: (h[:10] + "..") if h else ""
    doc = next(n for n in g if n["type"] == "SpdxDocument")
    mroot = next((h["hashValue"] for h in doc.get("verifiedUsing", [])
                  if h.get("algorithm") == "sha256"), "")
    o = ['digraph BOM {', '  rankdir=TB; bgcolor="white";',
         '  node [fontname="Helvetica"]; edge [fontname="Helvetica", fontsize=9];',
         '  labelloc="t"; fontsize=14; label="SPDX FuSa safety-BOM (contract vector + Merkle commitment)";']
    o.append(f'  {did(doc["spdxId"])} [label=<<b>SpdxDocument</b>'
             f'<br/><font point-size="8">{doc.get("name","")}</font>'
             f'<br/><font point-size="8" color="#9c36b5">merkle root {short(mroot)}</font>>, '
             f'shape=tab, style=filled, fillcolor="#ffd6a5"];')
    for b in g:
        if b.get("type") != "Bom":
            continue
        mh = next((h["hashValue"] for h in b.get("verifiedUsing", [])
                   if h.get("algorithm") == "sha256"), "")
        o.append(f'  {did(b["spdxId"])} [label=<<b>{b["name"]}</b><br/><font point-size="8">Bom</font>'
                 f'<br/><font point-size="8" color="#9c36b5">member {short(mh)}</font>>, '
                 f'shape=folder, style=filled, fillcolor="#ffe8cc"];')
        o.append(f'  {did(doc["spdxId"])} -> {did(b["spdxId"])} [label="rootElement", color="#868e96"];')
        gid = b["rootElement"][0]
        o.append(f'  {did(b["spdxId"])} -> {did(gid)} [label="rootElement", color="#333333"];')
        for e in b["element"]:
            if e != gid:
                o.append(f'  {did(b["spdxId"])} -> {did(e)} [label="element", color="#adb5bd", style=dashed];')
    for n in g:
        if n.get("type") == "Requirement":
            o.append(f'  {did(n["spdxId"])} [label=<<b>{n["name"]}</b>'
                     f'<br/><font point-size="8">Requirement (G)</font>>, shape=box, '
                     f'style=filled, fillcolor="#b7e4c7"];')
        elif n.get("type") == "functionalsafety_Assumption":
            o.append(f'  {did(n["spdxId"])} [label=<<b>{n["name"]}</b>'
                     f'<br/><font point-size="8">Assumption (A)</font>>, shape=note, '
                     f'style=filled, fillcolor="#ffe08a"];')
    for n in g:
        if n.get("type") == "Relationship" and n.get("relationshipType") == "assumes":
            for to in n["to"]:
                o.append(f'  {did(n["from"])} -> {did(to)} '
                         f'[label="assumes", color="#e8590c", penwidth=2.0];')
    o.append("}")
    open(f"{path}.dot", "w").write("\n".join(o))
    if _sh.which("dot"):
        _sp.run(["dot", f"-T{fmt}", f"{path}.dot", "-o", f"{path}.{fmt}"], check=True)
        _sp.run(["dot", "-Tpng", f"{path}.dot", "-o", f"{path}.png"], check=True)
    return f"{path}.{fmt}"


if __name__ == "__main__":
    render_bom("safety_bom.jsonld")
    print("wrote bom_graph.dot / .svg / .png")
