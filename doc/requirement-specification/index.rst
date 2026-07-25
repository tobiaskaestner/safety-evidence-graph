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
