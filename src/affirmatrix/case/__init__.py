"""The affirmation store — persistence of the graph, both directions.

The successor of the four-stream topology's repo G, and the only component that
touches persisted graph artifacts: node and edge hash records, ReviewEvents,
and sealed proofs under ``case/`` (SEG-SYS-007). It stores hashes and
references only — content never reaches it (AC-005) — and it is the single
point at which schema validation is applied, on write *and* on read-back
(AC-008).

Its **read face is a record source** (ADR-0004): persisted edge records
carrying stored ``edgeHash`` and ``linkState`` enter the engine through the
AC-003 protocol, so drift detection is two record sources in, one derived state
out, and the graph builder never learns whether a hash came from disk or from
source. Its write face is exclusive.

Write policy (ADR-0008): writes land in place in the working ``case/`` by
default, per file atomically, never deleting a record this run did not write;
``--output-dir`` relocates the root. The tool never runs git — the review
surface is the dirty tree and the FSM commits.

The module keeps the name ``case`` for one-word symmetry with the directory it
owns; module names denote the artifact, component names the actor.

Iteration 0, backlog items B10 (write) and B11 (read-back).
"""
