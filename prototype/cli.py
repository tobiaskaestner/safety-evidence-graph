"""Command-line entry point for the three SEG prototype workflows.

Usage:
    python cli.py [--store-file PATH] <command> [options]

Commands:
    dump          [--nodes] [--edges] [--hashes] [--dot]
    consistency   [--dot]
    proof         <pattern> [<pattern> ...] [--dot]
    suspect       --mutate STORE_ID FIELD "new content" [--mutate ...] [--dot]
    generate-store --sys-reqs N --reqs-per-sys-req N [--test-cases-per-req N]
                   [--outcomes-per-test-case N] [--seed N] --out-file PATH

Global flag:
    --store-file PATH   store file to load (default: store-small.json)

Available stores in prototype/:
    store-small.json       — 2 sys-reqs, 5 leaf reqs (hand-crafted; has waivers/stale)
    store-medium.json      — ~10 sys-reqs, up to 6 reqs each
    store-large.json       — ~80 sys-reqs, up to 10 reqs each
    store-extra-large.json — ~1000 sys-reqs, up to 50 reqs each

dump flags (no flags = show everything):
    --nodes   emitted node records as JSON
    --edges   emitted edge records as JSON
    --hashes  per-node sub-hashes, nodeHash, merkleHash
    --dot     graph in DOT format — static, type colours only

consistency / proof --dot:
    Outputs DOT instead of JSON. Nodes and edges are coloured by proof
    state. proof --dot also dims nodes outside the resolved scope.

    Pipe to graphviz:  python cli.py consistency --dot | dot -Tsvg -o out.svg

proof patterns:
    Each <pattern> is a Python regex matched (fullmatch) against
    requirement store_ids. Multiple patterns are OR-ed; duplicates removed.
    Examples:
        python cli.py proof 'SYS-REQ-.*'
        python cli.py proof 'SYS-REQ-001' 'REQ-00[12]'
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STORE = Path(__file__).parent / "store-small.json"


def _load():
    from loader import load, emit_all_records
    graph, items = load(STORE)
    records = emit_all_records(graph)
    return graph, records


# ── scope resolution ──────────────────────────────────────────────────────────

def _resolve_scope(patterns: list[str], graph) -> list[str]:
    """Match regex patterns against requirement store_ids; return deduped IRIs."""
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


def _dump_dot(graph) -> None:
    from dot_render import render
    print(render(graph))


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

def cmd_consistency(flags: argparse.Namespace) -> None:
    from workflows import consistency, compute_dot_state
    from dot_render import render
    graph, _ = _load()
    if flags.dot:
        state = compute_dot_state(graph)
        print(render(graph, state))
    else:
        print(json.dumps(consistency(graph), indent=2))


def cmd_proof(patterns: list[str], dot: bool) -> None:
    from workflows import generate_proof, compute_dot_state
    from dot_render import render
    graph, _ = _load()
    scope = _resolve_scope(patterns, graph)
    if not scope:
        print("error: no requirements matched — nothing to prove", file=sys.stderr)
        sys.exit(1)
    matched_ids = [graph.nodes[iri].store_id for iri in scope]
    print(f"scope: {matched_ids}", file=sys.stderr)
    if dot:
        state = compute_dot_state(graph, scope_iris=scope)
        print(render(graph, state))
    else:
        print(json.dumps(generate_proof(graph, scope), indent=2))


def cmd_suspect(flags: argparse.Namespace) -> None:
    from workflows import detect_suspect, compute_dot_state
    from dot_render import render
    graph, _ = _load()

    patches: dict[str, dict[str, str]] = {}
    for store_id, field, new_val in (flags.mutate or []):
        patches.setdefault(store_id, {})[field] = new_val

    if not patches:
        print("error: specify at least one --mutate STORE_ID FIELD VALUE",
              file=sys.stderr)
        sys.exit(1)

    result = detect_suspect(graph, patches)  # mutates graph.edges link_states in-place

    if flags.dot:
        mutated_iris = {
            graph.store_to_iri[c["storeId"]]
            for c in result["nodeHashChanges"]
            if c["storeId"] in graph.store_to_iri
        }
        state = compute_dot_state(graph, mutated_iris=mutated_iris)
        print(render(graph, state))
    else:
        print(json.dumps(result, indent=2))


def cmd_generate_store(flags: argparse.Namespace) -> None:
    from store_generator import GenConfig, generate
    cfg = GenConfig(
        num_sys_reqs=flags.sys_reqs,
        max_reqs_per_sys_req=flags.reqs_per_sys_req,
        max_test_cases_per_req=flags.test_cases_per_req,
        max_outcomes_per_test_case=flags.outcomes_per_test_case,
        seed=flags.seed,
    )
    items = generate(cfg)
    out = Path(flags.out_file)
    out.write_text(json.dumps(items, indent=2))
    node_count = sum(1 for it in items if "type" in it)
    print(f"wrote {node_count} nodes to {out}", file=sys.stderr)


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    global STORE
    argv = sys.argv[1:]

    # Pre-parse global --store-file before subcommand dispatch
    if "--store-file" in argv:
        idx = argv.index("--store-file")
        if idx + 1 >= len(argv):
            print("error: --store-file requires a path argument", file=sys.stderr)
            sys.exit(1)
        STORE = Path(argv[idx + 1])
        argv = argv[:idx] + argv[idx + 2:]

    if not argv:
        print(__doc__)
        sys.exit(1)

    match argv[0]:
        case "dump":
            p = argparse.ArgumentParser(prog="cli.py dump")
            p.add_argument("--nodes",  action="store_true", help="emitted node records (JSON)")
            p.add_argument("--edges",  action="store_true", help="emitted edge records (JSON)")
            p.add_argument("--hashes", action="store_true", help="per-node sub/node/merkle hashes")
            p.add_argument("--dot",    action="store_true", help="static DOT graph")
            cmd_dump(p.parse_args(argv[1:]))
        case "consistency":
            p = argparse.ArgumentParser(prog="cli.py consistency")
            p.add_argument("--dot", action="store_true",
                           help="DOT graph with state overlay instead of JSON")
            cmd_consistency(p.parse_args(argv[1:]))
        case "proof":
            p = argparse.ArgumentParser(prog="cli.py proof")
            p.add_argument("patterns", nargs="+", help="regex patterns for requirement IDs")
            p.add_argument("--dot", action="store_true",
                           help="DOT graph with scope + state overlay instead of JSON")
            flags = p.parse_args(argv[1:])
            cmd_proof(flags.patterns, flags.dot)
        case "suspect":
            p = argparse.ArgumentParser(prog="cli.py suspect")
            p.add_argument("--mutate", action="append", nargs=3,
                           metavar=("STORE_ID", "FIELD", "NEW_CONTENT"),
                           help="patch a node's to_hash field; repeatable")
            p.add_argument("--dot", action="store_true",
                           help="DOT graph with suspect edges highlighted instead of JSON")
            cmd_suspect(p.parse_args(argv[1:]))
        case "generate-store":
            p = argparse.ArgumentParser(prog="cli.py generate-store")
            p.add_argument("--sys-reqs",               type=int, required=True,
                           help="number of system requirements")
            p.add_argument("--reqs-per-sys-req",       type=int, required=True,
                           help="maximum leaf reqs per system req (actual count varies 1..N)")
            p.add_argument("--test-cases-per-req",     type=int, default=2,
                           help="maximum test specs per leaf req (default 2)")
            p.add_argument("--outcomes-per-test-case", type=int, default=1,
                           help="maximum test outcomes per test spec (default 1)")
            p.add_argument("--seed",                   type=int, default=42,
                           help="RNG seed for reproducibility (default 42)")
            p.add_argument("--out-file",               required=True,
                           help="output path for the generated store JSON")
            cmd_generate_store(p.parse_args(argv[1:]))
        case _:
            print(f"Unknown command: {argv[0]!r}")
            print(__doc__)
            sys.exit(1)


if __name__ == "__main__":
    main()
