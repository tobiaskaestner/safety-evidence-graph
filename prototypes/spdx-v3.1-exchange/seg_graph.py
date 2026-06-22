"""
seg_graph.py -- a minimal in-memory SEG graph and its lowering to the clingo
fact format used by seg_ruleset.PROG.

Node/edge/field identifiers are emitted as bare lowercase clingo atoms; field
VALUES are emitted as quoted strings (matching the demos of record, e.g.
node_field(toa, outcome, "PASS")). Descriptive fields (text, etc.) are carried
for the SPDX projection but only the fields the ruleset reads
({outcome, component_iri, expiry, approver}) affect the verdict.
"""
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List


def impl_sha1(body: str) -> str:
    """DEC-028 stand-in content-ref for an implementation: sha1 over its body
    label. Real content-addressing (a git blob/commit sha) replaces this later;
    the field is the source of truth the BOM projects (never invented at export)."""
    return hashlib.sha1(body.encode("utf-8")).hexdigest()


@dataclass
class Node:
    id: str
    type: str                       # requirement|testspecification|implementation|
                                    # testoutcome|waiver|designreview|manifest|guarantee|
                                    # assumption
                                    # implementation nodes carry a `sha1` content-ref (DEC-028)
    fields: Dict[str, str] = field(default_factory=dict)


@dataclass
class Edge:
    id: str
    type: str                       # refines|verifies|implements|confirms|witnesses|
                                    # excuses|reviews|covers|assumes|uses|conformsTo
    src: str
    dst: str
    kind: str = ""                  # provenance hint for rendering (e.g. covers:
                                    # "affirmed" = hand-authored reliance / "minted" =
                                    # derived from a resolved conformsTo). Not lowered.


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
