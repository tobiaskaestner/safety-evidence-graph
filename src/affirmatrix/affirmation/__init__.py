"""The affirmation recorder — writing the human judgement.

Builds the ReviewEvent that records an affirmation: the edge, the affirming
role, the reasoning, and — mandatory, uncapturable later — the per-endpoint
source-repo commit SHAs at the moment of judgement (``seg:affirmedAt``,
DEC-006 / AC-009). Setting an affirmed edge back to ``active`` is the other
half.

**Capability, not authority (AC-006).** This component is built and unit-tested
here; the FSM operates it. The engine never affirms on its own, and affirmation
cannot clear a ``broken`` edge or a stale outcome — those need an endpoint fix
or a re-run.

Persisting the event is the affirmation store's; composing it is this
component's.

Iteration 0, backlog item B14 (SEG-SYS-004 and its decomposition).
"""
