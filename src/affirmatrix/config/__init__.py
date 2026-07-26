"""The configuration loader — source topology behind one seam.

The set of source repositories, their names and roles, and the mapping from
node kind to source are read from ``affirmatrix.yaml``, never scattered as
literals through the engine, the record sources, or the manifest writer. This
version ships the single-repository mapping (ADR-0002), with the multi-stream
layout retained as a supported configuration and exercised as a fixture.

No value loaded here reaches a hash preimage. The identifier base is a
serialization concern (ADR-0007) and the integrity mechanics are not
configurable, so configuration never has to be hashed into a package to make
one reproducible — which is exactly the obligation that would otherwise follow
from letting settings influence hashes.

Iteration 0 (minimal).
"""
