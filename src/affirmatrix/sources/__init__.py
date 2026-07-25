"""Record-source adapters — the AC-003 seam's implementations.

Container package, not a component: the components are the adapters inside it.
Each turns some outside thing into the record stream the engine consumes, and
each emits *content hashes*, never content (AC-005) — producers hash.

This is the only package that changes when iteration 0's hand-authored store is
replaced by real extraction, which is how AC-003's interchangeability claim is
demonstrated rather than asserted.

Nothing here may import ``affirmatrix.graph``: adapters sit below the graph.
"""
