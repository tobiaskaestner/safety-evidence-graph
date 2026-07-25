0003. The commitment layer owns hash derivation as metadata-agnostic primitives
================================================================================

Status
------

Accepted, 2026-07-25.

Context
-------

The engine decomposition names a component for hash derivation only
descriptively ("the hashing/commitment layer"), and two binding sources
disagree on its boundary: the SWE brief assigns node hash, edge hash, and
the flat-sealed design root to it, while the design summary (§9, step 5)
computes the design root inside the proof generator, folding in snapshot
metadata there. The first requirement slice (SEG-SREQ-002/003/005) needed
a settled subject.

Decision
--------

The component is named **the commitment layer**. It owns node-hash
derivation (from a node's content hashes), the two-sided edge hash, and
the flat-sealed design-root computation (DEC-012/014) — all as
**metadata-agnostic primitives**. The proof generator *calls* the root
primitive and supplies the snapshot metadata at proof time. Approved
component vocabulary alongside it: the content extractor, the graph
builder, the requirements reader.

Consequences
------------

- SEG-SREQ-002, -003, and -005 use "the commitment layer" as subject;
  SEG-SREQ-003 treats the metadata term as a caller-supplied opaque
  input, deferring its semantics to the proof slice.
- The proof generator holds no hashing logic of its own.
- The engine's module decomposition must reflect this boundary (design
  round, iteration 0).
