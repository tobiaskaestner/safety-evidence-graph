"""The affirmation store — persistence of the graph, both directions.

The only component that touches persisted graph artifacts: node and edge hash
records, review events, and sealed evidence packages under ``case/``
(SEG-SYS-007). It persists hashes and references only — the content those
hashes cover never reaches it (SEG-SREQ-018) — and it is the single point at
which schema validation is applied, rejecting an invalid record rather than
writing it (SEG-SREQ-019) and reproducing every record it wrote unchanged when
that record is read back (SEG-SREQ-020).

Its **read face is a record source** (ADR-0004): persisted edge records
carrying their stored edge hash and link state enter the engine through the
record-source protocol, so drift detection takes two record sources in and
gives one derived state out, and the graph builder never learns whether a hash
came from disk or from a producer. Its write face is exclusive.

Write policy (ADR-0008): writes land in place in the working ``case/`` by
default, each record appearing only once it is complete (SEG-SREQ-022), never
removing a record unless removal was requested (SEG-SREQ-023), and never
outside the write root it was given (SEG-SREQ-021). An output directory can
relocate that root. The tool performs no version-control operations of its
own — the review surface is the working tree, and a maintainer records it.

The module keeps the name ``case`` for one-word symmetry with the directory it
owns; module names denote the artifact, component names the actor.

Iteration-0 backlog items B10 (write) and B11 (read-back).
"""
