# Notes to the RE — surfaced by the B10 pass (affirmation store, write face)

Raised by the SWE during B10 (`tool` commit `ba34c5c`, 2026-08-10) and parked
per cardinal rule 3: gaps become requirements, not code. Numbered G-nn as in
the B10 report-phase plan; restated fully here because that plan was a
session-scratch document. Each item is a candidate for requirements work —
none blocks B11.

## G3 — `ReviewEvent` carries no role

ADR-0009's decision section says the ReviewEvent record states "the edge, the
content hashes of both endpoints, the source anchor per endpoint, **the role**
and the reasoning." The `records.ReviewEvent` dataclass B5 shipped carries
everything except the role. An accepted ADR and the shipped vocabulary
diverge; adding a field changes what an affirmation *is*, so it needs a
requirement, not a patch. (The missing timestamp and identifier are
deliberate: ADR-0009 assigns *when* to the commit, and the absent identifier
is what makes review events ordinal-numbered and append-only.)

## G6 — the identifier base has no home

The design summary (§8.1) puts the namespace in `config.json` alongside org,
repo URLs, standard and SIL level; ruling 3 of the B10 work order deferred
`config.json`, and `affirmatrix.config` is a stub. B10 minted IRIs anyway, so
the base lives as a module constant, `identity.BASE` — safe, because the base
never enters a hash preimage (ADR-0007), but temporary. The real question:
how `config.json` reconciles with `affirmatrix.yaml` in the mono-repo
(DEC-030 c3). The identifier base is the first field that needs the answer.

## G8 — `snapshotId` is not a portable directory name

The design summary's format (§7.5, `2024-03-15T14:32:00Z-a1b2c3d4e5f6`)
contains colons; it becomes a directory under `proofs/`, and colons are legal
on POSIX, illegal on Windows. Whether a case must be checkable out on Windows
is a requirements question, and the format is cheapest to change before any
proof directory exists (none does yet — minting the id is the proof
generator's, B16). B10's store enforces path safety only, deliberately not
the §7.5 shape.

## G9 — a current stream handed to the write face silently resets affirmations

Every edge in a *current* record stream is `pending` by construction (the
store loader, and later the extractors, produce no affirmed state). Handing
such a stream to `write_edges` would rewrite every affirmed edge back to
pending — each change individually "on request" (so SEG-SREQ-033 is
satisfied to the letter), collectively the silent loss of every affirmation
in the case. The SWE assessed this the most consequential way the component
can be misused, and did not design a guard because the guard would be a new
requirement. Candidate: the store shall refuse to replace an edge record
carrying an affirmed hash with one carrying none, absent an explicit demotion
request.

## G15 — a persisted node record cannot locate its own content

**FSM ruling attached (2026-08-10): confirmed a real B5 gap; the source
location is to be recorded per content hash in the `NodeRecord`** — per hash,
not per node, because a node can carry several hashes over different byte
spans (an Implementation's `apiHash` and `bodyHash`). Background: AC-005 has
content fetched transiently from the versioned source repos when needed (the
affirmation diff), which presumes the record says where to fetch from; the
prototype's node schemas carried `seg:sourceRepo`/`seg:sourcePath` for
exactly this, and the B5 vocabulary carries neither. Requirements and the
record vocabulary need the field; the store then persists it like any other
reference. Suggest treating G3 + G15 as one review of `records` against
ADR-0009 and AC-005 rather than two point fixes.

## Standing, related

`pyproject.toml` still has no owner (ADR-0006 consequences). B10 edited it
under one-time explicit FSM authorization to add the first runtime
dependencies (`jsonschema`, `referencing`); the ownership question is now
live rather than theoretical.
