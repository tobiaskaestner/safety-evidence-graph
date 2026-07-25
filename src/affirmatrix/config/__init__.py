"""The configuration loader — repo topology behind one seam (AC-015).

The repo set, names, roles, and the node-type-to-source mapping are read from
``affirmatrix.yaml``, never scattered as ``repoA``/``repoB`` literals through
the engine, the record sources, or the manifest writer. v1 ships the mono-repo
mapping (DEC-030) with the four-stream topology retained as a supported
configuration and conformance fixture.

No value loaded here reaches a hash preimage: the IRI base is a serialization
concern (ADR-0007) and integrity mechanics are not configurable (AC-013), so
AC-011's proof-binding obligation stays dormant in v1.

Iteration 0 (minimal).
"""
