"""The record source — the AC-003 interface, and the persisted vocabulary.

Two things live here because they are one thing: the record *types* the engine
exchanges, and the protocol that yields them.

* **The protocol.** One interface, several adapters: the store loader, the
  requirements reader, the content extractor, the outcome extractor, and the
  read face of the affirmation store. Swapping iteration 0's store loader for
  the real extractors is an adapter change, not a rewrite.
* **Two roles.** A record stream is either *recorded* (what the affirmation
  store holds — edge records carrying stored ``edgeHash`` and ``linkState``) or
  *current* (what a producer derives from today's content). Drift detection is
  the comparison of the two.
* **The vocabulary.** Node records, edge records, review events and the proof
  documents are declared here so the affirmation store can serialize them
  without importing the components that compute them — the boundary that keeps
  ``case`` below ``proof`` in the layering (ADR-0004).

Producers emit *content hashes*, never content (AC-005).

Iteration 0, backlog item B5.
"""
