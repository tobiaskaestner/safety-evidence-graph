"""Conformance tests for the commitment layer (SEG-SREQ-002, -003, -005).

The layer owns three derivations and no I/O: a node hash from a node's type and
its named content hashes, a two-sided edge hash, and one flat-sealed design
root over a design set plus caller-supplied metadata. Their byte layout is
ADR-0005.

As in ``test_hashing``, the binding checks are **re-derivations**: each formula
is transcribed independently from ADR-0005's Decision section rather than
imported from the code under test, so drift between the decision and the
implementation shows up as a failure rather than as agreement between a
function and itself.
"""

from __future__ import annotations

import hashlib
import struct

import pytest

from affirmatrix import commitment

# ── An independent transcription of ADR-0005 ────────────────────────────────

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


D1 = hashlib.sha256(b"one").digest()
D2 = hashlib.sha256(b"two").digest()
D3 = hashlib.sha256(b"three").digest()


# ── SEG-SREQ-005 — the node hash ────────────────────────────────────────────


def test_node_hash_matches_the_transcribed_formula() -> None:
    fields = {"bodyHash": D2, "apiHash": D1}
    expected = hashlib.sha256(
        lp(NODE_TAG)
        + lp(u("Implementation"))
        + seq([lp(u("apiHash")) + lp(D1), lp(u("bodyHash")) + lp(D2)])
    ).digest()
    assert commitment.node_hash("Implementation", fields) == expected


def test_a_single_span_node_hash_is_not_its_content_hash() -> None:
    """n = 1 folds like any other arity (ADR-0005 iii).

    The prototype returned the lone content hash unchanged, making a
    Requirement's content hash and node hash the same 32 bytes — and therefore
    substitutable wherever a node hash was expected.
    """
    assert commitment.node_hash("Requirement", {"nodeHash": D1}) != D1


def test_the_node_hash_derives_from_the_node_type() -> None:
    """SEG-SREQ-005 names the type as an input, so identical content diverges."""
    requirement = commitment.node_hash("Requirement", {"nodeHash": D1})
    waiver = commitment.node_hash("Waiver", {"nodeHash": D1})
    assert requirement != waiver


def test_the_node_hash_pairs_each_content_hash_with_its_name() -> None:
    """Swapping which name holds which digest is a different node."""
    straight = commitment.node_hash("TestSpecification", {"specHash": D1, "implHash": D2})
    swapped = commitment.node_hash("TestSpecification", {"specHash": D2, "implHash": D1})
    assert straight != swapped


def test_the_name_is_bound_distinctly_from_the_digest() -> None:
    """Framing keeps a longer name from absorbing the bytes that follow it."""
    assert commitment.node_hash("Requirement", {"ab": D1}) != commitment.node_hash(
        "Requirement", {"a": D1}
    )


def test_node_field_order_does_not_reach_the_hash() -> None:
    """Pairs sort by field name, so a mapping's insertion order is irrelevant."""
    one = commitment.node_hash("Implementation", {"apiHash": D1, "bodyHash": D2})
    other = commitment.node_hash("Implementation", {"bodyHash": D2, "apiHash": D1})
    assert one == other


def test_a_node_without_content_hashes_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least one"):
        commitment.node_hash("Requirement", {})


# ── SEG-SREQ-002 — the edge hash ────────────────────────────────────────────


def test_edge_hash_matches_the_transcribed_formula() -> None:
    expected = hashlib.sha256(
        lp(EDGE_TAG)
        + lp(u("SEG-SREQ-001"))
        + lp(u("SEG-SYS-001"))
        + lp(u("Refines"))
        + lp(D1)
        + lp(D2)
    ).digest()
    assert commitment.edge_hash("SEG-SREQ-001", "SEG-SYS-001", "Refines", D1, D2) == expected


def test_the_edge_hash_binds_both_endpoint_node_hashes() -> None:
    """Two-sided: either endpoint moving changes the hash (SEG-SREQ-002)."""
    baseline = commitment.edge_hash("a", "b", "Refines", D1, D2)
    from_moved = commitment.edge_hash("a", "b", "Refines", D3, D2)
    to_moved = commitment.edge_hash("a", "b", "Refines", D1, D3)
    both_moved = commitment.edge_hash("a", "b", "Refines", D3, D3)
    assert len({baseline, from_moved, to_moved, both_moved}) == 4


def test_the_edge_hash_binds_the_edge_type() -> None:
    assert commitment.edge_hash("a", "b", "Refines", D1, D2) != commitment.edge_hash(
        "a", "b", "Verifies", D1, D2
    )


def test_the_edge_hash_is_directional() -> None:
    """Reversing the endpoints is a different edge, not the same one."""
    assert commitment.edge_hash("a", "b", "Refines", D1, D2) != commitment.edge_hash(
        "b", "a", "Refines", D2, D1
    )


def test_framing_separates_endpoints_that_concatenation_would_merge() -> None:
    """The prototype's bug: ``("a", "bc")`` and ``("ab", "c")`` hashed alike."""
    assert commitment.edge_hash("a", "bc", "Refines", D1, D2) != commitment.edge_hash(
        "ab", "c", "Refines", D1, D2
    )


def test_framing_separates_an_edge_type_absorbed_into_an_endpoint() -> None:
    assert commitment.edge_hash("a", "b", "Refines", D1, D2) != commitment.edge_hash(
        "a", "bRefines", "", D1, D2
    )


def test_edge_tuple_matches_the_transcribed_formula() -> None:
    assert commitment.edge_tuple("a", "b", "Verifies") == lp(u("a")) + lp(u("b")) + lp(
        u("Verifies")
    )


# ── SEG-SREQ-003 — the design root ──────────────────────────────────────────


def test_design_root_matches_the_transcribed_formula() -> None:
    metadata = b'{"snapshotId":"2026-07-25T00:00:00Z-abc123"}'
    edges = [("SEG-SREQ-001", "SEG-SYS-001", "Refines")]
    expected = hashlib.sha256(
        lp(ROOT_TAG)
        + lp(metadata)
        + seq(sorted([D1, D2]))
        + seq([lp(u("SEG-SREQ-001")) + lp(u("SEG-SYS-001")) + lp(u("Refines"))])
    ).digest()
    assert commitment.design_root(metadata, [D2, D1], edges) == expected


def test_the_root_is_independent_of_node_and_edge_input_order() -> None:
    """Canonical sorting, so a traversal order cannot change a seal."""
    edges = [("a", "b", "Refines"), ("c", "d", "Verifies"), ("e", "f", "Implements")]
    forward = commitment.design_root(b"metadata", [D1, D2, D3], edges)
    backward = commitment.design_root(b"metadata", [D3, D2, D1], list(reversed(edges)))
    assert forward == backward


def test_the_root_preserves_duplicate_node_hashes() -> None:
    """Two same-type nodes with identical content share a digest; both count.

    Sorting must never deduplicate, or a graph would seal identically to a
    smaller graph that merely resembles it (ADR-0005 v).
    """
    assert commitment.design_root(b"", [D1], []) != commitment.design_root(b"", [D1, D1], [])


def test_the_root_reflects_its_edge_set() -> None:
    without = commitment.design_root(b"", [D1], [])
    with_edge = commitment.design_root(b"", [D1], [("a", "b", "Refines")])
    rewired = commitment.design_root(b"", [D1], [("a", "b", "Verifies")])
    assert len({without, with_edge, rewired}) == 3


def test_the_root_reflects_its_metadata() -> None:
    assert commitment.design_root(b"a", [D1], []) != commitment.design_root(b"b", [D1], [])


def test_the_root_treats_metadata_as_opaque_bytes() -> None:
    """ADR-0003: the caller supplies it canonical; this layer never parses it."""
    not_json = b"\x00\xff not json at all \x00"
    assert len(commitment.design_root(not_json, [D1], [])) == 32


def test_the_root_of_an_empty_design_set_is_total() -> None:
    """The primitive seals whatever it is given; refusing empty scope is the gate's."""
    assert len(commitment.design_root(b"", [], [])) == 32


def test_the_root_accepts_exhaustible_iterables() -> None:
    """Callers stream the design set; consuming it twice must not be required."""
    streamed = commitment.design_root(b"m", iter([D2, D1]), iter([("a", "b", "Refines")]))
    assert streamed == commitment.design_root(b"m", [D1, D2], [("a", "b", "Refines")])


# ── Domain separation across all three ──────────────────────────────────────


def test_the_three_domain_tags_are_distinct() -> None:
    assert len({commitment.NODE_TAG, commitment.EDGE_TAG, commitment.ROOT_TAG}) == 3


def test_each_preimage_leads_with_its_own_length_prefixed_tag() -> None:
    """Tag divergence, checked at the preimage rather than inferred from digests.

    A body-level collision between a node and an edge preimage is constructible
    in principle — the shapes are close — so asserting two digests differ would
    prove little. The re-derivations pin each preimage exactly; this states the
    property they encode.
    """
    node_preimage = lp(NODE_TAG) + lp(u("Requirement")) + seq([lp(u("nodeHash")) + lp(D1)])
    edge_preimage = lp(EDGE_TAG) + lp(u("a")) + lp(u("b")) + lp(u("Refines")) + lp(D1) + lp(D2)
    root_preimage = lp(ROOT_TAG) + lp(b"") + seq([D1]) + seq([])

    assert commitment.node_hash("Requirement", {"nodeHash": D1}) == hashlib.sha256(
        node_preimage
    ).digest()
    assert commitment.edge_hash("a", "b", "Refines", D1, D2) == hashlib.sha256(
        edge_preimage
    ).digest()
    assert commitment.design_root(b"", [D1], []) == hashlib.sha256(root_preimage).digest()

    assert len({node_preimage[4:23], edge_preimage[4:23], root_preimage[4:23]}) == 3


# ── Raw digests, determinism, purity ────────────────────────────────────────


def test_digests_enter_as_raw_bytes_and_hex_is_rejected() -> None:
    """A hex digest is 64 bytes; accepting one would silently seal the wrong value."""
    hex_digest = D1.hex().encode("ascii")
    with pytest.raises(ValueError, match="32"):
        commitment.node_hash("Requirement", {"nodeHash": hex_digest})
    with pytest.raises(ValueError, match="32"):
        commitment.edge_hash("a", "b", "Refines", D1, hex_digest)
    with pytest.raises(ValueError, match="32"):
        commitment.design_root(b"", [hex_digest], [])


def test_every_derivation_returns_thirty_two_raw_bytes() -> None:
    assert len(commitment.node_hash("Requirement", {"nodeHash": D1})) == 32
    assert len(commitment.edge_hash("a", "b", "Refines", D1, D2)) == 32
    assert len(commitment.design_root(b"", [D1], [])) == 32


def test_the_same_inputs_always_produce_the_same_hashes() -> None:
    """AC-007: same inputs, same hashes, across runs and environments."""
    fields = {"apiHash": D1, "bodyHash": D2}
    edges = [("a", "b", "Refines")]
    assert commitment.node_hash("Implementation", fields) == commitment.node_hash(
        "Implementation", fields
    )
    assert commitment.edge_hash("a", "b", "Refines", D1, D2) == commitment.edge_hash(
        "a", "b", "Refines", D1, D2
    )
    assert commitment.design_root(b"m", [D1], edges) == commitment.design_root(b"m", [D1], edges)


def test_the_layer_does_not_mutate_its_inputs() -> None:
    """Purity is the whole claim of ADR-0003; a shared mapping must survive."""
    fields = {"apiHash": D1, "bodyHash": D2}
    nodes = [D2, D1]
    edges = [("c", "d", "Verifies"), ("a", "b", "Refines")]
    commitment.node_hash("Implementation", fields)
    commitment.design_root(b"m", nodes, edges)
    assert fields == {"apiHash": D1, "bodyHash": D2}
    assert nodes == [D2, D1]
    assert edges == [("c", "d", "Verifies"), ("a", "b", "Refines")]
