# ============================================================================
# seg_example_v1_plus_composition.dsl — the v1 SEG grammar with cross-project composition
# The v1 Safety Evidence Graph baseline (seg_example_v1_baseline.dsl) AMENDED with cross-project COMPOSITION
# (DEC-010). Purely additive in the File-B sense: two node types, four edges,
# two core-projected EDB relations, an alternative discharge path (reliance),
# and a published-conditions (residual) set. Nothing in v1 is removed or
# weakened — an import-free graph validates and gets byte-identical verdicts
# (conservative-extension invariant, seg_composability_cbd.md §9).
# Status: illustrative surface syntax (final form likely YAML/JSON; see ADR).
# ============================================================================
#
# ---- EDB: the relations the engine injects, in three provenance tiers ----
#
#   1. Graph-extensional (the authored graph; sealed):
#        node(Id, Type)                  one tuple per node
#        edge(EdgeId, Type, From, To)    one tuple per edge; From/To = endpoint identities
#        node_field(NodeId, Name, Value) uniform field accessor (fields declared below)
#
#   2. Core integrity facts (fixed, universal mechanics — AC-013; DEC-005):
#        edge_state(EdgeId, State)       computed suspect-detection state, recomputed
#                                        each run; State in {active, pending,
#                                        directlyOutdated, transitivelySuspect,
#                                        doublyOutdated, broken}
#        seal_ok(ManifestId)             NEW. Core-recomputed each run: the upstream
#                                        manifest's Merkle recompute + authenticity check
#                                        succeed. Parallel to edge_state — an integrity
#                                        primitive, not stored content. (Authenticity half
#                                        = the deferred signed-external-projection corner,
#                                        seg_adr_projection_core.md §8; stubbed for now.)
#        referenced_under(NodeId, ManifestId)  NEW. Core-projected per-node provenance: this
#                                        node is an upstream node embedded BY REFERENCE (IRI +
#                                        content hash), and its seal is the named Manifest.
#                                        Surfaced from the node's source binding (DEC-009).
#                                        The seal lookup is node-anchored — `covers` carries
#                                        no manifest reference; it is reached via this fact.
#
#   3. Context (facts about the evaluation environment, not the graph):
#        eval_time(T)                    the SEALED evaluation timestamp (pinned in proof)
#        authorised_fsm(Id)              approver ids valid in the FSM authorised-committers config
#
# ---- Verdict purity invariant (unchanged) ----
# A SEALED verdict (`satisfied`, `residual`, ...) may depend only on graph-extensional
# facts, the core integrity primitives (`edge_state`, `seal_ok`, `referenced_under`), and
# SEALED context. No unsealed input may sit upstream of a sealed verdict.
# Report-only / validation predicates may read anything.
#
# ---- The `deep` retirement (DEC-012) reflected here ----
# `fingerprint: deep` is RETIRED. Every committed design edge below is `flat-sealed`
# (member of the flat set-commitment over the design graph). Because `deep => acyclic`
# no longer holds, the DAG constraint that satisfaction/well-foundedness needs is now
# declared EXPLICITLY as `acyclic: true` on the structural edges that feed the verdict
# recursion (`refines`, `covers`, `assumes`). The joint acyclicity invariant
# (seg_definition_language.md §6 inv. 2) ranges over THIS explicitly-acyclic union, not
# the (now empty) deep union. NOTE (DEC-017 §2a): `covers` enters the union read in its
# dependant->dependee orientation `R -> G` (R's discharge depends on G), NOT its surface
# direction `G -> R`; the dependency graph is identical to the old `relies_on(R,G)` form.
# ============================================================================

namespace "https://zephyrproject.org/seg/zephyr-rtos#"

repo RequirementsRepo { role: source; }     # repo A
repo CodeRepo         { role: source; }     # repo B (impl + test specs)
repo EvidenceRepo     { role: source; }     # repo C (raw outcomes)
repo GraphStore       { role: store; }      # repo G (graph + waivers + imported manifests)

# ---- Node types (the v1 five, unchanged) ----
node Requirement {
    source_in:   RequirementsRepo;
    identity:    id;
    hash_fields: [ text ];
    # NOTE: a Requirement INSTANCE may instead be embedded by reference — an upstream
    # condition-of-use C reached via a sealed `assumes`. Such instances carry a
    # by-reference source binding and surface as `referenced_under(id, M)`. The TYPE is
    # unchanged (a condition of use is an ordinary Requirement). The upstream guarantee
    # G_up is NO LONGER an ordinary Requirement — it is the distinct `Guarantee` type
    # below (DEC-017), so the satisfaction recursion never ranges over it.
}
node TestSpecification {
    source_in:   CodeRepo;
    identity:    ts_id;
    hash_fields: [ intent, body ];            # specHash + implHash
}
node Implementation {
    source_in:   CodeRepo;
    identity:    symbol;
    hash_fields: [ api, body ];               # apiHash + bodyHash
}
node TestOutcome {
    source_in:   EvidenceRepo;
    identity:    outcome_id;
    hash_fields: [ result, ran_against_sha ]; # PASS/FAIL + the CodeRepo commit it ran against
}
node Waiver {
    source_in:   GraphStore;
    identity:    waiver_id;
    hash_fields: [ reason, approver, expiry ];
}

# ---- Node types added by COMPOSITION ----
node DesignReview {                           # NEW: the second Witness species (alongside
    source_in:   RequirementsRepo;            #      TestOutcome). A human-authored review/
    identity:    review_id;                   #      analysis with a body. Discharges a
    hash_fields: [ scope, body ];             #      Requirement by authorship (mode 1).
}                                             #      Drift in its content re-suspects.
node Manifest {                               # NEW: the upstream SEALED proof, embedded by
    source_in:   GraphStore;                  #      reference (evidence side). Owns the
    identity:    manifest_id;                 #      shared recomputed facts; the verification
    hash_fields: [ component_iri, version, digest ]; # backing for any reliance pointing at it.
    # `seal_ok(manifest_id)` is core-recomputed (see EDB), NOT a stored field.
    # component_iri = stable component identity (the version-consistency join key,
    # distinct from version). A re-seal changes `digest` => this node's hash =>
    # every reliance referencing it re-suspects, in one place.
}
node Guarantee {                              # NEW (DEC-017): the imported upstream guarantee G_up,
    source_in:   RequirementsRepo;            #      embedded BY REFERENCE (IRI + content hash, attested
    identity:    id;                          #      by the Manifest). A DISTINCT type so the satisfaction
    hash_fields: [ text ];                    #      recursion (headed by Requirement) never ranges over it;
                                              #      surfaces as referenced_under(id, M), sits design-side.
    # TO BE REVISED (DEC-017, deferred): `source_in` and `hash_fields` are provisional —
    # left as Requirement's bindings for now; the by-reference binding may argue otherwise.
}

# ---- Edge types (the v1 six; fingerprint deep -> flat-sealed per DEC-012) ----
edge refines {                                # child -> parent
    from:        Requirement;
    to:          Requirement;
    binds:       true;
    propagates:  true;
    fingerprint: flat-sealed;
    acyclic:     true;                        # was entailed by deep; now declared explicitly
}
edge verifies {
    from:        TestSpecification;
    to:          Requirement;
    binds:       true;
    propagates:  true;
    fingerprint: flat-sealed;
}
edge implements {
    from:        Implementation;
    to:          Requirement;
    binds:       true;
    propagates:  true;
    fingerprint: flat-sealed;
}
edge confirms {
    from:        TestOutcome;
    to:          TestSpecification;
    binds:       false;
    propagates:  false;
    fingerprint: none;
}
edge witnesses {
    from:        TestOutcome;
    to:          Implementation;
    binds:       false;
    propagates:  false;
    fingerprint: none;
}
edge excuses {
    from:        Waiver;
    to:          TestOutcome;
    binds:       false;
    propagates:  false;
    fingerprint: none;
}

# ---- Edge types added by COMPOSITION ----
edge reviews {                                # NEW: a DesignReview discharges a Requirement
    from:        DesignReview;                #      (mode-1 witness). Affirming the edge IS
    to:          Requirement;                 #      the discharge — a review has no pass/fail.
    binds:       true;
    propagates:  true;
    fingerprint: flat-sealed;
}
edge covers {                                 # NEW (DEC-017): an upstream Guarantee G_up COVERS a
    from:        Guarantee;                    #      downstream Requirement (mode-2). THE single human
    to:          Requirement;                  #      act: affirming this edge = affirming the
    binds:       true;                         #      refinement "G_up covers my need".
    propagates:  true;                         #      Replaces relies_on (which was R -> G_up).
    fingerprint: flat-sealed;
    acyclic:     true;                         # joins the acyclic union read R -> G (DEC-017 §2a)
    # Pure binary G_up -> R. The seal backing is NODE-anchored: the engine reaches the
    # Manifest via G_up's source binding (referenced_under), not via an edge field.
}
edge assumes {                                # NEW: SEALED upstream structure — G_up assumes
    from:        Requirement | Guarantee;     #      condition-of-use C. Source is Guarantee upstream
    to:          Requirement;                 #      (G_up), Requirement for the product's OWN published
    binds:       false;                       #      conditions (local authored A_up). Lives in the
    propagates:  false;                       #      upstream graph, embedded by reference; integrity
    fingerprint: none;                         #      comes from the manifest seal, NOT a downstream
    acyclic:     true;                         #      affirmation. `acyclic` only for recursion termination.
}
edge uses {                                   # NEW: impl-uses-impl — a downstream Implementation
    from:        Implementation;              #      links the upstream component the seal is
    to:          Manifest;                    #      about. Extracted from the build, not
    binds:       true;                        #      affirmed. The Manifest is the downstream
    propagates:  false;                       #      graph's representative of the one linked
    fingerprint: none;                        #      upstream implementation.
}

edb { node/2, edge/4, node_field/3,
      edge_state/2, seal_ok/1, referenced_under/2,
      eval_time/1, authorised_fsm/1 }

rules {
    # --- terseness helper: an edge that is currently active ---
    active_edge(E, T, F, To) :- edge(E, T, F, To), edge_state(E, "active").

    # --- requirement shape (BASE) ---
    is_parent(R) :- edge(_, "refines", _, R).
    leaf(R)      :- node(R, "Requirement"), not is_parent(R).

    has_active_verifies(R)   :- active_edge(_, "verifies",   _, R).
    has_active_implements(R) :- active_edge(_, "implements", _, R).

    # --- a test spec's outcome is OK (BASE) ---
    spec_ok(TS) :- active_edge(_, "confirms", O, TS), node_field(O, "result", "PASS").
    spec_ok(TS) :- active_edge(_, "confirms", O, TS), node_field(O, "result", "FAIL"),
                   active_edge(_, "excuses", W, O), waiver_valid(W).

    waiver_valid(W) :- node(W, "Waiver"),
                       node_field(W, "expiry",   Exp), eval_time(Now), before(Now, Exp),
                       node_field(W, "approver", App), authorised_fsm(App).

    has_unmet_spec(R) :- active_edge(_, "verifies", TS, R), not spec_ok(TS).

    # ========================================================================
    # COMPOSITION (all NEW; each predicate is empty on an import-free graph)
    # ========================================================================

    # --- mode-1, second kind of witness: a DesignReview discharges by authorship ---
    discharged_by_review(R) :- active_edge(_, "reviews", _, R).

    # --- mode-2 reliance: the four conditions of seg_composability_cbd.md §8 ---
    # (i)  refinement affirmed  == the covers edge is active:
    covered(R)          :- active_edge(_, "covers", _, R).
    # the seal backing is NODE-anchored: reach the Manifest via G_up's source binding.
    referenced(N)       :- referenced_under(N, _).                            # boolean, for residual
    reliance_seal_ok(R) :- active_edge(_, "covers", Gup, R),
                           referenced_under(Gup, M), seal_ok(M).              # (iv) seal verifies
    impl_uses(M)        :- active_edge(_, "uses", _, M).
    reliance_uses_ok(R) :- active_edge(_, "covers", Gup, R),
                           referenced_under(Gup, M), impl_uses(M).            # (iii) impl-uses-impl

    # --- residual = the product's OWN authored conditions, published as A_up (DEC-015) ---
    # An `assumes` edge whose SOURCE guarantee is local (not referenced) declares a
    # condition of use the product ships rather than discharges. It is exempt from the
    # leaf failure rules (it is the safety manual, not a gap) and reported as residual.
    residual(C) :- edge(_, "assumes", G, C), not referenced(G).

    # --- alternative-discharge exemption (drives the guard on the leaf rules below) ---
    # A leaf needs LOCAL verifies+implements only when it is not otherwise discharged.
    discharged_otherwise(R) :- discharged_by_review(R).   # reviewed
    discharged_otherwise(R) :- covered(R).                # relied upon (good or broken; broken
                                                          # fails via the reliance clauses below)
    discharged_otherwise(R) :- residual(R).               # published condition of use (A_up)

    # ========================================================================
    # FAILURE PROPAGATED UPWARD (positive recursion in `unsatisfied`; the only
    # negations point DOWN to lower strata — so the whole program stays in the
    # syntactically-stratified fragment, Soufflé and clingo alike).
    # ========================================================================

    # BASE leaf rules — the ONLY base clauses touched: an inert guard
    # `not discharged_otherwise(R)` is added. On an import-free graph
    # `discharged_otherwise` is empty, so the guard is vacuously true and these
    # behave byte-identically to the baseline grammar (conservative extension).
    unsatisfied(R) :- leaf(R), not has_active_verifies(R),   not discharged_otherwise(R).
    unsatisfied(R) :- leaf(R), not has_active_implements(R), not discharged_otherwise(R).

    # BASE (unchanged): enforce-if-present, refines propagation, suspect decomposition
    unsatisfied(R) :- node(R, "Requirement"), has_unmet_spec(R).
    unsatisfied(R) :- is_parent(R), active_edge(_, "refines", C, R), unsatisfied(C).
    unsatisfied(R) :- is_parent(R), edge(E, "refines", _, R), not edge_state(E, "active").

    # NEW: a present reliance that is not GOOD makes its requirement unsatisfied
    # (DEC-015 — a broken/incomplete reliance is a defect here, never a residual).
    unsatisfied(R) :- covered(R), not reliance_seal_ok(R).         # (iv) seal absent/failed
    unsatisfied(R) :- covered(R), not reliance_uses_ok(R).         # (iii) upstream impl not linked
    # (ii) every SEALED condition discharged — dualized to the positive form so no
    #      negation enters the recursion: a not-yet-discharged sealed condition poisons R.
    unsatisfied(R) :- active_edge(_, "covers", Gup, R),
                      edge(_, "assumes", Gup, C), unsatisfied(C).

    # --- verdict (queried over the in-scope / product requirements) ---
    satisfied(R) :- node(R, "Requirement"), not unsatisfied(R).

    # ========================================================================
    # REPORT-ONLY / VALIDATION (never upstream of a sealed verdict)
    # ========================================================================

    # Three-state proof verdict (proof scope), over the PRODUCT (in-scope) requirements.
    # Concretely exercised in seg_demo_clingo_partial_discharge.py.
    #   total       — non-empty scope, no in-scope gap, nothing published as A_up
    #   conditional — no in-scope gap, but some residual published as A_up
    #   unsatisfied — some in-scope requirement is unsatisfied (a genuine gap)
    product(R)         :- node(R, "Requirement"), not referenced(R).
    has_product        :- product(_).
    proof_unsatisfied  :- product(R), unsatisfied(R).
    proof_has_residual :- residual(_).
    # `has_product` stops a vacuous "total" on an empty / all-referenced graph.
    proof_total        :- has_product, not proof_unsatisfied, not proof_has_residual.
    proof_conditional  :- not proof_unsatisfied, proof_has_residual.

    # VALIDATION (structural well-formedness; SHACL/structural pass in the real pipeline):
    # at most one Manifest per upstream component identity ("one upstream impl only").
    manifest_conflict(Iri) :- node(M1, "Manifest"), node_field(M1, "component_iri", Iri),
                              node(M2, "Manifest"), node_field(M2, "component_iri", Iri),
                              M1 != M2.
    # a requirement is decomposed locally OR relied upon — not both.
    ill_formed_reliance(R) :- covered(R), is_parent(R).
}
