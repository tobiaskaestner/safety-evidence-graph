"""The suspect detector — link state derived from current content.

Recomputes each strong edge's hash from today's node hashes, compares it with
the hash the edge was affirmed against, and derives the edge's state:
directly outdated (one endpoint moved, SEG-SREQ-011), doubly outdated (both,
SEG-SREQ-013), transitively suspect (neither, but a strong edge it depends on
is not active, SEG-SREQ-012), active (SEG-SREQ-014), and broken (an endpoint no
longer exists, SEG-SREQ-017).

State derives from exactly two inputs — a recorded record source and a current
one (SEG-SREQ-015) — and derivation never writes: recorded affirmations are
left untouched by it (SEG-SREQ-034).

Transitive suspicion is *derived*, never affirmed. It clears by recomputation
once the edges it depended on return to active, so no one is asked to
re-affirm an edge whose own endpoints never moved — that would be a signature
on something that did not change. Affirmation resolves only the directly and
doubly outdated cases.

Pending and broken edges have no stored hash to compare against: the absence of
a stored hash is a state, not a mismatch (ADR-0005).

Iteration-0 backlog item B13 (SEG-SYS-003 and its decomposition).
"""
