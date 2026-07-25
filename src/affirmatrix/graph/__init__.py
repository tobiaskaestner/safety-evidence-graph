"""The graph builder — records to the in-memory graph.

Assembles node and edge records into the typed graph the rest of the engine
reads, and reports ``refines`` cycles and self-loops as graph-level errors
(SEG-SREQ-004). It carries each edge's *recorded* link state and never invents
one; a newly seen edge is ``pending`` (SEG-SREQ-016), which is a state, not a
default. Deriving current state from content is the suspect detector's job —
the builder assembles, the detector derives (ADR-0004).

Local identifiers must be unique within a case; a duplicate is a graph-level
error (ADR-0007).

Iteration 0, backlog items B7 (build) and B8 (cycles).
"""
