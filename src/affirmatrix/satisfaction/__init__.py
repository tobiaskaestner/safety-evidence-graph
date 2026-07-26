"""The satisfaction evaluator — requirement coverage by transitive closure.

A pure, deterministic, side-effect-free predicate over the typed graph, behind
one interface: evaluation repeats (SEG-SREQ-009) and leaves the graph unchanged
(SEG-SREQ-010). The leaf and non-leaf rules (SEG-SREQ-006, SEG-SREQ-007) are
written as small named predicates rather than woven into imperative gate code,
so that a user-definable satisfaction rule would be a substitution here rather
than a rewrite everywhere.

Coverage is evaluated over the whole graph, never a partial scope
(SEG-SREQ-008): a parent cannot be declared satisfied while a child sits
outside the window being examined.

Two boundaries worth stating, because the prototype crossed both:

* **Staleness is not a satisfaction concern.** A stale outcome is *discarded*
  when a package is generated, and blocks only if its removal opens a gap; it
  is not a coverage gap here.
* **An outcome counts as evidence only if it both confirms a specification and
  witnesses an implementation**; an incomplete outcome is discarded, not
  failed. Discarding is not forgiving — it becomes a gap wherever it leaves a
  specification uncovered.

The evaluator may assume an acyclic refines relation: cycle *reporting* is the
graph builder's (SEG-SREQ-004), so the recursion terminates by precondition.

Iteration-0 backlog item B12 (SEG-SYS-002 and its decomposition).
"""
