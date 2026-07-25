"""The gate evaluator — reporting a guarded action as blocked.

While any condition of a gate is unmet, the action that gate guards is blocked
(SEG-SYS-006). Iteration 0 implements **Gate 2, the proof gate** only, whose
output is the CoverageReport: structural gaps at the leaf, the ``suspectLinks``
worklist (every in-scope strong edge that is not ``active`` — including
``pending`` and ``broken``, which affirmation cannot resolve), stale outcomes,
and the overall status.

Gate 1 (commit) and Gate 3 (release) are deferred past iteration 0: Gate 1's
conditions are all extractor conditions and record production is deferred;
Gate 3 needs a sealed package and release tags.

Iteration 0, backlog item B15.
"""
