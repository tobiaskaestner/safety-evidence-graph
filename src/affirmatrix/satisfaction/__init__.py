"""The satisfaction evaluator — requirement coverage by transitive closure.

A pure, deterministic, side-effect-free predicate over the typed graph, behind
one interface (AC-002). DEC-001's leaf / non-leaf / orphan rule is written as
small named predicates rather than woven into imperative gate code, so the
configurable-satisfaction future (DEC-007) is a substitution rather than a
rewrite.

Two boundaries worth stating, because the prototype crossed both:

* **Staleness is not a satisfaction concern.** A stale outcome is *discarded*
  at proof time and blocks only if its removal opens a gap (design summary
  §9 step 4); it is not a coverage gap here.
* **An outcome counts as evidence only with both ``confirms`` and
  ``witnesses``**; an incomplete outcome is discarded, not failed (DEC-016).

The evaluator may assume a DAG: cycle *reporting* is the graph builder's
(SEG-SREQ-004), so the recursion terminates by precondition.

Iteration 0, backlog item B12 (SEG-SYS-002 and its decomposition).
"""
