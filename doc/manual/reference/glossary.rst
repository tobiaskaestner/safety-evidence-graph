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

   seal
      The recomputable commitment over the whole graph (per-edge hashes plus
      one flat-sealed root). Verification is recomputation.

   Safety BOM
      The lossy exchange projection of a safety case: the contract vector
      (guarantee, assumption down-closure, implementation pin) under a
      flat-openable commitment. Always published, always signed; the roll-up
      verdict never travels in it.
