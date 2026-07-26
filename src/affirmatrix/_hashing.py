"""Shared internal — the byte-level encoding of ADR-0005.

Not a component and never a requirement subject: this module is the single
implementation site for the framing (``LP``, ``SEQ``, ``U``) and for the bare
content hash. The *derivations* built on top of it — node hash, edge hash,
design root — belong to the commitment layer, which is the component the
requirements name (ADR-0003, ADR-0004).

The split follows use, not taste. The framing and the content hash are needed
on both sides of the record-source boundary: producers hash content
(``sources.*`` may import this module), while the derivations sit above them
and are reached only through the commitment layer.

Two rules are enforced by ``tests/unit/test_import_layering.py``:

* this is the only module in the engine that imports ``hashlib``;
* only the commitment layer and the record sources depend on it.

SHA-256 is fixed, not injected: the algorithm is not a configuration point.
Agility, if it is ever needed, arrives as a new domain-tag version through a
superseding decision record.

Every function here is pure: no I/O, no clock, no configuration. Digests are
raw 32-byte values throughout; hex is a serialization form and belongs to
``records`` (ADR-0005 iv).

Iteration-0 backlog item B1.
"""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Iterable

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
    """The bare SHA-256 of a node kind's canonical content form.

    Deliberately untagged and unframed, so an auditor can reproduce it with
    ``sha256sum`` over the extracted form and no knowledge of this module.
    Safety is not lost: every consumer frames it under a domain tag before
    hashing again.
    """
    return hashlib.sha256(canonical_form).digest()


def digest_of(preimage: bytes) -> bytes:
    """SHA-256 of an already-assembled preimage."""
    return hashlib.sha256(preimage).digest()


def checked_digest(digest: bytes, label: str) -> bytes:
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
