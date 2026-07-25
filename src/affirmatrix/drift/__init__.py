"""The suspect detector — link state derived from current content.

Recomputes each strong edge's hash from today's node hashes, compares it with
the hash the edge was affirmed against, and derives the edge's state:
``directlyOutdated`` (one endpoint moved), ``doublyOutdated`` (both),
``transitivelySuspect`` (neither, but a strong descendant is non-active), and
``broken`` (an endpoint no longer exists, SEG-SREQ-017).

Transitive suspicion is *derived*, never affirmed, and auto-clears by
recomputation once descendants return to active (DEC-005 / AC-010). Affirmation
resolves only ``directlyOutdated`` and ``doublyOutdated``.

``pending`` and ``broken`` edges have no stored hash to compare against: the
absence of a stored hash is a state, not a mismatch (ADR-0005).

Iteration 0, backlog item B13 (SEG-SYS-003 and its decomposition).
"""
