"""The taxonomy provider — the built-in safety-evidence graph type.

Single internal source for the node and edge kinds (SEG-SREQ-029), which edge
kinds propagate suspicion (SEG-SREQ-030), the content-hash names each node kind
carries (SEG-SREQ-032), and the local-vs-serialized token spelling
(``Requirement`` / ``seg:Requirement``, ADR-0007). Nothing else in the engine
hardwires a kind name; a record declaring a kind this provider does not declare
is rejected (SEG-SREQ-031).

This version populates the provider from constants — the built-in
safety-evidence graph type. A user-definable graph vocabulary is out of scope
and would plug in here rather than anywhere else, which is the point of routing
every kind lookup through one place.

Because ADR-0005 hashes both the node kind and the content-hash names, the
spellings this provider declares are integrity-relevant: renaming one is an
affirmation event, not a refactor.

Iteration-0 backlog item B6.
"""
