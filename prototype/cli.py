"""Command-line entry point for the three SEG prototype workflows.

Usage:
    python cli.py dump [--nodes] [--edges] [--hashes] [--dot]
    python cli.py consistency
    python cli.py proof <pattern> [<pattern> ...]
    python cli.py suspect

dump flags (no flags = show everything):
    --nodes   emitted node records as JSON
    --edges   emitted edge records as JSON
    --hashes  per-node sub-hashes, nodeHash, merkleHash
    --dot     graph in DOT format (pipe to: dot -Tsvg -o graph.svg)

proof:
    Each <pattern> is a Python regex matched (fullmatch) against requirement
    store_ids. Multiple patterns are OR-ed; duplicates are removed.
    Examples:
        python cli.py proof 'SYS-REQ-.*'          # both system reqs
        python cli.py proof 'REQ-00[123]'          # three leaves
        python cli.py proof 'SYS-REQ-001' 'REQ-.*' # union
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STORE = Path(__file__).parent / "store.json"


def _load():
    from loader import load, emit_all_records
    graph, items = load(STORE)
    records = emit_all_records(graph)
    return graph, records


# ── scope resolution ──────────────────────────────────────────────────────────

def _resolve_scope(patterns: list[str], graph) -> list[str]:
    """Match regex patterns against requirement store_ids; return deduplicated IRIs."""
    req_nodes = [n for n in graph.nodes.values() if n.node_type == "Requirement"]
    seen: set[str] = set()
    result: list[str] = []
    for raw in patterns:
        try:
            pat = re.compile(raw)
        except re.error as exc:
            print(f"error: invalid regex {raw!r}: {exc}", file=sys.stderr)
            sys.exit(1)
        hits = [n for n in req_nodes if pat.fullmatch(n.store_id)]
        if not hits:
            print(f"warning: pattern {raw!r} matched no requirements", file=sys.stderr)
        for n in hits:
            if n.iri not in seen:
                seen.add(n.iri)
                result.append(n.iri)
    return result


# ── dump sections ─────────────────────────────────────────────────────────────

def _dump_nodes(records: dict) -> None:
    print("=" * 70)
    print("EMITTED NODE RECORDS")
    print("=" * 70)
    for group in ("requirement_nodes", "implementation_nodes", "ts_nodes",
                  "outcome_nodes", "waiver_nodes"):
        print(f"\n── {group} ──")
        for rec in records[group]:
            print(json.dumps(rec, indent=2))


def _dump_edges(records: dict) -> None:
    print("=" * 70)
    print("EMITTED EDGE RECORDS")
    print("=" * 70)
    for group in ("refines_edges", "implements_edges", "verifies_edges",
                  "confirms_edges", "witnesses_edges", "excuses_edges"):
        print(f"\n── {group} ──")
        for rec in records[group]:
            print(json.dumps(rec, indent=2))


def _dump_hashes(graph) -> None:
    print("=" * 70)
    print("NODE HASHES (store_id → nodeHash, merkleHash)")
    print("=" * 70)
    for node in sorted(graph.nodes.values(), key=lambda n: n.store_id):
        print(f"\n  {node.store_id} ({node.node_type})")
        for k, v in node.sub_hashes.items():
            print(f"    {k:12s}: {v}")
        if len(node.sub_hashes) > 1:
            print(f"    {'nodeHash':12s}: {node.node_hash}")
        print(f"    {'merkleHash':12s}: {node.merkle_hash}")


_NODE_STYLES: dict[str, str] = {
    "Requirement":       'shape=box,      style=filled, fillcolor="#AED6F1"',
    "Implementation":    'shape=ellipse,  style=filled, fillcolor="#A9DFBF"',
    "TestSpecification": 'shape=hexagon,  style=filled, fillcolor="#FAD7A0"',
    "TestOutcome":       'shape=note,     style=filled, fillcolor="#F9E79F"',
    "Waiver":            'shape=octagon,  style=filled, fillcolor="#F5CBA7"',
}

_EDGE_STYLES: dict[str, str] = {
    "seg:Refines":    'color="#2980B9", fontcolor="#2980B9", label="Refines"',
    "seg:Implements": 'color="#27AE60", fontcolor="#27AE60", label="Implements"',
    "seg:Verifies":   'color="#E67E22", fontcolor="#E67E22", label="Verifies"',
    "seg:Confirms":   'style=dashed, color="#7F8C8D", fontcolor="#7F8C8D", label="Confirms"',
    "seg:Witnesses":  'style=dashed, color="#7F8C8D", fontcolor="#7F8C8D", label="Witnesses"',
    "seg:Excuses":    'style=dashed, color="#C0392B", fontcolor="#C0392B", label="Excuses"',
}


def _dump_dot(graph) -> None:
    lines = [
        "digraph seg {",
        '  graph [rankdir=LR, fontname="Helvetica"];',
        '  node  [fontname="Helvetica", fontsize=11];',
        '  edge  [fontname="Helvetica", fontsize=9];',
        "",
    ]
    lines.append("  // nodes")
    for node in sorted(graph.nodes.values(), key=lambda n: n.store_id):
        dot_id = f'"{node.store_id}"'
        style = _NODE_STYLES.get(node.node_type, "")
        label = f"{node.store_id}\\n{node.node_type}"
        lines.append(f"  {dot_id} [{style}, label=\"{label}\"];")
    lines.append("")
    lines.append("  // edges")
    for edge in graph.edges:
        from_id = f'"{graph.nodes[edge.from_iri].store_id}"'
        to_id = f'"{graph.nodes[edge.to_iri].store_id}"'
        style = _EDGE_STYLES.get(edge.edge_type, "")
        lines.append(f"  {from_id} -> {to_id} [{style}];")
    lines.append("}")
    print("\n".join(lines))


def cmd_dump(flags: argparse.Namespace) -> None:
    graph, records = _load()
    show_all = not (flags.nodes or flags.edges or flags.hashes or flags.dot)

    if show_all or flags.nodes:
        _dump_nodes(records)
    if show_all or flags.edges:
        if show_all or flags.nodes:
            print()
        _dump_edges(records)
    if show_all or flags.hashes:
        if show_all or flags.nodes or flags.edges:
            print()
        _dump_hashes(graph)
    if show_all or flags.dot:
        if show_all or flags.nodes or flags.edges or flags.hashes:
            print()
        _dump_dot(graph)


# ── other commands ────────────────────────────────────────────────────────────

def cmd_consistency() -> None:
    from workflows import consistency
    graph, _ = _load()
    result = consistency(graph)
    print(json.dumps(result, indent=2))


def cmd_proof(patterns: list[str]) -> None:
    from workflows import generate_proof
    graph, _ = _load()
    scope = _resolve_scope(patterns, graph)
    if not scope:
        print("error: no requirements matched — nothing to prove", file=sys.stderr)
        sys.exit(1)
    matched_ids = [graph.nodes[iri].store_id for iri in scope]
    print(f"scope: {matched_ids}", file=sys.stderr)
    result = generate_proof(graph, scope)
    print(json.dumps(result, indent=2))


def cmd_suspect() -> None:
    from workflows import detect_suspect
    graph, _ = _load()
    result = detect_suspect(graph)
    print(json.dumps(result, indent=2))


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)

    match argv[0]:
        case "dump":
            p = argparse.ArgumentParser(prog="cli.py dump", add_help=True)
            p.add_argument("--nodes",  action="store_true", help="emitted node records (JSON)")
            p.add_argument("--edges",  action="store_true", help="emitted edge records (JSON)")
            p.add_argument("--hashes", action="store_true", help="per-node sub/node/merkle hashes")
            p.add_argument("--dot",    action="store_true", help="graph in DOT format")
            cmd_dump(p.parse_args(argv[1:]))
        case "consistency":
            cmd_consistency()
        case "proof":
            if len(argv) < 2:
                print("Usage: python cli.py proof <pattern> [<pattern> ...]")
                sys.exit(1)
            cmd_proof(argv[1:])
        case "suspect":
            cmd_suspect()
        case _:
            print(f"Unknown command: {argv[0]!r}")
            print(__doc__)
            sys.exit(1)


if __name__ == "__main__":
    main()
