"""Records as JSON-LD entries, and the documents that collect them.

Two responsibilities, one file, because they are two halves of one rule: an
entry carries exactly the fields of the record it serializes — no more, because
a field that could carry covered content must not exist (SEG-SREQ-018), and no
less, because a field the store drops is a field read-back cannot reproduce.

The envelope is the store's, not the record's. ``@context`` and ``@graph`` are
how a case describes itself; the schemas describe the entries inside.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from operator import itemgetter
from pathlib import Path

from affirmatrix import identity
from affirmatrix.case._errors import AffirmationStoreError
from affirmatrix.records import EdgeRecord, NodeRecord, ReviewEvent, hex_digest

Entry = dict[str, object]

_GRAPH = "@graph"
_CONTEXT = "@context"
_ID = "id"


def node_entry(record: NodeRecord) -> Entry:
    """One node record as a JSON-LD entry.

    :implements: SEG-SREQ-018

    Every value is an identifier, a kind token or a digest. The content those
    digests cover has no field to travel in, which is the structural half of
    the guarantee; the schema's refusal of any undeclared property is the other.
    """
    entry: Entry = {
        _ID: identity.node_iri(record.local_id),
        "type": f"seg:{record.kind}",
        "seg:localId": record.local_id,
    }
    for name, digest in sorted(record.content_hashes.items()):
        entry[f"seg:{name}"] = hex_digest(digest)
    return entry


def edge_entry(record: EdgeRecord) -> Entry:
    """One edge record as a JSON-LD entry.

    :implements: SEG-SREQ-018

    The endpoints are written as their own fields rather than left to be read
    out of the entry's identifier. An identifier is an opaque key (ADR-0007),
    and a reader that split one would be relying on a separator that either
    part may itself contain.
    """
    entry: Entry = {
        _ID: identity.edge_iri(record.kind, record.from_id, record.to_id),
        "type": f"seg:{record.kind}",
        "seg:from": identity.node_iri(record.from_id),
        "seg:to": identity.node_iri(record.to_id),
        "seg:linkState": record.state.value,
    }
    if record.edge_hash is not None:
        entry["seg:edgeHash"] = hex_digest(record.edge_hash)
    return entry


def event_entry(event: ReviewEvent, ordinal: int) -> Entry:
    """One review event as a JSON-LD entry, at the position it was appended to.

    :implements: SEG-SREQ-018

    A review event carries nothing that identifies it — the same edge may be
    affirmed more than once — so its identity is where it sits in the case's
    sequence of events. That is available because events are only ever
    appended.

    The revisions inside ``seg:affirmedAt`` are named apart from the endpoint
    fields rather than repeating ``seg:from`` and ``seg:to`` inside a nested
    object. A term in the shared context is defined once for the whole
    document, and the endpoint term is defined as holding an identifier — so
    reusing the name here would tell a reader that a git revision is one, and
    it would be resolved as such against the context's base.
    """
    return {
        _ID: identity.review_event_iri(ordinal),
        "type": "seg:ReviewEvent",
        "seg:from": identity.node_iri(event.from_id),
        "seg:to": identity.node_iri(event.to_id),
        "seg:relation": f"seg:{event.kind}",
        "seg:fromNodeHash": hex_digest(event.from_node_hash),
        "seg:toNodeHash": hex_digest(event.to_node_hash),
        "seg:affirmedAt": {
            "seg:fromRevision": event.from_source_revision,
            "seg:toRevision": event.to_source_revision,
        },
        "seg:reason": event.reason,
    }


def merged(existing: Iterable[Entry], incoming: Iterable[Entry]) -> list[Entry]:
    """The document's entries after this write, keyed by identifier.

    :implements: SEG-SREQ-023

    An entry the call did not mention is carried through exactly as it was
    read. That is what makes a write of one record a write of one record: with
    the whole document as the unit of atomicity, anything not preserved here is
    silently deleted, and a producer that happened to yield a short stream
    would prune the case without saying so.

    Sorted by identifier, so the document is a function of what it holds rather
    than of the order a producer streamed it in, and two runs over an unchanged
    graph leave byte-identical files.
    """
    entries = {entry[_ID]: entry for entry in existing}
    entries.update({entry[_ID]: entry for entry in incoming})
    return sorted(entries.values(), key=itemgetter(_ID))


def read_entries(path: Path) -> list[Entry]:
    """The entries a document already holds, or none if it does not exist yet.

    A document that cannot be read as one raises rather than being replaced.
    Overwriting it would be precisely the silent removal that explicit deletion
    exists to rule out — and the records it holds may be the only place an
    affirmation survives.
    """
    if not path.exists():
        return []
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AffirmationStoreError(
            f"{path} cannot be read as an instance document: {error}"
        ) from error
    entries = document.get(_GRAPH) if isinstance(document, Mapping) else None
    if not isinstance(entries, list):
        raise AffirmationStoreError(
            f"{path} is not an instance document: it declares no {_GRAPH!r} of entries"
        )
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get(_ID), str):
            raise AffirmationStoreError(
                f"{path} holds {entry!r}, which is not an entry with an identifier"
            )
    return entries


def serialized(document: Mapping[str, object], context_reference: str) -> bytes:
    """One document's bytes: deterministic, sorted, newline-terminated.

    Indented and one field per line because the review surface for the whole
    store is somebody reading a diff of it, and a single-line document would
    show every change as the same change.
    """
    payload = {_CONTEXT: context_reference, **document}
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def collection(entries: Iterable[Entry], context_reference: str) -> bytes:
    """A per-kind collection document's bytes."""
    return serialized({_GRAPH: list(entries)}, context_reference)


__all__ = [
    "Entry",
    "collection",
    "edge_entry",
    "event_entry",
    "merged",
    "node_entry",
    "read_entries",
    "serialized",
]
