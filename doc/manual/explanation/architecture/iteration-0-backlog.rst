Iteration-0 backlog
===================

Scope is whatever this backlog says — nothing more. There is no standing
"deferred features" list: anything not below is out of scope by definition, and
work that surfaces a gap becomes a note to the Requirements Engineer rather
than code.

Iteration 0 builds the engine core against the would-be store and closes when
its own pytest suite is green and the three workflows — consistency, proof
generation, suspect detection — run end to end on that store. "No proof" means
no *self*-proof: proof generation is built and exercised, the tool is simply
not yet the subject of its own graph.

Working rules
-------------

- **Requirements lead code.** Every item below names the requirement it
  realizes. An item whose requirement is still in decomposition cites its
  parent system requirement and waits for the leaf.
- **Test first**, per item, following the python-patterns skill.
- Implementation functions carry ``:implements:`` docstring-field markers as
  they are written; ``:verifies:`` markers wait for the Test Engineer's slice
  and are re-pointed together with it.
- Components are named exactly as the component map (ADR-0004) names them,
  because those names are the requirement subjects.

The items
---------

===  =========================================================  ======================  ======================
Id   Work item                                                  Component               Requirement
===  =========================================================  ======================  ======================
B0   Package skeleton, pytest wiring, import-direction lint     — (infrastructure)      —
B1   Canonical byte encoding and the SHA-256 primitive          — (shared internal)     ADR-0005
B2   Node-hash derivation                                       commitment layer        SEG-SREQ-005
B3   Two-sided edge hash                                        commitment layer        SEG-SREQ-002
B4   Flat-sealed design root, caller-supplied metadata          commitment layer        SEG-SREQ-003
B5   Persisted vocabulary and the record-source protocol        record source           SEG-SYS-001/007
B6   The built-in safety-evidence graph type                    taxonomy provider       (SYS home pending)
B7   Records to the in-memory graph                             graph builder           SEG-SYS-001
B8   Refines cycles and self-loops as graph-level errors        graph builder           SEG-SREQ-004
B9   The would-be store dataset and its loader                  store loader            — (scaffolding)
B10  Persist nodes, edges, events, proofs; validate on write    affirmation store       SEG-SYS-007
B11  Read-back as a record source                               affirmation store       SEG-SYS-007
B12  Satisfaction by transitive closure                         satisfaction evaluator  SEG-SYS-002 (batch A)
B13  Link state derived from current content                    suspect detector        SEG-SYS-003 (batch A)
B14  ReviewEvent with the affirmation anchor                    affirmation recorder    SEG-SYS-004
B15  Gate 2, the proof gate, and its CoverageReport             gate evaluator          SEG-SYS-006
B16  Scope collection and the partial-vs-total signal           proof generator         SEG-SYS-005
B17  The four proof documents                                   proof generator         SEG-SYS-005
B18  Refuse to generate for a blocked scope                     proof generator         SEG-SYS-008
B19  Minimal CLI over the three workflows                       command-line interface  (SYS home pending)
B20  Iteration architecture note; notes to the RE               —                       —
===  =========================================================  ======================  ======================

Sequencing
----------

The order above is the dependency order. Three joins are worth stating
explicitly:

- **B1 gates everything.** The byte encoding is irreversible once a hash is
  affirmed, which is why ADR-0005 preceded any code.
- **B11 gates B13.** Drift detection compares two record streams — the
  *recorded* one from the affirmation store and the *current* one from a
  producer — so read-back must exist before suspicion can be derived.
- **The FSM affirms between B14 and B15.** A faithfully bootstrapped store
  starts every edge ``pending``, and ``pending`` blocks proof, so the proof
  gate has nothing to show until a bulk affirmation has been operated by the
  FSM at a checkpoint. Agents never affirm.

Deferred out of iteration 0
---------------------------

- **Record production** — the content extractor, the requirements reader, and
  the outcome extractor. Only the span-hashing primitive lands early. This is
  the first self-hosting slice: it replaces the would-be store and retires the
  manual translation.
- **Gate 1 (commit) and Gate 3 (release).** Gate 1's conditions are all
  extractor conditions, and record production is deferred; Gate 3 needs a
  sealed package and release tags.
- **Implementation node identity**, which blocks the self-hosting slice rather
  than this one.
- **Composition and exchange** — contract vectors, SPDX projection,
  ``flat-openable``, assessor certificates. Not v1 at all; only the
  composition-enabling invariants (AC-016) constrain what is built here.
- **The graph-type meta-model and configurable satisfaction.** v1 has a fixed
  vocabulary and fixed satisfaction; AC-001 and AC-002 keep them behind seams
  so the meta-model plugs in later rather than forcing a rewrite.

Decisions this backlog rests on
-------------------------------

ADR-0003 (commitment layer), ADR-0004 (component map), ADR-0005 (hash
encoding), ADR-0006 (test-tree ownership), ADR-0007 (identifiers), ADR-0008
(write policy); DEC-001 (satisfaction), DEC-003 and DEC-031 (canonical content
form), DEC-005 (derived suspicion), DEC-006 (affirmation anchor), DEC-012 and
DEC-014 (flat-sealed root), DEC-016 (outcome validity), DEC-030 (mono-repo).
