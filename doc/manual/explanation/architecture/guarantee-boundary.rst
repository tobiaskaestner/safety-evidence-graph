What drift detection covers
===========================

affirmatrix detects that content moved by recomputing hashes and comparing them
against what an edge was affirmed against. That mechanism has a boundary, and
the boundary is worth stating plainly before anyone reads a green case as
saying more than it does.

The unit of coverage is the marked span
---------------------------------------

A content hash covers one canonical content form: the bytes of a marked
function's signature and docstring, the bytes of its body, the text of a
requirement. Drift detection recomputes exactly those and compares. So what it
detects is precise and narrow — **the content of a marked span changed since
someone affirmed it**.

It does not follow the call graph. A marked function that delegates to an
unmarked helper is hashed over its own bytes only. Change the helper, leave the
caller alone, and every hash in the graph still matches: the caller's node hash
is unchanged, the edge hash still verifies, and the edge stays active. The
behaviour behind the marked surface moved; the graph did not notice, because
nothing it measures moved.

So a case with no suspect edges says *every marked span still holds the content
it was affirmed against*. It does not say *nothing behind these functions
changed*. Those are different claims, and only the first is mechanical.

What covers the gap today
-------------------------

The test suite. A helper whose behaviour changes breaks the tests of everything
that depends on it, which is ordinary engineering and works as well here as
anywhere. The distinction is one of kind, not of quality: tests are evidence
that the code does what it should, refreshed when someone runs them;
affirmations are evidence that a human accepted a specific binding between a
requirement and specific content, and stay valid until that content moves.
Tests cover the gap without closing it.

The loud case
-------------

One class of shared dependency cannot hide, and it is the one that would matter
most: the encoding primitives underneath the hashes themselves. Change how a
preimage is framed and every hash the engine computes changes at once, so every
recorded edge hash fails to verify and the entire graph goes suspect in a single
recomputation. That is the correct and desirable response — the seal is
defined by that encoding, and a graph sealed under a different one is not
comparable. It is also why the encoding is fixed in a decision record and
pinned by tests that re-derive it independently: it is the one shared
dependency whose drift is maximally visible rather than invisible.

The general shape holds: a change that alters what the hashing *produces* is
caught, loudly. A change that alters behaviour without touching any hashed span
or any hash input is not.

Why this is not closed yet
--------------------------

Three resolutions are plausible, and the repository already carries the
scaffolding for the first: a ``Calls`` edge kind is declared in the vocabulary
and nothing propagates along it.

- Activate propagation along ``Calls``, so suspicion follows the call graph.
- Require transitive marking, so anything a marked function depends on is
  itself marked and hashed.
- Declare an explicit trusted kernel — a named set of code held to a different
  standard of review and exempted deliberately rather than by omission.

Each amends requirement text that is already ratified, and each has costs the
others do not: propagation along ``Calls`` risks marking half the graph suspect
for a change to a logging helper; transitive marking pushes the boundary
outwards until it reaches the standard library; a trusted kernel is only as
good as the discipline that maintains its edges. Choosing between them is
deferred past this iteration as an open design question.

Stating the boundary now is the interim measure. A limitation documented before
the first evidence package exists is a known property of the tool; the same
limitation discovered afterwards, by someone who relied on the wrong reading,
is a defect.
