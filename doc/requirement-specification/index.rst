Requirement Specification
=========================

The affirmatrix requirement specification — the first half of the repo's own
safety evidence graph (the dogfood case). IDs follow the SEG conventions:
``SEG-SYS-nnn`` (system), ``SEG-SREQ-nnn`` (software).

System requirements
-------------------

.. sys:: Sealed evidence graphs
   :id: SEG-SYS-001

   affirmatrix SHALL bind requirements, implementation, test specifications,
   and test outcomes into a content-anchored evidence graph carrying a single
   recomputable commitment (the seal).

Software requirements
---------------------

.. sreq:: Content binding over raw byte spans
   :id: SEG-SREQ-001
   :refines: SEG-SYS-001

   The graph SHALL store content hashes computed over raw source byte spans;
   parsers locate spans but never feed the hash (DEC-003).

.. sreq:: Affirmation bound to content state
   :id: SEG-SREQ-002
   :refines: SEG-SYS-001

   An affirmation SHALL be recorded against the exact content hashes of both
   edge endpoints; the engine builds but never operates affirmation (AC-006).
