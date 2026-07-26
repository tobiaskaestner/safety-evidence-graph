"""Shared internal — identifier minting (ADR-0007).

Not a component and never a requirement subject. This module is the only place
that knows the identifier base, and it mints the absolute IRIs that serialized
records carry. Minted IRIs are **opaque keys**: tooling reads an edge's
endpoints from the record's endpoint fields and never parses them back out of
an identifier, because the parts can themselves contain the separator and the
split is not reliably reversible.

What enters a hash preimage is the *case-local* stable identifier, never an
IRI — which is why the base stays revisable and why this module is invisible
to the commitment layer.
"""
