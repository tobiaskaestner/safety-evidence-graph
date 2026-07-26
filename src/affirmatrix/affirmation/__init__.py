"""The affirmation recorder — writing the human judgement.

Builds the review event that records an affirmation: the edge, the content
hashes of both endpoints (SEG-SREQ-024), the reason supplied, preserved as
given (SEG-SREQ-028), and the source commit of each endpoint at the moment of
judgement (SEG-SREQ-025). That last one cannot be reconstructed afterwards —
nothing else correlates a source revision to the moment someone accepted it —
so it is captured at affirmation or not at all.

**Capability, not authority.** This component is built and unit-tested here;
an operator runs it. The recorder originates no affirmation of its own
(SEG-SREQ-026), and only an unaffirmed or outdated edge can be affirmed
(SEG-SREQ-027) — affirmation cannot clear a broken edge or a stale outcome,
which need an endpoint fix or a re-run. It is a review act, not a button that
makes the graph green.

Persisting the event is the affirmation store's; composing it is this
component's.

Iteration-0 backlog item B14 (SEG-SYS-004 and its decomposition).
"""
