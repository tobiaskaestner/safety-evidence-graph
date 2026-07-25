"""Shared internal — the hash encoding of ADR-0005.

Not a component and never a requirement subject: this module is the single
implementation site for the framing (``LP``, ``SEQ``, ``U``), the three domain
tags, and the four hash functions (content, node, edge, design root). The
components that own the *requirements* for those hashes — the commitment layer
and the content extractor — call in here and carry the ``:implements:``
markers; nothing here is marked, because a marker asserts that a *component*
realizes a requirement and this module is not one.

Two rules are enforced by ``tests/unit/test_import_layering.py``:

* this is the only module in the engine that imports ``hashlib``;
* nothing in the engine below the commitment layer depends on it.

SHA-256 is fixed, not injected (AC-013). Agility, if it is ever needed,
arrives as a new domain-tag version through a superseding ADR.

Every function here is pure: no I/O, no clock, no configuration. Digests are
raw 32-byte values throughout; hex is a serialization form and belongs to
``records`` (ADR-0005 iv).

Iteration 0, backlog item B1.
"""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Iterable, Mapping

#: Domain tags. The ``v1`` segment is the encoding version: a change to the
#: layout mints new tags rather than silently re-hashing the same inputs.
NODE_TAG = "affirmatrix/v1/node"
EDGE_TAG = "affirmatrix/v1/edge"
ROOT_TAG = "affirmatrix/v1/root"

DIGEST_BYTES = 32

#: The 32-bit framing width is arbitrary but fixed (ADR-0005 i).
_MAX_FRAMED = 2**32 - 1


def utf8(text: str) -> bytes:
    """``U(s)`` — UTF-8 bytes of ``text`` exactly as recorded.

    Never normalized: normalizing an identifier would be a second
    transformation of the thing being identified, the same reason the parser
    stays a locator and never feeds a hash.
    """
    return text.encode("utf-8")


def length_prefixed(payload: bytes) -> bytes:
    """``LP(b)`` — a 32-bit big-endian length, then the bytes themselves.

    Framing rather than delimiting is what makes a preimage unambiguous: the
    endpoint pair ``("a", "bc")`` and the pair ``("ab", "c")`` share a
    concatenation but not a framing.
    """
    if len(payload) > _MAX_FRAMED:
        raise ValueError(
            f"field of {len(payload)} bytes exceeds the 32-bit framing width of ADR-0005"
        )
    return struct.pack(">I", len(payload)) + payload


def counted_sequence(items: Iterable[bytes]) -> bytes:
    """``SEQ(x1..xn)`` — a 32-bit big-endian count, then each item framed.

    The count is what makes a *variable-arity* preimage unambiguous, as the
    length prefix does for a variable-length one.
    """
    framed = [length_prefixed(item) for item in items]
    if len(framed) > _MAX_FRAMED:
        raise ValueError(f"sequence of {len(framed)} items exceeds the 32-bit count width")
    return struct.pack(">I", len(framed)) + b"".join(framed)


def content_hash(canonical_form: bytes) -> bytes:
    """The bare SHA-256 of a node type's canonical content form (DEC-031).

    Deliberately untagged and unframed, so an auditor can reproduce it with
    ``sha256sum`` over the extracted form and no knowledge of this module.
    Safety is not lost: every consumer frames it under a domain tag before
    hashing again.
    """
    return hashlib.sha256(canonical_form).digest()


def node_hash(node_type: str, content_hashes: Mapping[str, bytes]) -> bytes:
    """Fold a node's content hashes into its node hash.

    Binds the local type token and the content-hash field names, not only the
    digests, so a Requirement and a Waiver covering byte-identical content
    differ. Pairs are ordered by field name, which makes the result
    reproducible from the record's own pairs without consulting the taxonomy
    provider's declaration order.

    The fold is uniform: a single-span node is a sequence of one, never its own
    content hash passed through.
    """
    if not content_hashes:
        raise ValueError(f"node type {node_type!r} needs at least one content hash")
    fields = [
        length_prefixed(utf8(name)) + length_prefixed(_raw_digest(digest, name))
        for name, digest in sorted(content_hashes.items(), key=lambda pair: utf8(pair[0]))
    ]
    return hashlib.sha256(
        length_prefixed(utf8(NODE_TAG))
        + length_prefixed(utf8(node_type))
        + counted_sequence(fields)
    ).digest()


def edge_tuple(from_id: str, to_id: str, edge_type: str) -> bytes:
    """``⟨from, to, type⟩`` framed — an edge's contribution to the design root.

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
    """Bind an edge to the content of both its endpoints.

    Two-sided by construction: either endpoint moving changes the hash, which
    is what lets recomputation detect that an affirmation no longer covers what
    it was made against.
    """
    return hashlib.sha256(
        length_prefixed(utf8(EDGE_TAG))
        + edge_tuple(from_id, to_id, edge_type)
        + length_prefixed(_raw_digest(from_node_hash, "from_node_hash"))
        + length_prefixed(_raw_digest(to_node_hash, "to_node_hash"))
    ).digest()


def design_root(
    metadata: bytes,
    node_hashes: Iterable[bytes],
    edges: Iterable[tuple[str, str, str]],
) -> bytes:
    """Seal a design set under one flat root.

    One canonical sort and one hash — no per-node aggregation and no traversal
    (DEC-012/014). ``metadata`` is opaque: the caller supplies it already
    canonical, and this function frames and hashes it without parsing.

    Sorting never deduplicates. Two same-type nodes covering identical content
    share a node hash, and both must count, or a graph would seal identically
    to a smaller graph that merely resembles it.
    """
    sorted_nodes = sorted(_raw_digest(digest, "node hash") for digest in node_hashes)
    sorted_edges = sorted(edge_tuple(*edge) for edge in edges)
    return hashlib.sha256(
        length_prefixed(utf8(ROOT_TAG))
        + length_prefixed(metadata)
        + counted_sequence(sorted_nodes)
        + counted_sequence(sorted_edges)
    ).digest()


def _raw_digest(digest: bytes, label: str) -> bytes:
    """Reject anything that is not a raw 32-byte digest.

    The realistic mistake is a hex string: 64 bytes that frame and hash
    perfectly well, producing a stable and entirely wrong commitment. Caught
    here it is a crash; uncaught it is an affirmed lie.
    """
    if len(digest) != DIGEST_BYTES:
        raise ValueError(
            f"{label}: expected {DIGEST_BYTES} raw bytes, got {len(digest)} — "
            "digests enter preimages as raw bytes, hex is a serialization form"
        )
    return digest
