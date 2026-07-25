"""affirmatrix — sealed, drift-tracking safety evidence graphs.

The engine's components are direct children of this package, one per row of
the component map (ADR-0004). There is deliberately no ``core`` namespace:
a level containing every component except the CLI distinguishes nothing, and
"the core" is not a requirement subject.

Shared internals (``_hashing``, ``identity``, ``diagnostics``) are not
components and never appear as requirement subjects.
"""

__version__ = "0.0.1.dev0"
