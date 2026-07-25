Requirement Specification
=========================

The affirmatrix requirement specification — the first half of the repo's own
safety evidence graph (the dogfood case). IDs follow the SEG conventions:
``SEG-SYS-nnn`` (system), ``SEG-SREQ-nnn`` (software).

System requirements
-------------------

.. sys:: Content-anchored evidence graph
   :id: SEG-SYS-001

   affirmatrix shall build the evidence graph from node and edge records,
   deriving every node hash, edge hash, and design root solely from the raw
   source bytes of the nodes and the declared endpoints and types of the
   edges, reproducibly across runs.

.. sys:: Transitive requirement satisfaction
   :id: SEG-SYS-002

   affirmatrix shall determine the satisfaction of every requirement in the
   graph by transitive closure over the refines relation.

.. sys:: Suspicion derived from current content
   :id: SEG-SYS-003

   affirmatrix shall derive whether each strong edge is active or suspect from
   its endpoints' current content measured against the content it was affirmed
   against, and from the states of the strong edges it depends on.

.. sys:: Affirmation is a recorded human judgement
   :id: SEG-SYS-004

   affirmatrix shall record each affirmation as a human judgement bound to the
   content of both edge endpoints at the moment the judgement was made.

.. sys:: Self-verifiable evidence packages
   :id: SEG-SYS-005

   affirmatrix shall generate, for a defined scope and without altering the
   graph, an evidence package whose claims are verifiable by recomputation
   from the package's own contents.

.. sys:: Gates block on unmet conditions
   :id: SEG-SYS-006

   While any condition of a gate is unmet, affirmatrix shall report the action
   that gate guards as blocked.

.. sys:: The graph persists as hashes and references
   :id: SEG-SYS-007

   affirmatrix shall persist the evidence graph as hashes and references,
   never as the content those hashes cover.

.. sys:: Blocked scopes are refused
   :id: SEG-SYS-008

   If the proof gate reports a scope as blocked, then affirmatrix shall refuse
   to generate an evidence package for that scope.

Software requirements
---------------------

.. sreq:: Content hashes over verbatim byte spans
   :id: SEG-SREQ-001
   :refines: SEG-SYS-001

   The content extractor shall compute each content hash as the SHA-256 of
   the verbatim source byte span it covers.

.. sreq:: Edge hashes bind both endpoints
   :id: SEG-SREQ-002
   :refines: SEG-SYS-001

   The commitment layer shall compute each strong edge's hash from the edge's
   endpoint identifiers, the edge type, and the node hashes of both endpoints.

.. sreq:: A single design root over the design set
   :id: SEG-SREQ-003
   :refines: SEG-SYS-001

   The commitment layer shall compute the design root as one hash over the
   canonically sorted node hashes of the design set, the canonically sorted
   endpoints and types of its edges, and the metadata supplied by its caller.

.. sreq:: Refines cycles are a graph-level error
   :id: SEG-SREQ-004
   :refines: SEG-SYS-001

   If the refines edges form a cycle or a self-loop, then the graph builder
   shall report a graph-level error.

.. sreq:: Node hashes derive from a node's content hashes
   :id: SEG-SREQ-005
   :refines: SEG-SYS-001

   The commitment layer shall derive each node hash solely from the content
   hashes of the spans that node covers.

.. sreq:: Leaf satisfaction rule
   :id: SEG-SREQ-006
   :refines: SEG-SYS-002

   The satisfaction evaluator shall report a leaf requirement as satisfied
   when, and only when, it carries at least one active verifies edge, at least
   one active implements edge, and every test specification verifying it has a
   passing outcome.

.. sreq:: Non-leaf satisfaction rule
   :id: SEG-SREQ-007
   :refines: SEG-SYS-002

   The satisfaction evaluator shall report a non-leaf requirement as satisfied
   when, and only when, every requirement refining it is satisfied and every
   verifies or implements edge it carries is active.

.. sreq:: Satisfaction is evaluated over the whole graph
   :id: SEG-SREQ-008
   :refines: SEG-SYS-002

   The satisfaction evaluator shall determine satisfaction from the whole
   graph, never from a subset of it.

.. sreq:: Verdicts repeat
   :id: SEG-SREQ-009
   :refines: SEG-SYS-002

   The satisfaction evaluator shall produce the same verdict for the same
   graph on every evaluation.

.. sreq:: Evaluation leaves the graph unchanged
   :id: SEG-SREQ-010
   :refines: SEG-SYS-002

   The satisfaction evaluator shall leave the graph unchanged when evaluating
   it.

.. sreq:: Direct outdatedness
   :id: SEG-SREQ-011
   :refines: SEG-SYS-003

   While an affirmed edge's endpoint content differs from the content recorded
   at its last affirmation and every strong edge it depends on is active, the
   suspect detector shall report that edge as directly outdated.

.. sreq:: Transitive suspicion
   :id: SEG-SREQ-012
   :refines: SEG-SYS-003

   While an affirmed edge's endpoint content matches the content recorded at
   its last affirmation and any strong edge it depends on is not active, the
   suspect detector shall report that edge as transitively suspect.

.. sreq:: Outdated on both counts
   :id: SEG-SREQ-013
   :refines: SEG-SYS-003

   While an affirmed edge's endpoint content differs from the content recorded
   at its last affirmation and any strong edge it depends on is not active,
   the suspect detector shall report that edge as doubly outdated.

.. sreq:: Active edges
   :id: SEG-SREQ-014
   :refines: SEG-SYS-003

   While an affirmed edge's endpoint content matches the content recorded at
   its last affirmation and every strong edge it depends on is active, the
   suspect detector shall report that edge as active.

.. sreq:: State derives from a recorded and a current record source
   :id: SEG-SREQ-015
   :refines: SEG-SYS-003

   The suspect detector shall derive each edge's state from a recorded record
   source and a current record source alone.
