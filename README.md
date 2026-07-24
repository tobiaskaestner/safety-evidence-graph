# affirmatrix

*She who affirms.* affirmatrix binds requirements, code, tests, and results
into a **safety evidence graph**: content-anchored nodes (hashes over raw
source byte spans), human **affirmations** recorded against exact content
states, **drift detection** with derived suspicion, user-authored
**verdicts** (stratified Datalog), and a **sealed, recomputable commitment**
over the whole case — composable across a supply chain via SPDX Safety BOMs.
The roll-up verdict never travels: every consumer recomputes it.

**Status: pre-alpha scaffold, API not stable.**

## Install

```sh
pip install -e . --group dev
```

## Development

```sh
pytest
ruff check .
python -m doc build      # build the documentation federation
```

The documentation is a *federation* of Sphinx documents (manual,
requirement-specification, test-specification, test-report) declared once in
`doc/documents.yaml`; the repo dogfoods its own tool — the specification
documents are the first safety evidence graph affirmatrix seals.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
