"""
seg_graph.py -- a minimal in-memory SEG graph and its lowering to the clingo
fact format used by seg_ruleset.PROG.

Node/edge/field identifiers are emitted as bare lowercase clingo atoms; field
VALUES are emitted as quoted strings (matching the demos of record, e.g.
node_field(toa, outcome, "PASS")). Descriptive fields (text, etc.) are carried
for the SPDX projection but only the fields the ruleset reads
({outcome, component_iri, expiry, approver}) affect the verdict.
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Node:
    id: str
    type: str                       # requirement|testspecification|implementation|
                                    # testoutcome|waiver|designreview|manifest|guarantee
    fields: Dict[str, str] = field(default_factory=dict)


@dataclass
class Edge:
    id: str
    type: str                       # refines|verifies|implements|confirms|witnesses|
                                    # excuses|reviews|covers|assumes|uses
    src: str
    dst: str


@dataclass
class Graph:
    namespace: str
    component_iri: str
    component_name: str
    component_version: str
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    # provenance facts for imported (referenced) nodes: node_id -> manifest_id
    referenced_under: Dict[str, str] = field(default_factory=dict)
    seal_ok: List[str] = field(default_factory=list)   # manifest ids whose seal verifies

    def node(self, nid):
        return next(n for n in self.nodes if n.id == nid)

    def to_facts(self) -> str:
        out = []
        for n in self.nodes:
            out.append(f"node({n.id}, {n.type}).")
            for k, v in n.fields.items():
                out.append(f'node_field({n.id}, {k}, "{v}").')
        for e in self.edges:
            out.append(f"edge({e.id}, {e.type}, {e.src}, {e.dst}).")
        for nid, man in self.referenced_under.items():
            out.append(f"referenced_under({nid}, {man}).")
        for man in self.seal_ok:
            out.append(f"seal_ok({man}).")
        return "\n".join(out) + "\n"
