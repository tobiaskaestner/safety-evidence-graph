0007. Case-local identifiers in preimages; absolute IRIs in serialization
==========================================================================

Status
------

Accepted, 2026-07-25.

Context
-------

SEG-SREQ-002 puts an edge's endpoint identifiers into its hash, so whatever
string identifies a node becomes irreversible the moment an edge is
affirmed. The design of record identifies nodes by absolute IRI over a
project namespace, and the design summary's own open questions (§14) record
that this namespace is project-specific and its relocation is deferred —
while DEC-029 has already renamed the project once. The input most likely
to change was about to become the input least able to.

A configurable base was considered and rejected: it would make node and
edge hashes a function of configuration, so editing one line of YAML would
re-hash the graph and trip every strong edge to suspect with no content
having changed, and it would activate AC-011's proof-binding obligation for
a facet the design defers to Phase C.

Decision
--------

**Preimages carry case-local stable identifiers.** The strings that enter
the ``edgeTuple`` of ADR-0005 are identities within one case, not IRIs:

- a Requirement's is its **need ID verbatim** — ``SEG-SREQ-001``;
- a TestSpecification's is its manual ``SEG-TS-nnn``, independent of test
  function name and file location (DEC-003);
- a TestOutcome's is ``{runId}/{specId}``;
- a Waiver's is the FSM-assigned ID;
- an Implementation's is pending a separate ruling; until it is taken, only
  hand-authored fixture identities exist, since record production is
  deferred past iteration 0.

**Type tokens are local too, and the mapping is prefix-only.** The local
token is the serialized token minus the ``seg:`` prefix — local
``Requirement`` serializes as ``seg:Requirement``, local ``Refines`` as
``seg:Refines``. One rule, no translation table. Node kinds are
``Requirement``, ``Implementation``, ``TestSpecification``, ``TestOutcome``,
``Waiver``; edge kinds are ``Refines``, ``Verifies``, ``Implements``,
``Confirms``, ``Witnesses``, ``Excuses``, ``Calls``. The taxonomy provider
owns both spellings (AC-001), and per ADR-0005 those spellings are
integrity-relevant.

**Absolute IRIs are serialization, minted by ``affirmatrix.identity``.**
Instance documents continue to carry absolute IRIs for every ``id``,
``seg:from``, ``seg:to`` and cross-reference field, as the design summary
§8.4 requires and the schemas enforce. ``identity`` mints them from a base
that is free to change, and is the only module that knows the base. It
never participates in hashing; an import rule keeps ``commitment``
independent of it. Minted IRIs remain **opaque keys** (§4.7): tooling reads
endpoints from ``seg:from``/``seg:to`` and never parses an ``id`` back into
parts.

**The ``seg:`` vocabulary prefix stays.** DEC-029 keeps "safety evidence
graph" as the artifact term; the vocabulary namespace is a project constant
and never enters a preimage.

**Local identifiers must be unique within a case.** A duplicate is a
graph-level error reported by the graph builder, consistent with the
design's existing duplicate-ID error conditions. Their lexical shape is
validated at the taxonomy and schema layer; to the commitment layer a local
identifier is an opaque byte string.

Consequences
------------

- The namespace base becomes a serialization concern. A rebrand, a domain
  move, or a per-project base is a re-serialization: no hash changes, no
  affirmation is invalidated, no edge goes suspect.
- No configuration value reaches any preimage, so AC-013 holds without
  qualification and AC-011's proof-binding obligation stays dormant, as the
  design intends for v1.
- AC-016 is satisfied where it applies: the IRIs published in proofs remain
  globally unique and stable.
- **The trade, stated plainly.** Preimage uniqueness is case-local. Two
  organizations whose cases each contain ``SEG-SREQ-001`` can compute equal
  edge hashes for structurally identical edges. This is invisible in v1,
  where composition is out of scope, and the remedy when Phase C arrives is
  to fold a case identifier into the design root's caller-supplied metadata
  — which sits outside every per-edge preimage, so it costs nothing now and
  requires no re-hashing of edges then. What it does *not* support is
  treating two cases' edge hashes as globally distinct without that step.
- Implementation identity is the one gap: it blocks the self-hosting slice,
  not iteration 0, and it interacts with the design summary's claim (§2.3)
  that a function rename is not a meaningful change — which is false once
  the identifier is hashed. A note to the Requirements Engineer accompanies
  that ruling.
