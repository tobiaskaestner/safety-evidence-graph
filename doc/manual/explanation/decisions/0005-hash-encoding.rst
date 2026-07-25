0005. Hash encoding and domain separation
==========================================

Status
------

Accepted, 2026-07-25.

Context
-------

SEG-SREQ-001, -002, -003 and -005 state *what* each hash is computed from;
none states how the inputs are laid out in the byte string that is hashed.
The prototype concatenated fields as UTF-8 text with no framing, which is
ambiguous — the endpoint pair ``("a", "bc")`` and the pair ``("ab", "c")``
produce the same preimage — and it returned a node's single content hash
unchanged as the node hash, so for a Requirement the content hash *is* the
node hash, and the two are substitutable wherever a node hash is expected.

These choices are irreversible in a way ordinary implementation choices are
not: a computed hash is affirmed by a human and recorded in a ReviewEvent,
and every stored edge hash and every sealed root is invalidated if the
encoding changes afterwards. They must therefore be fixed before the first
hash is computed, and they are integrity mechanics, which AC-013 places
outside configuration.

This ADR fixes only the layout of bytes. Two neighbouring questions are
settled elsewhere and slot in without reopening it. *What* bytes a content
hash covers is each node type's **canonical content form** — for Python
source, the verbatim byte span; for requirements, a form derived from the
needs export — which is a refinement of DEC-003 logged at the
design-of-record level (DEC-031). *Which strings* identify nodes and edges
is ADR-0007; this ADR fixes how such strings are encoded, not what they
are.

Decision
--------

**Notation.** ``uint32be(n)`` is a four-byte big-endian unsigned integer.

.. code-block::

   LP(b)         = uint32be(len(b)) ‖ b               length-prefixed bytes
   SEQ(x1..xn)   = uint32be(n) ‖ LP(x1) ‖ … ‖ LP(xn)  counted sequence
   U(s)          = the UTF-8 bytes of s exactly as recorded

**(i) Framing is length-prefix, not delimiter.** Every variable-length
field entering a preimage is length-prefixed; variable-arity sequences are
additionally count-prefixed. A delimiter would require escaping, and an
escaping rule is a second thing to get right forever. The width — 32 bits —
is arbitrary but fixed: no hashed field approaches four gigabytes.

**(ii) Three domain tags; content hashes are deliberately untagged.**

============================  ============================================
Tag (ASCII)                   Applies to
============================  ============================================
``affirmatrix/v1/node``       node-hash derivation (SEG-SREQ-005)
``affirmatrix/v1/edge``       the two-sided edge hash (SEG-SREQ-002)
``affirmatrix/v1/root``       the flat-sealed design root (SEG-SREQ-003)
============================  ============================================

The tag is length-prefixed and leads the preimage, so the hash state
diverges from the first block and no digest computed for one purpose can be
reinterpreted as another. The ``v1`` segment makes the tag the encoding
version: a future change to this ADR mints new tags rather than silently
re-hashing the same inputs.

A **content hash is the bare SHA-256 of the canonical content form** — no
tag, no framing. This buys a real property: an auditor can reproduce any
content hash by running ``sha256sum`` over the extracted form with standard
tools, with no knowledge of affirmatrix's encoding. Safety is not lost,
because every consumer of a content hash frames it under a tag before
hashing again.

**(iii) The node fold binds type and field names, and is uniform at
n = 1.**

.. code-block::

   contentHash(form) = SHA256(form)

   field(name, c)    = LP(U(name)) ‖ LP(c)

   nodeHash(type, F) = SHA256( LP("affirmatrix/v1/node")
                               ‖ LP(U(type))
                               ‖ SEQ( field(n, c) for (n, c) in F
                                      ordered by U(n) ascending ) )

``type`` is the node's **local type token** (ADR-0007) — ``Requirement``,
``Implementation``, ``TestSpecification``, ``TestOutcome``, ``Waiver`` —
and ``F`` is the set of ⟨content-hash field name, raw digest⟩ pairs for the
forms that node covers. A single-span node is ``SEQ`` with n = 1, not its
own digest; that uniformity is what closes the substitution the prototype
allowed.

The pairs are ordered by **field name, ascending byte-wise** — not by a
taxonomy-declared order. With the names in the preimage, order carries no
semantic weight, and sorting makes the node hash reproducible from the
record's own pairs alone, without consulting the taxonomy provider's
declaration order. This is the same instinct as the untagged content hash:
a verifier should need as little of our machinery as possible.

The **taxonomy provider (AC-001) owns the type token and the field-name
set**; it no longer needs to own an ordering. Because both are now hashed,
the vocabulary's *spelling* is integrity-relevant: renaming a node type or
a content-hash field changes every affected node hash. That is precisely
AC-013's "parameterized only by the declared vocabulary", and it means
vocabulary spelling changes are affirmation events, not refactors.

**(iv) Digests enter preimages as raw 32 bytes; hex is a serialization
concern.** One canonical internal form removes case and encoding questions
from the integrity path entirely. Lowercase hex appears only where records
are written, and ``records`` owns that conversion. A useful consequence:
ascending byte-wise order over raw digests and lexicographic order over
lowercase hex are the same order, so (v) is unambiguous however a reader
pictures it.

**(v) Canonical sort keys.**

.. code-block::

   edgeTuple(e) = LP(U(e.from)) ‖ LP(U(e.to)) ‖ LP(U(e.type))

   edgeHash(e, hFrom, hTo)
       = SHA256( LP("affirmatrix/v1/edge") ‖ edgeTuple(e)
                 ‖ LP(hFrom) ‖ LP(hTo) )

   designRoot(metadata, N, E)
       = SHA256( LP("affirmatrix/v1/root") ‖ LP(metadata)
                 ‖ SEQ(sorted(nodeHash(n) for n in N))
                 ‖ SEQ(sorted(edgeTuple(e) for e in E)) )

- ``e.from``, ``e.to`` are case-local stable identifiers and ``e.type`` is
  the local edge-type token (ADR-0007).
- Node hashes sort **ascending byte-wise over the raw digests**, and
  **duplicates are preserved** — the design set is a multiset. Binding the
  type and field names removes the cross-type collision the earlier draft
  accepted (a Requirement and a Waiver with byte-identical content now
  differ), but two nodes *of the same type* with byte-identical content
  still share a node hash, and both must count in the root. Sorting must
  therefore never deduplicate.
- Edge tuples are framed first and the resulting **byte strings** are
  sorted ascending. Sorting the framed bytes rather than comparing fields
  pairwise is one rule instead of three and is immune to any collation
  question. It orders shorter fields before longer ones irrespective of
  content, which is arbitrary but fixed.
- ``metadata`` is the caller-supplied opaque byte string of ADR-0003. The
  commitment layer length-prefixes it and hashes it; it does not
  canonicalize, parse, or validate it. Metadata leads the preimage, as in
  the design summary §7.3.
- ``E`` and ``N`` are the design set only — ``refines``, ``verifies``,
  ``implements`` and the nodes they connect (DEC-012/014).

**(vi) SHA-256 is fixed, not injected.** There is no algorithm parameter,
no pluggable hasher, and no configuration reaching any function in this
ADR (AC-013). Cryptographic agility, if ever needed, arrives as a new
domain-tag version through a superseding ADR — never as a runtime option.

**Identifier encoding.** Identifiers and type tokens enter preimages as
``U(·)``: UTF-8 bytes **exactly as recorded, with no normalization**.
Normalizing an identity string would be a second transformation of the
thing being identified, against the same instinct that keeps the parser a
locator and never a hash input.

Consequences
------------

- ``affirmatrix._hashing`` implements ``LP``, ``SEQ``, ``U`` and the four
  hash functions above and is the only module in the engine that calls
  ``hashlib``. An import rule enforces this.
- Every hash here is reproducible from this specification alone, with no
  reference to affirmatrix's source — what AC-016's
  independent-verifiability invariant requires of the root.
- SEG-SREQ-005's "solely from the content hashes" is amended by the
  Requirements Engineer to admit the node type and the field names. The
  domain tag and the framing remain constants of the derivation function
  rather than inputs to it.
- Node-type and content-hash-field names are now part of the integrity
  surface: renaming either is an affirmation event affecting every node of
  that type.
- Content hashes remain reproducible with ``sha256sum``; node, edge and
  root hashes are not, by design.
- ``pending`` and ``broken`` edges have no stored edge hash to compare
  against; the suspect detector must treat the absence of a stored hash as
  a state, not as a mismatch.
