import hashlib

ALGO = "SHA256"


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_sub_hashes(to_hash: dict[str, str]) -> dict[str, str]:
    """Hash each value in to_hash over its raw UTF-8 bytes."""
    return {k: sha256_hex(v) for k, v in to_hash.items()}


def compute_node_hash(sub_hashes: dict[str, str]) -> str:
    """Combine sub-hashes into a single nodeHash (sorted by key for determinism).

    Single-sub-hash nodes (Requirement, TestOutcome, Waiver): the one sub-hash IS
    the nodeHash. Multi-sub-hash nodes (Implementation, TestSpecification): hash the
    sorted concatenation of sub-hashes.
    """
    parts = [sub_hashes[k] for k in sorted(sub_hashes)]
    if len(parts) == 1:
        return parts[0]
    return sha256_hex("".join(parts))


def compute_edge_hash(
    from_iri: str,
    to_iri: str,
    edge_type: str,
    from_node_hash: str,
    to_node_hash: str,
) -> str:
    """H(from || to || type || nodeHash(from) || nodeHash(to)).

    Binds the edge to the content of both endpoints at affirmation time. A mismatch
    on recomputation marks the edge suspect (DEC-003).
    """
    return sha256_hex(from_iri + to_iri + edge_type + from_node_hash + to_node_hash)


def compute_merkle_hash(node_hash: str, dep_merkle_hashes: list[str]) -> str:
    """H(nodeHash || sorted(dep merkle hashes)).

    Sorted so the result is independent of traversal order.
    """
    return sha256_hex("".join([node_hash] + sorted(dep_merkle_hashes)))


def hash_object(hex_digest: str) -> dict[str, str]:
    return {"algorithm": ALGO, "hashValue": hex_digest}
