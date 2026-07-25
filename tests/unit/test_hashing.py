"""Conformance tests for the byte-level encoding (ADR-0005).

The framing and the bare content hash live below the commitment layer because
both sides of the record-source boundary need them: producers hash content, the
commitment layer folds. The derivations built on this encoding — node hash,
edge hash, design root — belong to the commitment layer and are tested in
``test_commitment``.

These hashes are irreversible in a way ordinary code is not: once a human has
affirmed an edge, changing how its preimage is laid out invalidates the
affirmation. So the binding checks are **re-derivations** transcribed from
ADR-0005's Decision section rather than imported from the module under test.
"""

from __future__ import annotations

import hashlib
import struct

import pytest

from affirmatrix import _hashing


def lp(payload: bytes) -> bytes:
    """``LP(b) = uint32be(len(b)) ‖ b``"""
    return struct.pack(">I", len(payload)) + payload


D1 = hashlib.sha256(b"one").digest()


# ── The content hash ────────────────────────────────────────────────────────


def test_content_hash_is_the_bare_sha256_of_the_form() -> None:
    """No tag, no framing — reproducible with ``sha256sum`` (ADR-0005 ii)."""
    form = b"def f():\n    return 1\n"
    assert _hashing.content_hash(form) == hashlib.sha256(form).digest()


def test_a_content_hash_is_exactly_thirty_two_bytes() -> None:
    assert len(_hashing.content_hash(b"anything")) == _hashing.DIGEST_BYTES


def test_the_content_hash_of_an_empty_form_is_defined() -> None:
    """An empty canonical form is still a form; refusing it is not this layer's."""
    assert _hashing.content_hash(b"") == hashlib.sha256(b"").digest()


# ── The framing ─────────────────────────────────────────────────────────────


def test_length_prefix_matches_the_notation() -> None:
    assert _hashing.length_prefixed(b"abc") == b"\x00\x00\x00\x03abc"
    assert _hashing.length_prefixed(b"") == b"\x00\x00\x00\x00"


def test_counted_sequence_matches_the_notation() -> None:
    assert _hashing.counted_sequence([]) == b"\x00\x00\x00\x00"
    assert _hashing.counted_sequence([b"a", b"bc"]) == (
        b"\x00\x00\x00\x02" b"\x00\x00\x00\x01a" b"\x00\x00\x00\x02bc"
    )


def test_framing_distinguishes_splits_that_concatenation_merges() -> None:
    """The property the whole encoding rests on (ADR-0005 i)."""
    left = _hashing.length_prefixed(b"a") + _hashing.length_prefixed(b"bc")
    right = _hashing.length_prefixed(b"ab") + _hashing.length_prefixed(b"c")
    assert left != right


def test_a_counted_sequence_distinguishes_arity_from_content() -> None:
    """One item of two bytes is not two items of one byte."""
    assert _hashing.counted_sequence([b"ab"]) != _hashing.counted_sequence([b"a", b"b"])


def test_counted_sequence_accepts_an_exhaustible_iterable() -> None:
    assert _hashing.counted_sequence(iter([b"a"])) == _hashing.counted_sequence([b"a"])


def test_utf8_encodes_without_normalizing() -> None:
    """ADR-0005: identifiers enter as recorded — normalization is a second edit."""
    # Written as escapes deliberately: as literal characters an editor may
    # normalize one into the other and the test would assert nothing.
    decomposed = "é"  # "e" + COMBINING ACUTE ACCENT
    composed = "é"  # LATIN SMALL LETTER E WITH ACUTE
    assert decomposed != composed
    assert _hashing.utf8(decomposed) != _hashing.utf8(composed)
    assert _hashing.utf8(decomposed) == b"e\xcc\x81"
    assert _hashing.utf8(composed) == b"\xc3\xa9"


# ── Digest discipline ───────────────────────────────────────────────────────


def test_a_raw_digest_passes_through_unchanged() -> None:
    assert _hashing.checked_digest(D1, "example") is D1


def test_a_hex_digest_is_rejected() -> None:
    """64 bytes that would frame and hash perfectly well, and be entirely wrong."""
    with pytest.raises(ValueError, match="32 raw bytes"):
        _hashing.checked_digest(D1.hex().encode("ascii"), "example")


def test_the_rejection_names_the_offending_input() -> None:
    """A wrong digest is unrecoverable once affirmed; the message must locate it."""
    with pytest.raises(ValueError, match="apiHash"):
        _hashing.checked_digest(b"short", "apiHash")


def test_digest_of_hashes_an_assembled_preimage() -> None:
    preimage = lp(b"tag") + lp(D1)
    assert _hashing.digest_of(preimage) == hashlib.sha256(preimage).digest()
