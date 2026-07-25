"""Shared internal — the hash encoding of ADR-0005.

Not a component and never a requirement subject: this module is the single
implementation site for the framing (``LP``, ``SEQ``, ``U``), the three domain
tags, and the four hash functions (content, node, edge, design root). The
components that own the *requirements* for those hashes — the commitment layer
and the content extractor — call in here.

Two rules are enforced by ``tests/unit/test_import_layering.py``:

* this is the only module in the engine that imports ``hashlib``;
* nothing in the engine below the commitment layer depends on it.

SHA-256 is fixed, not injected (AC-013). Agility, if it is ever needed,
arrives as a new domain-tag version through a superseding ADR.

Iteration 0, backlog item B1.
"""
