Commitment Layer
================

The commitment layer folds content hashes into the graph's three integrity
values: the hash of a node, the two-sided hash of an edge, and the design root
that seals a set of them. Its requirements say what each value is derived
from, and deliberately say nothing about how it is computed. The layer holds
no graph, no records and no metadata of its own — the snapshot metadata that
enters a design root comes from whoever calls for one.

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

.. sreq:: Node hashes derive from a node's content hashes
   :id: SEG-SREQ-005
   :refines: SEG-SYS-001

   The commitment layer shall derive each node hash solely from the node's
   type and from each content hash paired with the name of the content it
   covers.
