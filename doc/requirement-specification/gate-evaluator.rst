Gate Evaluator
==============

A gate is a set of conditions that must hold before an action may proceed.
The gate evaluator judges those conditions and reports the result; it does not
enforce it. Its requirements fix which findings block and which merely inform,
what a blocked report must contain for anyone to act on it, and one condition
that would otherwise pass in silence — a scope with nothing in it to seal.

.. sreq:: Severity decides what blocks
   :id: SEG-SREQ-042
   :refines: SEG-SYS-006

   The gate evaluator shall treat a condition reported as an error or a
   warning as blocking, and a condition reported as information as not
   blocking.

.. sreq:: Every unready edge is listed
   :id: SEG-SREQ-043
   :refines: SEG-SYS-006

   The gate evaluator shall list in its report every strong edge in scope that
   is not active.

.. sreq:: Gaps are reported where coverage is missing
   :id: SEG-SREQ-044
   :refines: SEG-SYS-006

   The gate evaluator shall report a coverage gap at the requirement that
   lacks coverage, never at a requirement that it refines.

.. sreq:: An empty design set cannot be sealed
   :id: SEG-SREQ-045
   :refines: SEG-SYS-006

   If a scope's design set is empty, then the gate evaluator shall report that
   scope as blocked.
