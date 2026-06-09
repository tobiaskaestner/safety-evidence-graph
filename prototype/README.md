# SEG Phase A — Throwaway De-risking Prototype

**This is a throwaway prototype.** Its sole purpose is to exercise the three
core SEG workflows end-to-end and surface unknowns before the real tool is
built. Do not reuse, package, or make this production-clean.

## What lives here

| File | Role |
|---|---|
| `store.json` | Hand-written "would-be" store — the only input |
| `hashing.py` | Raw-byte hashing of `to_hash` fields; derive `nodeHash`/`merkleHash` |
| `loader.py` | `store.json` → hashes → schema-valid node/edge records |
| `graph_model.py` | In-memory node/edge/link-state representation |
| `satisfaction.py` | Leaf/non-leaf recursive coverage (DEC-001) |
| `suspect.py` | Suspect propagation over strong edges |
| `workflows.py` | `consistency()`, `generate_proof(scope)`, `detect_suspect()` |
| `cli.py` | Command-line entry point for the three workflows |
| `schemas/` | Copy of the real JSON schemas — used only for validating emitted records |

## How to run

```bash
# Check graph consistency
python cli.py consistency

# Generate a proof over a requirement scope
python cli.py proof REQ-001 REQ-002

# Detect suspect links after a mutation (human edits store.json first)
python cli.py suspect
```

All commands read `store.json` from the same directory as `cli.py`.

## Reference docs

- `.claude/plans/seg_decision_log.md` — DEC-001…DEC-004
- `.claude/plans/seg_python_realization.md`
- `.claude/plans/prototype_agent_brief.md` — action plan and scope
