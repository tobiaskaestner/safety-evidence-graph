"""Shared internal — identifier minting (ADR-0007).

Not a component and never a requirement subject. This module is the only place
that knows the IRI base, and it mints the absolute IRIs that instance documents
serialize (design summary §8.4). Minted IRIs are opaque keys: tooling reads an
edge's endpoints from ``seg:from``/``seg:to`` and never parses an ``id`` back
into parts (§4.7).

What enters a hash preimage is the *case-local* stable identifier, never an
IRI — which is why the base stays revisable and why this module is invisible
to the commitment layer.
"""
