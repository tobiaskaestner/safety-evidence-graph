"""The store loader — iteration 0's record source over the would-be store.

Reads the hand-authored fixture under ``tests/fixtures/would_be_store/`` and
produces the *current* record stream: node records with their content hashes,
and the edges declared alongside them.

**Test scaffolding.** No requirements attach to this adapter; it exists so the
engine has an input before record production is built, and it retires when the
real extractors and the requirements reader land. It is the "would-be store" —
it holds content and is deliberately not schema-validated, unlike the
affirmation store, which holds hashes and references and always is.

Iteration-0 backlog item B9.
"""
