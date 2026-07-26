"""The record source — the input interface, and the persisted vocabulary.

Two things live here because they are one thing: the record *types* the engine
exchanges, and the protocol that yields them.

* **The protocol.** One interface, several adapters: the store loader, the
  requirements reader, the content extractor, the outcome extractor, and the
  read face of the affirmation store. Swapping iteration 0's store loader for
  the real extractors is an adapter change, not a rewrite.
* **Two roles.** A record stream is either *recorded* — what the affirmation
  store holds, edge records carrying the hash and state they were last
  affirmed with — or *current*, what a producer derives from today's content.
  Deriving an edge's state means comparing exactly these two (SEG-SREQ-015),
  so both need names.
* **The vocabulary.** Node records, edge records and review events are declared
  here so the affirmation store can serialize them without importing the
  components that compute them. That is the boundary keeping persistence below
  package generation in the layering (ADR-0004). Evidence-package documents
  join them when the generator lands.

Records carry hashes and references, never the content those hashes cover
(SEG-SREQ-018), and they are frozen: a record that could be edited in flight
would let a hash and the thing it describes drift apart between the producer
that made it and the store that keeps it.

Identifiers here are case-local and stable — the same strings that enter a hash
preimage. Absolute IRIs are minted at serialization time (ADR-0007), so a
record cannot disagree with its own hash about what it identifies.

Iteration-0 backlog item B5.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Protocol, runtime_checkable

from affirmatrix._hashing import checked_digest


class LinkState(StrEnum):
    """The states a strong edge can be in.

    ``pending`` and ``broken`` are not resolvable by affirming: a pending edge
    needs a first affirmation, and a broken edge needs its missing endpoint
    restored or the edge removed. Both block an evidence package all the same.
    """

    PENDING = "pending"
    ACTIVE = "active"
    DIRECTLY_OUTDATED = "directlyOutdated"
    TRANSITIVELY_SUSPECT = "transitivelySuspect"
    DOUBLY_OUTDATED = "doublyOutdated"
    BROKEN = "broken"


class SourceRole(StrEnum):
    """Which of the two streams a record source supplies.

    Named because the difference is not cosmetic: comparing *recorded* against
    *current* is the whole of drift detection, and getting them the wrong way
    round inverts every verdict it produces.
    """

    RECORDED = "recorded"
    CURRENT = "current"


def _require(value: str, what: str) -> str:
    if not value:
        raise ValueError(f"a record needs a non-empty {what}")
    return value


@dataclass(frozen=True, slots=True)
class NodeRecord:
    """A node as the graph knows it: an identity, a kind, and its hashes.

    The content those hashes cover lives in the source that produced them and
    is fetched transiently when a human needs to look at it. It is never
    carried here.
    """

    local_id: str
    kind: str
    content_hashes: Mapping[str, bytes]

    def __post_init__(self) -> None:
        _require(self.local_id, "local identifier")
        _require(self.kind, "kind")
        if not self.content_hashes:
            raise ValueError(f"node {self.local_id!r} needs at least one content hash")
        frozen = {
            name: checked_digest(digest, f"{self.local_id}.{name}")
            for name, digest in self.content_hashes.items()
        }
        object.__setattr__(self, "content_hashes", MappingProxyType(frozen))


@dataclass(frozen=True, slots=True)
class EdgeRecord:
    """An edge as the graph knows it, with the state it was last left in.

    ``edge_hash`` is the hash the edge was affirmed against — present exactly
    when there was an affirmation to record one. An edge that has never been
    affirmed has nothing to compare against, which is why the field is absent
    rather than zeroed: a placeholder would be indistinguishable from a real
    hash that happens to mismatch.
    """

    from_id: str
    to_id: str
    kind: str
    state: LinkState
    edge_hash: bytes | None = field(default=None)

    def __post_init__(self) -> None:
        _require(self.from_id, "source identifier")
        _require(self.to_id, "target identifier")
        _require(self.kind, "kind")
        if self.state is LinkState.PENDING and self.edge_hash is not None:
            raise ValueError(
                f"edge {self.from_id!r} -> {self.to_id!r} is pending and so was never "
                "affirmed; it cannot carry the hash it was affirmed against"
            )
        if self.state is LinkState.ACTIVE and self.edge_hash is None:
            raise ValueError(
                f"edge {self.from_id!r} -> {self.to_id!r} is active and must carry the "
                "hash it was affirmed against"
            )
        if self.edge_hash is not None:
            checked_digest(self.edge_hash, f"{self.from_id}->{self.to_id} edge hash")


@dataclass(frozen=True, slots=True)
class ReviewEvent:
    """One recorded human judgement about one edge.

    Carries the content hashes of both endpoints, so the judgement is bound to
    exactly what was reviewed (SEG-SREQ-024), and the source revision each
    endpoint stood at when it was made (SEG-SREQ-025). That second pair cannot
    be reconstructed later — nothing else correlates a source revision to the
    moment someone accepted it — so it is captured here or lost.

    The reason is stored exactly as supplied (SEG-SREQ-028). An empty one is
    allowed: a thin justification is the operator's to give and a reader's to
    judge, and silently substituting text would make the record a paraphrase of
    the judgement rather than the judgement.
    """

    from_id: str
    to_id: str
    kind: str
    from_node_hash: bytes
    to_node_hash: bytes
    from_source_revision: str
    to_source_revision: str
    reason: str

    def __post_init__(self) -> None:
        _require(self.from_id, "source identifier")
        _require(self.to_id, "target identifier")
        _require(self.kind, "kind")
        _require(self.from_source_revision, "source revision for the source endpoint")
        _require(self.to_source_revision, "source revision for the target endpoint")
        checked_digest(self.from_node_hash, f"{self.from_id} node hash")
        checked_digest(self.to_node_hash, f"{self.to_id} node hash")


@runtime_checkable
class RecordSource(Protocol):
    """Everything the engine consumes arrives through this.

    Structural, not inherited: an adapter satisfies it by having the two
    methods, so a producer never has to import the engine to be one. Both
    return iterators — a source may stream, and nothing may assume it can be
    walked twice.
    """

    def nodes(self) -> Iterator[NodeRecord]:
        """The node records this source supplies."""
        ...

    def edges(self) -> Iterator[EdgeRecord]:
        """The edge records this source supplies."""
        ...


__all__ = [
    "EdgeRecord",
    "LinkState",
    "NodeRecord",
    "RecordSource",
    "ReviewEvent",
    "SourceRole",
]
