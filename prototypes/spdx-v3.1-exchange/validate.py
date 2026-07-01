"""
validate.py -- validate a safety BOM JSON-LD against the generated SPDX FuSa
SHACL shapes.

inference="none" is REQUIRED: pyshacl's targetClass selection is already
subclass-aware via the ontology graph (so Element-level constraints such as
creationInfo DO fire on Requirement / Assumption / Relationship instances --
verified by negative probe). Turning on rdfs/owlrl instead MATERIALIZES
`rdf:type Element` onto every instance, which trips SPDX's "Element is an
abstract class, do not instantiate directly" guard with false positives.
"""
import sys
from rdflib import Graph
from pyshacl import validate

SHAPES = "/tmp/spdx_rdf/spdx-model.ttl"


def run(bom_path):
    data = Graph().parse(bom_path, format="json-ld")
    shapes = Graph().parse(SHAPES, format="turtle")
    conforms, _, text = validate(
        data, shacl_graph=shapes, ont_graph=shapes,
        inference="none", advanced=True, abort_on_first=False,
    )
    print(f"data graph: {len(data)} triples")
    print("CONFORMS" if conforms else "VIOLATIONS")
    if not conforms:
        print(text)
    return conforms


if __name__ == "__main__":
    ok = run(sys.argv[1] if len(sys.argv) > 1 else "safety_bom.jsonld")
    sys.exit(0 if ok else 1)
