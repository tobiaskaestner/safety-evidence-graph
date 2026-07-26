"""The gate evaluator — reporting a guarded action as blocked.

While any condition of a gate is unmet, the action that gate guards is blocked
(SEG-SYS-006). Iteration 0 implements the **package gate** only, whose output
is the coverage report: structural gaps reported at the leaf where coverage is
actually missing rather than up the ancestor chain, the worklist of every
in-scope strong edge that is not active — including pending and broken, which
affirmation cannot resolve — stale outcomes, and the overall status.

The commit gate and the release gate are deferred past iteration 0: the commit
gate's conditions are all extraction conditions and record production is
deferred, and the release gate needs a sealed package and a release to check.

Iteration-0 backlog item B15.
"""
