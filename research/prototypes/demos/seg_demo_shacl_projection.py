import json
from rdflib import Graph, Namespace, RDF, Literal
from pyshacl import validate

# ============================================================
# 1. THE SEG CORE FRAGMENT — the single source of truth.
#    Note: holds only IDENTITIES, TYPES, HASHES, STATES.
#    No content. `state` was COMPUTED by the integrity core
#    (drift check); here it is an input we faithfully carry.
# ============================================================
core = {
  "nodes": [
    {"id": "R1",  "type": "Requirement",       "nodeHash": "h_R1"},
    {"id": "R2",  "type": "Requirement",       "nodeHash": "h_R2"},
    {"id": "TS1", "type": "TestSpecification", "nodeHash": "h_TS1"},
  ],
  "edges": [
    {"id": "e1", "type": "refines",  "from": "R1",  "to": "R2", "edgeHash": "h_e1", "state": "active"},
    {"id": "e2", "type": "verifies", "from": "TS1", "to": "R1", "edgeHash": "h_e2", "state": "active"},
  ],
}

SEG = Namespace("https://zephyrproject.org/seg#")
EDGE_CLASS = {"refines": "Refines", "verifies": "Verifies",
              "implements": "Implements", "calls": "Calls"}

# ============================================================
# 2. THE PROJECTION — a pure, deterministic function core -> RDF.
#    Edges carry payload (edgeHash, state), so each edge is
#    REIFIED: promoted to its own RDF node with from/to pointers.
#    This function is WRITE-ONLY output. Never edited, never read back.
# ============================================================
def project(core) -> Graph:
    g = Graph(); g.bind("seg", SEG)
    for n in core["nodes"]:
        s = SEG[n["id"]]
        g.add((s, RDF.type, SEG[n["type"]]))
        g.add((s, SEG.nodeHash, Literal(n["nodeHash"])))
    for e in core["edges"]:
        s = SEG[e["id"]]
        g.add((s, RDF.type, SEG[EDGE_CLASS[e["type"]]]))   # edge-as-node (reification)
        g.add((s, SEG["from"], SEG[e["from"]]))
        g.add((s, SEG["to"],   SEG[e["to"]]))
        g.add((s, SEG.edgeHash, Literal(e["edgeHash"])))
        g.add((s, SEG.state,    Literal(e["state"])))
    return g

# ============================================================
# 3. THE SHACL SHAPES — structural well-formedness only.
#    (These could THEMSELVES be projected from the graph-type
#     definition; hand-written here to show the target.)
#    SHACL checks: endpoint typing, presence of hash, state is a
#    valid enum. It does NOT check whether the state is *correct*
#    — that truth is the core's job, carried in as data.
# ============================================================
shapes_ttl = """
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix seg: <https://zephyrproject.org/seg#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

seg:RefinesShape a sh:NodeShape ;
    sh:targetClass seg:Refines ;
    sh:property [ sh:path seg:from ; sh:class seg:Requirement ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:path seg:to   ; sh:class seg:Requirement ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:path seg:edgeHash ; sh:datatype xsd:string ; sh:minCount 1 ] ;
    sh:property [ sh:path seg:state ; sh:in ( "active" "pending" "suspect" "broken" ) ; sh:minCount 1 ] .

seg:VerifiesShape a sh:NodeShape ;
    sh:targetClass seg:Verifies ;
    sh:property [ sh:path seg:from ; sh:class seg:TestSpecification ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:path seg:to   ; sh:class seg:Requirement ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:path seg:edgeHash ; sh:datatype xsd:string ; sh:minCount 1 ] ;
    sh:property [ sh:path seg:state ; sh:in ( "active" "pending" "suspect" "broken" ) ; sh:minCount 1 ] .
"""

def check(label, core):
    data = project(core)
    conforms, _, text = validate(data, shacl_graph=shapes_ttl,
                                 shacl_graph_format="turtle", inference="none")
    print(f"=== {label} ===")
    print("conforms:", conforms)
    if not conforms:
        # print just the violation focus + message lines
        for line in text.splitlines():
            if any(k in line for k in ("Focus Node", "Value Node", "Message", "Source Shape")):
                print("   ", line.strip())
    print()

# Good case
check("well-formed projection", core)

# Malformed case: make the verifies edge originate from a Requirement (R2),
# not a TestSpecification. The CORE structure is wrong; SHACL must catch it
# on the projection — exactly the job our hand-rolled checker did in batch 1.
import copy
bad = copy.deepcopy(core)
bad["edges"][1]["from"] = "R2"   # verifies now from a Requirement
check("malformed (verifies from a Requirement)", bad)
