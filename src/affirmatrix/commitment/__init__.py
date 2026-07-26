"""The commitment layer — hash derivation as metadata-agnostic primitives.

Owns node-hash derivation from a node's type and its named content hashes
(SEG-SREQ-005), the two-sided edge hash (SEG-SREQ-002), and the flat-sealed
design root (SEG-SREQ-003) — all as pure primitives with no I/O, no clock, and
no configuration (ADR-0003). The proof generator *calls* the root primitive and
supplies the snapshot metadata; the metadata is an opaque byte string this
layer length-prefixes and hashes without parsing.

There is no per-node aggregate hash and no recursive fold up the refines
graph: the root is flat and sealed, one canonical sort and one hash. A
selectively openable commitment — a Merkle tree over the same set — is a later
concern and is not built here.

**This package is a leaf.** It imports ``_hashing`` — the byte-level framing it
shares with the record sources — and nothing else in the engine, so ADR-0003's
boundary is mechanically checkable rather than merely conventional. Byte layout
is ADR-0005.

Iteration-0 backlog items B2 (node hash), B3 (edge hash), B4 (design root).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from affirmatrix._hashing import (
    checked_digest,
    counted_sequence,
    digest_of,
    length_prefixed,
    utf8,
)

#: The component's public surface. The framing helpers imported above are
#: ``_hashing``'s, not the commitment layer's, and are not re-exported.
__all__ = [
    "EDGE_TAG",
    "NODE_TAG",
    "ROOT_TAG",
    "design_root",
    "edge_hash",
    "edge_tuple",
    "node_hash",
]

#: Domain tags (ADR-0005 ii). The ``v1`` segment is the encoding version: a
#: change to the layout mints new tags rather than silently re-hashing the same
#: inputs.
NODE_TAG = "affirmatrix/v1/node"
EDGE_TAG = "affirmatrix/v1/edge"
ROOT_TAG = "affirmatrix/v1/root"


def node_hash(node_type: str, content_hashes: Mapping[str, bytes]) -> bytes:
    """Derive a node hash from the node's type and its named content hashes.

    :implements: SEG-SREQ-005

    Binds the local type token and the content-hash field names, not only the
    digests, so a Requirement and a Waiver covering byte-identical content
    differ. Pairs are ordered by field name, which makes the result
    reproducible from the record's own pairs without consulting the taxonomy
    provider's declaration order.

    The fold is uniform: a single-span node is a sequence of one, never its own
    content hash passed through — the substitution the prototype allowed, where
    a Requirement's content hash *was* its node hash.
    """
    if not content_hashes:
        raise ValueError(f"node type {node_type!r} needs at least one content hash")
    fields = [
        length_prefixed(utf8(name)) + length_prefixed(checked_digest(digest, name))
        for name, digest in sorted(content_hashes.items(), key=lambda pair: utf8(pair[0]))
    ]
    return digest_of(
        length_prefixed(utf8(NODE_TAG))
        + length_prefixed(utf8(node_type))
        + counted_sequence(fields)
    )


def edge_tuple(from_id: str, to_id: str, edge_type: str) -> bytes:
    """``⟨from, to, type⟩`` framed — an edge's contribution to a preimage.

    Identifiers are case-local stable identifiers and the type is a local token
    (ADR-0007); no IRI enters a preimage, which is what keeps the namespace
    base revisable.
    """
    return (
        length_prefixed(utf8(from_id))
        + length_prefixed(utf8(to_id))
        + length_prefixed(utf8(edge_type))
    )


def edge_hash(
    from_id: str,
    to_id: str,
    edge_type: str,
    from_node_hash: bytes,
    to_node_hash: bytes,
) -> bytes:
    """Compute a strong edge's hash from its endpoints, type, and node hashes.

    :implements: SEG-SREQ-002

    Two-sided by construction: either endpoint moving changes the hash, which
    is what lets recomputation detect that an affirmation no longer covers the
    content it was made against.
    """
    return digest_of(
        length_prefixed(utf8(EDGE_TAG))
        + edge_tuple(from_id, to_id, edge_type)
        + length_prefixed(checked_digest(from_node_hash, "from_node_hash"))
        + length_prefixed(checked_digest(to_node_hash, "to_node_hash"))
    )


def design_root(
    metadata: bytes,
    node_hashes: Iterable[bytes],
    edges: Iterable[tuple[str, str, str]],
) -> bytes:
    """Seal a design set under one flat root, with caller-supplied metadata.

    :implements: SEG-SREQ-003

    One canonical sort and one hash — no per-node aggregation and no
    traversal. ``metadata`` is opaque: the caller supplies it already
    canonical, and this function frames and hashes it without parsing, which is
    what keeps snapshot semantics out of the commitment layer (ADR-0003).

    Sorting never deduplicates. Two same-type nodes covering identical content
    share a node hash, and both must count, or a graph would seal identically
    to a smaller graph that merely resembles it.

    The primitive is total: an empty design set seals to a well-defined value.
    Refusing to seal an empty scope is a gate decision, not a hashing one.
    """
    sorted_nodes = sorted(checked_digest(digest, "node hash") for digest in node_hashes)
    sorted_edges = sorted(edge_tuple(*edge) for edge in edges)
    return digest_of(
        length_prefixed(utf8(ROOT_TAG))
        + length_prefixed(metadata)
        + counted_sequence(sorted_nodes)
        + counted_sequence(sorted_edges)
    )
