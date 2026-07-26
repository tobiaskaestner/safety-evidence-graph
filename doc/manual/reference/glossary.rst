Glossary
========

.. glossary::

   safety evidence graph
      The artifact affirmatrix manages: a content-anchored graph binding
      requirements, implementation, test specifications, and outcomes,
      carrying affirmations, derived suspicion, verdicts, and a seal.
      ("SEG" in the research record.)

   affirmation
      A human judgement recorded against the exact content hashes of an
      edge's endpoints. The engine builds affirmation but never operates it.

   drift
      A change to committed content. Drift flips affirmed edges resting on
      the changed content to *suspect*.

   verdict
      The user-authored validity computation (stratified Datalog) over the
      committed graph. Reproducible: a pure function of committed content.

   canonical content form
      The representation of a node's content that its content hash covers.
      Each node type has one, and an extractor earns its place by producing
      it: for Python source it is the verbatim source byte span; for a
      requirement it is derived from the needs export. Hashing a canonical
      form rather than whatever a tool happens to emit is what makes a
      content hash reproducible by a third party.

      A *representation*, not an ordering — contrast :term:`canonical sort`.

   canonical sort
      The fixed ordering applied to a set before it is folded into one hash:
      node hashes ascending byte-wise over the raw digests, edge tuples framed
      and then sorted as byte strings, duplicates preserved (ADR-0005). It is
      what makes the flat-sealed root independent of the order the graph
      happened to be traversed in.

      An *ordering rule*, not a representation — contrast
      :term:`canonical content form`.

   seal
      The recomputable commitment over the whole graph (per-edge hashes plus
      one flat-sealed root). Verification is recomputation.

   Safety BOM
      The lossy exchange projection of a safety case: the contract vector
      (guarantee, assumption down-closure, implementation pin) under a
      flat-openable commitment. Always published, always signed; the roll-up
      verdict never travels in it.
