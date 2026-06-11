import json
import pytest
from pathlib import Path
import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).parent.parent
SCHEMAS = ROOT / "schemas"
NODES = ROOT / "nodes"
EDGES = ROOT / "edges"


def load(path):
    with open(path) as f:
        return json.load(f)


def build_registry():
    resources = []
    for schema_file in SCHEMAS.glob("*.schema.json"):
        schema = load(schema_file)
        resource = Resource.from_contents(schema, default_specification=DRAFT202012)
        resources.append((schema["$id"], resource))
    return Registry().with_resources(resources)


REGISTRY = build_registry()  # rebuilt each test run; schemas are reloaded from disk


def validate_all(instance_path, schema_path):
    schema = load(schema_path)
    instances = load(instance_path)
    if not isinstance(instances, list):
        instances = [instances]
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema, registry=REGISTRY)
    errors = []
    for inst in instances:
        for e in validator.iter_errors(inst):
            errors.append(f"{inst.get('name', inst.get('id', '?'))}: {e.message}")
    return errors


def test_requirements():
    errors = validate_all(
        NODES / "requirements.jsonld",
        SCHEMAS / "requirement.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_implementations():
    errors = validate_all(
        NODES / "implementations.jsonld",
        SCHEMAS / "implementation.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_test_specifications():
    errors = validate_all(
        NODES / "test_specifications.jsonld",
        SCHEMAS / "test_specification.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_test_outcomes():
    errors = validate_all(
        NODES / "test_outcomes.jsonld",
        SCHEMAS / "test_outcome.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_waivers():
    errors = validate_all(
        NODES / "waivers.jsonld",
        SCHEMAS / "waiver.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_edge_refines():
    errors = validate_all(
        EDGES / "refines.jsonld",
        SCHEMAS / "edge-refines.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_edge_verifies():
    errors = validate_all(
        EDGES / "verifies.jsonld",
        SCHEMAS / "edge-verifies.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_edge_implements():
    errors = validate_all(
        EDGES / "implements.jsonld",
        SCHEMAS / "edge-implements.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_edge_confirms():
    errors = validate_all(
        EDGES / "confirms.jsonld",
        SCHEMAS / "edge-confirms.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_edge_witnesses():
    errors = validate_all(
        EDGES / "witnesses.jsonld",
        SCHEMAS / "edge-witnesses.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_edge_excuses():
    errors = validate_all(
        EDGES / "excuses.jsonld",
        SCHEMAS / "edge-excuses.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_review_events():
    errors = validate_all(
        ROOT / "events" / "review_events.jsonld",
        SCHEMAS / "review_event.schema.json",
    )
    assert not errors, "\n".join(errors)


SNAPSHOT = ROOT / "proofs" / "2024-03-15T120000Z"


def test_design_consistency_proof():
    errors = validate_all(
        SNAPSHOT / "design_consistency_proof.jsonld",
        SCHEMAS / "design_consistency_proof.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_execution_coverage_record():
    errors = validate_all(
        SNAPSHOT / "execution_coverage_record.jsonld",
        SCHEMAS / "execution_coverage_record.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_coverage_report():
    errors = validate_all(
        SNAPSHOT / "coverage_report.jsonld",
        SCHEMAS / "coverage_report.schema.json",
    )
    assert not errors, "\n".join(errors)


def test_evidence_manifest():
    errors = validate_all(
        SNAPSHOT / "evidence_manifest.jsonld",
        SCHEMAS / "evidence_manifest.schema.json",
    )
    assert not errors, "\n".join(errors)
