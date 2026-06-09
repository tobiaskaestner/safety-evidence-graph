"""Command-line entry point for the three SEG prototype workflows.

Usage:
    python cli.py dump                        # inspect emitted records and hashes
    python cli.py consistency                 # workflow 1
    python cli.py proof <req-id> [...]        # workflow 2
    python cli.py suspect                     # workflow 3 (human edits store first)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

STORE = Path(__file__).parent / "store.json"


def _load():
    from loader import load, emit_all_records
    graph, items = load(STORE)
    records = emit_all_records(graph)
    return graph, records


def cmd_dump() -> None:
    graph, records = _load()

    print("=" * 70)
    print("EMITTED NODE RECORDS")
    print("=" * 70)
    for group in ("requirement_nodes", "implementation_nodes", "ts_nodes",
                  "outcome_nodes", "waiver_nodes"):
        print(f"\n── {group} ──")
        for rec in records[group]:
            print(json.dumps(rec, indent=2))

    print("\n" + "=" * 70)
    print("EMITTED EDGE RECORDS")
    print("=" * 70)
    for group in ("refines_edges", "implements_edges", "verifies_edges",
                  "confirms_edges", "witnesses_edges", "excuses_edges"):
        print(f"\n── {group} ──")
        for rec in records[group]:
            print(json.dumps(rec, indent=2))

    print("\n" + "=" * 70)
    print("NODE HASHES (store_id → nodeHash, merkleHash)")
    print("=" * 70)
    for node in sorted(graph.nodes.values(), key=lambda n: n.store_id):
        print(f"\n  {node.store_id} ({node.node_type})")
        for k, v in node.sub_hashes.items():
            print(f"    {k:12s}: {v}")
        if len(node.sub_hashes) > 1:
            print(f"    {'nodeHash':12s}: {node.node_hash}")
        print(f"    {'merkleHash':12s}: {node.merkle_hash}")


def cmd_consistency() -> None:
    from workflows import consistency
    graph, _ = _load()
    result = consistency(graph)
    print(json.dumps(result, indent=2))


def cmd_proof(scope: list[str]) -> None:
    from workflows import generate_proof
    graph, _ = _load()
    result = generate_proof(graph, scope)
    print(json.dumps(result, indent=2))


def cmd_suspect() -> None:
    from workflows import detect_suspect
    graph, _ = _load()
    result = detect_suspect(graph)
    print(json.dumps(result, indent=2))


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    match args[0]:
        case "dump":
            cmd_dump()
        case "consistency":
            cmd_consistency()
        case "proof":
            if len(args) < 2:
                print("Usage: python cli.py proof <req-id> [...]")
                sys.exit(1)
            cmd_proof(args[1:])
        case "suspect":
            cmd_suspect()
        case _:
            print(f"Unknown command: {args[0]!r}")
            print(__doc__)
            sys.exit(1)


if __name__ == "__main__":
    main()
