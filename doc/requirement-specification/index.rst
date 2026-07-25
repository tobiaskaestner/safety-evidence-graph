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
   deriving every node hash, edge hash, and design root solely from the nodes'
   declared types and their content in each type's canonical form, and from
   the edges' declared endpoints and types, reproducibly across runs.

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

.. sys:: One built-in graph vocabulary
   :id: SEG-SYS-009

   affirmatrix shall determine node kinds, edge kinds, and which edges
   propagate suspicion from a single built-in vocabulary that no configuration
   redefines.

.. sys:: Operable from the command line
   :id: SEG-SYS-010

   affirmatrix shall make every workflow it performs operable from its command
   line, with the outcome of each invocation distinguishable by its exit
   status.

.. sys:: Affirmation state changes only by the operator's act
   :id: SEG-SYS-011

   affirmatrix shall change the recorded affirmation state only as the direct
   result of an act the operator performs.

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

   The commitment layer shall derive each node hash solely from the node's
   type and from each content hash paired with the name of the content it
   covers.

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

.. sreq:: Unaffirmed edges are pending
   :id: SEG-SREQ-016
   :refines: SEG-SYS-001

   The graph builder shall report an edge that has never been affirmed as
   pending.

.. sreq:: Edges to absent nodes are broken
   :id: SEG-SREQ-017
   :refines: SEG-SYS-001

   The suspect detector shall report every edge touching a node that is absent
   from the current records as broken.

.. sreq:: Covered content is never persisted
   :id: SEG-SREQ-018
   :refines: SEG-SYS-007

   The affirmation store shall never persist the content that a hash it
   stores covers.

.. sreq:: Only valid records are written
   :id: SEG-SREQ-019
   :refines: SEG-SYS-007

   If a record does not validate against its schema, then the affirmation
   store shall reject it instead of writing it.

.. sreq:: Records read back as written
   :id: SEG-SREQ-020
   :refines: SEG-SYS-007

   The affirmation store shall reproduce each record it has written unchanged
   when that record is read back.

.. sreq:: Writes stay under the write root
   :id: SEG-SREQ-021
   :refines: SEG-SYS-007

   The affirmation store shall write every record beneath the write root it
   was given, and no record outside it.

.. sreq:: Records appear only when complete
   :id: SEG-SREQ-022
   :refines: SEG-SYS-007

   The affirmation store shall make a record readable only once it has been
   written completely.

.. sreq:: Deletion is explicit
   :id: SEG-SREQ-023
   :refines: SEG-SYS-007

   The affirmation store shall remove a persisted record only when removal of
   that record is requested.

.. sreq:: Affirmations bind both endpoints
   :id: SEG-SREQ-024
   :refines: SEG-SYS-004

   The affirmation recorder shall record each affirmation as a review event
   carrying the content hashes of both endpoints of the affirmed edge.

.. sreq:: Affirmations carry their source anchor
   :id: SEG-SREQ-025
   :refines: SEG-SYS-004

   The affirmation recorder shall record in every review event the source
   commit of each endpoint at the moment of affirmation.

.. sreq:: The recorder originates nothing
   :id: SEG-SREQ-026
   :refines: SEG-SYS-004

   The affirmation recorder shall originate no affirmation of its own.

.. sreq:: Only unaffirmed or outdated edges are affirmable
   :id: SEG-SREQ-027
   :refines: SEG-SYS-004

   The affirmation recorder shall accept an affirmation only for an edge that
   is pending, directly outdated, or doubly outdated.

.. sreq:: Supplied reasons are preserved
   :id: SEG-SREQ-028
   :refines: SEG-SYS-004

   The affirmation recorder shall record the reason supplied with an
   affirmation in the review event without altering it.
