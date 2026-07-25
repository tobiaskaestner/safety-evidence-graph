"""The commitment layer — hash derivation as metadata-agnostic primitives.

Owns node-hash derivation from a node's content hashes (SEG-SREQ-005), the
two-sided edge hash (SEG-SREQ-002), and the flat-sealed design root
(SEG-SREQ-003) — all as pure primitives with no I/O, no clock, and no
configuration (ADR-0003). The proof generator *calls* the root primitive and
supplies the snapshot metadata; the metadata is an opaque byte string this
layer length-prefixes and hashes without parsing.

There is no per-node ``merkleHash`` and no deep aggregation — that design is
retired (DEC-012/014). ``flat-openable`` is Phase C.

**This package is a leaf.** It imports ``_hashing`` and nothing else in the
engine, so ADR-0003's boundary is mechanically checkable rather than merely
conventional. Byte layout is ADR-0005.

Iteration 0, backlog items B2 (node hash), B3 (edge hash), B4 (design root).
"""
