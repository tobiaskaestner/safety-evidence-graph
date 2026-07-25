"""The taxonomy provider — the built-in safety-evidence graph type (AC-001).

Single internal source for the node and edge types, the strong flag, the
content-hash field selection per node type, and the local-vs-serialized token
spelling (``Requirement`` / ``seg:Requirement``, ADR-0007). Nothing else in the
engine hardwires a type name.

v1 populates this from constants, framed as "the built-in safety-evidence graph
type"; the graph-type meta-model (DEC-007) is out of v1 and plugs in here.

Because ADR-0005 hashes both the node type and the content-hash field names,
the spellings this provider declares are integrity-relevant: renaming one is an
affirmation event, not a refactor.

Iteration 0, backlog item B6.
"""
