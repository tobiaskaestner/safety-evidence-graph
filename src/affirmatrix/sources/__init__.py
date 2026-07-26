"""Record-source adapters — the implementations behind the input seam.

Container package, not a component: the components are the adapters inside it.
Each turns some outside thing into the record stream the engine consumes, and
each emits *content hashes*, never content — producers hash.

This is the only package that changes when iteration 0's hand-authored store is
replaced by real extraction. That is what makes the adapters' interchangeability
a demonstrated property rather than an asserted one.

Nothing here may import ``affirmatrix.graph``: adapters sit below the graph.
"""
