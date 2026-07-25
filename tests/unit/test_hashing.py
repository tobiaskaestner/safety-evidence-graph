"""Conformance tests for the hash encoding (ADR-0005).

These hashes are irreversible in a way ordinary code is not: once a human has
affirmed an edge, changing how its preimage is laid out invalidates the
affirmation. So the binding checks here are **re-derivations**: each formula is
transcribed independently from ADR-0005's Decision section and compared against
the implementation. A property test can only show that the code is
self-consistent; a transcription shows that it says what the decision says.

The property tests that follow the re-derivations cover the specific failures
the ADR was written to prevent — the prototype's concatenation ambiguity and
its passthrough at n = 1 — plus the multiset and ordering guarantees the design
root rests on.
"""

from __future__ import annotations

import hashlib
import struct

import pytest

from affirmatrix import _hashing

# ── An independent transcription of ADR-0005 ────────────────────────────────
#
# Deliberately not imported from the module under test.

NODE_TAG = b"affirmatrix/v1/node"
EDGE_TAG = b"affirmatrix/v1/edge"
ROOT_TAG = b"affirmatrix/v1/root"


def lp(payload: bytes) -> bytes:
    """``LP(b) = uint32be(len(b)) ‖ b``"""
    return struct.pack(">I", len(payload)) + payload


def seq(items: list[bytes]) -> bytes:
    """``SEQ(x1..xn) = uint32be(n) ‖ LP(x1) ‖ … ‖ LP(xn)``"""
    return struct.pack(">I", len(items)) + b"".join(lp(item) for item in items)


def u(text: str) -> bytes:
    """``U(s)`` — UTF-8 bytes exactly as recorded."""
    return text.encode("utf-8")


# ── Fixtures: digests, not hashes of anything meaningful ────────────────────

D1 = hashlib.sha256(b"one").digest()
D2 = hashlib.sha256(b"two").digest()
D3 = hashlib.sha256(b"three").digest()


# ── Re-derivation: the four formulas ────────────────────────────────────────


def test_content_hash_is_the_bare_sha256_of_the_form() -> None:
    """No tag, no framing — reproducible with ``sha256sum`` (ADR-0005 ii)."""
    form = b"def f():\n    return 1\n"
    assert _hashing.content_hash(form) == hashlib.sha256(form).digest()


def test_node_hash_matches_the_transcribed_formula() -> None:
    fields = {"bodyHash": D2, "apiHash": D1}
    expected = hashlib.sha256(
        lp(NODE_TAG)
        + lp(u("Implementation"))
        + seq([lp(u("apiHash")) + lp(D1), lp(u("bodyHash")) + lp(D2)])
    ).digest()
    assert _hashing.node_hash("Implementation", fields) == expected


def test_edge_hash_matches_the_transcribed_formula() -> None:
    expected = hashlib.sha256(
        lp(EDGE_TAG)
        + lp(u("SEG-SREQ-001"))
        + lp(u("SEG-SYS-001"))
        + lp(u("Refines"))
        + lp(D1)
        + lp(D2)
    ).digest()
    actual = _hashing.edge_hash("SEG-SREQ-001", "SEG-SYS-001", "Refines", D1, D2)
    assert actual == expected


def test_design_root_matches_the_transcribed_formula() -> None:
    metadata = b'{"snapshotId":"2026-07-25T00:00:00Z-abc123"}'
    edges = [("SEG-SREQ-001", "SEG-SYS-001", "Refines")]
    expected = hashlib.sha256(
        lp(ROOT_TAG)
        + lp(metadata)
        + seq(sorted([D1, D2]))
        + seq([lp(u("SEG-SREQ-001")) + lp(u("SEG-SYS-001")) + lp(u("Refines"))])
    ).digest()
    assert _hashing.design_root(metadata, [D2, D1], edges) == expected


def test_edge_tuple_matches_the_transcribed_formula() -> None:
    expected = lp(u("a")) + lp(u("b")) + lp(u("Verifies"))
    assert _hashing.edge_tuple("a", "b", "Verifies") == expected


# ── The ambiguity the framing exists to kill ────────────────────────────────


def test_framing_separates_endpoints_that_concatenation_would_merge() -> None:
    """The prototype's bug: ``("a", "bc")`` and ``("ab", "c")`` hashed alike."""
    left = _hashing.edge_hash("a", "bc", "Refines", D1, D2)
    right = _hashing.edge_hash("ab", "c", "Refines", D1, D2)
    assert left != right


def test_framing_separates_an_edge_type_absorbed_into_an_endpoint() -> None:
    left = _hashing.edge_hash("a", "b", "Refines", D1, D2)
    right = _hashing.edge_hash("a", "bRefines", "", D1, D2)
    assert left != right


def test_framing_separates_field_names_from_their_digests() -> None:
    left = _hashing.node_hash("Requirement", {"ab": D1})
    right = _hashing.node_hash("Requirement", {"a": D1})
    assert left != right


# ── The passthrough that ADR-0005 closes ────────────────────────────────────


def test_a_single_span_node_hash_is_not_its_content_hash() -> None:
    """n = 1 folds like any other arity (ADR-0005 iii).

    The prototype returned the lone content hash unchanged, making a
    Requirement's content hash and node hash the same 32 bytes — and therefore
    substitutable wherever a node hash was expected.
    """
    assert _hashing.node_hash("Requirement", {"nodeHash": D1}) != D1


def test_a_single_span_node_hash_still_binds_its_type() -> None:
    requirement = _hashing.node_hash("Requirement", {"nodeHash": D1})
    waiver = _hashing.node_hash("Waiver", {"nodeHash": D1})
    assert requirement != waiver


def test_node_hash_binds_which_field_holds_which_digest() -> None:
    straight = _hashing.node_hash("TestSpecification", {"specHash": D1, "implHash": D2})
    swapped = _hashing.node_hash("TestSpecification", {"specHash": D2, "implHash": D1})
    assert straight != swapped


# ── Ordering: determined by the data, never by the caller ───────────────────


def test_node_field_order_does_not_reach_the_hash() -> None:
    """Pairs sort by field name, so a mapping's insertion order is irrelevant."""
    one = _hashing.node_hash("Implementation", {"apiHash": D1, "bodyHash": D2})
    other = _hashing.node_hash("Implementation", {"bodyHash": D2, "apiHash": D1})
    assert one == other


def test_the_root_is_independent_of_node_and_edge_input_order() -> None:
    edges = [("a", "b", "Refines"), ("c", "d", "Verifies"), ("e", "f", "Implements")]
    metadata = b"metadata"
    forward = _hashing.design_root(metadata, [D1, D2, D3], edges)
    reversed_inputs = _hashing.design_root(
        metadata, [D3, D2, D1], list(reversed(edges))
    )
    assert forward == reversed_inputs


def test_the_root_preserves_duplicate_node_hashes() -> None:
    """Two same-type nodes with identical content share a digest; both count.

    Sorting must never deduplicate, or a graph would seal identically to a
    smaller graph that merely resembles it (ADR-0005 v).
    """
    once = _hashing.design_root(b"", [D1], [])
    twice = _hashing.design_root(b"", [D1, D1], [])
    assert once != twice


def test_the_root_reflects_its_edge_set() -> None:
    metadata = b""
    without = _hashing.design_root(metadata, [D1], [])
    with_edge = _hashing.design_root(metadata, [D1], [("a", "b", "Refines")])
    rewired = _hashing.design_root(metadata, [D1], [("a", "b", "Verifies")])
    assert without != with_edge != rewired
    assert with_edge != rewired


def test_the_root_reflects_its_metadata() -> None:
    assert _hashing.design_root(b"a", [D1], []) != _hashing.design_root(b"b", [D1], [])


# ── Domain separation ───────────────────────────────────────────────────────


def test_the_three_domain_tags_are_distinct() -> None:
    tags = {_hashing.NODE_TAG, _hashing.EDGE_TAG, _hashing.ROOT_TAG}
    assert len(tags) == 3


def test_each_preimage_leads_with_its_own_length_prefixed_tag() -> None:
    """Tag divergence, checked at the preimage rather than inferred from digests.

    A body-level collision between a node and an edge preimage is constructible
    in principle — the shapes are close — so asserting two digests differ would
    prove little. The re-derivation tests above pin each preimage exactly; this
    one states the property they encode.
    """
    node_preimage = (
        lp(NODE_TAG) + lp(u("Requirement")) + seq([lp(u("nodeHash")) + lp(D1)])
    )
    edge_preimage = lp(EDGE_TAG) + lp(u("a")) + lp(u("b")) + lp(u("Refines")) + lp(D1) + lp(D2)
    root_preimage = lp(ROOT_TAG) + lp(b"") + seq([D1]) + seq([])

    assert _hashing.node_hash("Requirement", {"nodeHash": D1}) == hashlib.sha256(
        node_preimage
    ).digest()
    assert _hashing.edge_hash("a", "b", "Refines", D1, D2) == hashlib.sha256(
        edge_preimage
    ).digest()
    assert _hashing.design_root(b"", [D1], []) == hashlib.sha256(root_preimage).digest()

    assert node_preimage[:4] == edge_preimage[:4] == root_preimage[:4]
    assert len({node_preimage[4:23], edge_preimage[4:23], root_preimage[4:23]}) == 3


# ── Raw bytes, not hex ──────────────────────────────────────────────────────


def test_digests_enter_as_raw_bytes_and_hex_is_rejected() -> None:
    """A hex digest is 64 bytes; accepting one would silently seal the wrong value."""
    with pytest.raises(ValueError, match="32"):
        _hashing.node_hash("Requirement", {"nodeHash": D1.hex().encode("ascii")})
    with pytest.raises(ValueError, match="32"):
        _hashing.edge_hash("a", "b", "Refines", D1, D2.hex().encode("ascii"))
    with pytest.raises(ValueError, match="32"):
        _hashing.design_root(b"", [D1.hex().encode("ascii")], [])


def test_a_content_hash_is_exactly_thirty_two_bytes() -> None:
    assert len(_hashing.content_hash(b"anything")) == 32


def test_a_node_without_content_hashes_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least one"):
        _hashing.node_hash("Requirement", {})


# ── Determinism ─────────────────────────────────────────────────────────────


def test_the_same_inputs_always_produce_the_same_hashes() -> None:
    """AC-007: same inputs, same hashes, across runs and environments."""
    fields = {"apiHash": D1, "bodyHash": D2}
    edges = [("a", "b", "Refines")]
    assert _hashing.node_hash("Implementation", fields) == _hashing.node_hash(
        "Implementation", fields
    )
    assert _hashing.edge_hash("a", "b", "Refines", D1, D2) == _hashing.edge_hash(
        "a", "b", "Refines", D1, D2
    )
    assert _hashing.design_root(b"m", [D1], edges) == _hashing.design_root(b"m", [D1], edges)


def test_the_root_accepts_exhaustible_iterables() -> None:
    """Callers stream the design set; consuming it twice must not be required."""
    root = _hashing.design_root(b"m", iter([D2, D1]), iter([("a", "b", "Refines")]))
    assert root == _hashing.design_root(b"m", [D1, D2], [("a", "b", "Refines")])


# ── Framing primitives ──────────────────────────────────────────────────────


def test_length_prefix_and_counted_sequence_match_the_notation() -> None:
    assert _hashing.length_prefixed(b"abc") == b"\x00\x00\x00\x03abc"
    assert _hashing.counted_sequence([]) == b"\x00\x00\x00\x00"
    assert _hashing.counted_sequence([b"a", b"bc"]) == (
        b"\x00\x00\x00\x02" b"\x00\x00\x00\x01a" b"\x00\x00\x00\x02bc"
    )


def test_utf8_encodes_without_normalizing() -> None:
    """ADR-0005: identifiers enter as recorded — normalization is a second edit."""
    decomposed = "é"
    composed = "é"
    assert _hashing.utf8(decomposed) != _hashing.utf8(composed)
    assert _hashing.utf8(decomposed) == decomposed.encode("utf-8")
