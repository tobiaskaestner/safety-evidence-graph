"""Structural unit checks for the prototype loader and hashing layer.

These are mechanical checks only (DEC-001 / brief §Build scope):
  - emitted records validate against schema/
  - hashing is deterministic

Workflow correctness is NOT asserted here; that is judged by the human at each
⏸ PAUSE checkpoint.

Known schema limitation:
  - Implementation seg:sourcePath: schema expects .h/.c (C-centric); dummy
    paths satisfy the regex but do not correspond to real Python source files
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure the prototype directory is importable regardless of working directory.
sys.path.insert(0, str(Path(__file__).parent))

from loader import load, emit_all_records  # noqa: E402

STORE = Path(__file__).parent / "store-small.json"
SCHEMA_DIR = Path(__file__).parent / "schemas"


# ── Schema validation helpers ─────────────────────────────────────────────────

def _build_registry():
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012

    registry = Registry()
    for p in SCHEMA_DIR.glob("*.json"):
        content = json.loads(p.read_text())
        if "$id" in content:
            registry = registry.with_resource(
                content["$id"],
                Resource.from_contents(content, default_specification=DRAFT202012),
            )
    return registry


_REGISTRY = _build_registry()


def schema_errors(record: dict, schema_filename: str) -> list[str]:
    from jsonschema import Draft202012Validator

    schema_id = f"https://zephyrproject.org/seg/schema/{schema_filename}"
    schema = next(
        json.loads(p.read_text())
        for p in SCHEMA_DIR.glob("*.json")
        if json.loads(p.read_text()).get("$id") == schema_id
    )
    validator = Draft202012Validator(schema, registry=_REGISTRY)
    return sorted({e.message for e in validator.iter_errors(record)})


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def graph():
    g, _ = load(STORE)
    return g


@pytest.fixture(scope="module")
def records(graph):
    return emit_all_records(graph)


# ── Determinism ───────────────────────────────────────────────────────────────

class TestHashingDeterminism:
    def test_node_hashes_are_stable(self):
        g1, _ = load(STORE)
        g2, _ = load(STORE)
        for iri in g1.nodes:
            assert g1.nodes[iri].node_hash == g2.nodes[iri].node_hash, iri

    def test_merkle_hashes_are_stable(self):
        g1, _ = load(STORE)
        g2, _ = load(STORE)
        for iri in g1.nodes:
            assert g1.nodes[iri].merkle_hash == g2.nodes[iri].merkle_hash, iri

    def test_strong_edge_hashes_are_stable(self):
        g1, _ = load(STORE)
        g2, _ = load(STORE)
        h1 = sorted(e.edge_hash for e in g1.edges if e.edge_hash)
        h2 = sorted(e.edge_hash for e in g2.edges if e.edge_hash)
        assert h1 == h2

    def test_edge_iris_are_unique(self, graph):
        iris = [e.iri for e in graph.edges]
        assert len(iris) == len(set(iris)), "Duplicate edge IRIs detected"


# ── Schema validation: records that SHOULD validate ──────────────────────────

class TestSchemaValidation:
    def test_requirement_nodes(self, records):
        for rec in records["requirement_nodes"]:
            errs = schema_errors(rec, "requirement.schema.json")
            assert errs == [], f"{rec['name']}: {errs}"

    def test_refines_edges(self, records):
        for rec in records["refines_edges"]:
            errs = schema_errors(rec, "edge-refines.schema.json")
            assert errs == [], f"{rec['id']}: {errs}"

    def test_implementation_nodes(self, records):
        for rec in records["implementation_nodes"]:
            errs = schema_errors(rec, "implementation.schema.json")
            assert errs == [], f"{rec['name']}: {errs}"

    def test_test_specification_nodes(self, records):
        for rec in records["ts_nodes"]:
            errs = schema_errors(rec, "test_specification.schema.json")
            assert errs == [], f"{rec['name']}: {errs}"

    def test_test_outcome_nodes(self, records):
        for rec in records["outcome_nodes"]:
            errs = schema_errors(rec, "test_outcome.schema.json")
            assert errs == [], f"{rec['name']}: {errs}"

    def test_waiver_nodes(self, records):
        for rec in records["waiver_nodes"]:
            errs = schema_errors(rec, "waiver.schema.json")
            assert errs == [], f"{rec['name']}: {errs}"

    def test_implements_edges(self, records):
        for rec in records["implements_edges"]:
            errs = schema_errors(rec, "edge-implements.schema.json")
            assert errs == [], f"{rec['id']}: {errs}"

    def test_verifies_edges(self, records):
        for rec in records["verifies_edges"]:
            errs = schema_errors(rec, "edge-verifies.schema.json")
            assert errs == [], f"{rec['id']}: {errs}"

    def test_confirms_edges(self, records):
        for rec in records["confirms_edges"]:
            errs = schema_errors(rec, "edge-confirms.schema.json")
            assert errs == [], f"{rec['id']}: {errs}"

    def test_witnesses_edges(self, records):
        for rec in records["witnesses_edges"]:
            errs = schema_errors(rec, "edge-witnesses.schema.json")
            assert errs == [], f"{rec['id']}: {errs}"

    def test_excuses_edges(self, records):
        for rec in records["excuses_edges"]:
            errs = schema_errors(rec, "edge-excuses.schema.json")
            assert errs == [], f"{rec['id']}: {errs}"

