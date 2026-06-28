# ============================================================================
# File B — seg_example_v1_plus_adr.dsl
# The v1 Safety Evidence Graph (File A) AMENDED with Architectural Decision
# Records. Purely additive: one node type, two edges, one extra failure mode,
# one report-only signal. Nothing in v1 is removed or weakened — a requirement
# must still be implemented AND tested AND its outcomes pass/waived, and now
# ADDITIONALLY must not violate an applicable architectural decision.
# Status: illustrative surface syntax (final form likely YAML/JSON; see ADR).
# ============================================================================
#
# ---- EDB: the relations the engine injects, in three provenance tiers ----
#
#   1. Graph-extensional (the authored graph; sealed):
#        node(Id, Type)                  one tuple per node
#        edge(EdgeId, Type, From, To)    one tuple per edge; From/To = endpoint identities
#        node_field(NodeId, Name, Value) uniform field accessor (fields declared below)
#        edge_field(EdgeId, Name, Value) symmetric; for payload edges (unused here)
#
#   2. Core integrity fact (the one fixed, universal mechanic — AC-013; DEC-005):
#        edge_state(EdgeId, State)       computed suspect-detection state, recomputed
#                                        each run; State in {active, pending,
#                                        directlyOutdated, transitivelySuspect,
#                                        doublyOutdated, broken}
#
#   3. Context (facts about the evaluation environment, not the graph):
#        eval_time(T)                    the SEALED evaluation timestamp (pinned in proof)
#        authorised_fsm(Id)              approver ids valid in the FSM authorised-committers config
#
# Fields are read directly via node_field / edge_field — there is no projection
# sublanguage. Built-in comparisons (e.g. before/2) are range-restricted filters.
#
# ---- Verdict purity invariant ----
# A SEALED verdict (`satisfied`, ...) may depend only on graph-extensional facts,
# `edge_state`, and SEALED context. No unsealed input — a `tracked` field (such as
# ADR `status`) or live context — may sit upstream of a sealed verdict, or it would
# not be reproducible from the proof alone. Report-only predicates may read anything.
# The ADR `status` below is `tracked`, so it appears ONLY in the report-only
# `adr_pending`, never in `satisfied`.
# ============================================================================

namespace "https://zephyrproject.org/seg/zephyr-rtos#"

repo RequirementsRepo { role: source; }     # repo A
repo CodeRepo         { role: source; }     # repo B (impl + test specs)
repo EvidenceRepo     { role: source; }     # repo C (raw outcomes)
repo GraphStore       { role: store; }      # repo G (graph + waivers)

# ---- Node types (the v1 five, unchanged) ----
node Requirement {
    source_in:   RequirementsRepo;
    identity:    id;
    hash_fields: [ text ];
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
    # freshness: the core compares ran_against_sha to CodeRepo HEAD and reflects
    # staleness by holding this outcome's confirms/witnesses edges non-active.
    # OPEN (per-type facet): freshness as this committed pin, or a `witnesses` edgeHash bind?
}
node Waiver {
    source_in:   GraphStore;
    identity:    waiver_id;
    hash_fields: [ reason, approver, expiry ];
}

# ---- Node type added by the ADR extension ----
node ArchitecturalDecisionRecord {
    source_in:   RequirementsRepo;
    identity:    adr_id;
    hash_fields: [ title, decision_body ];    # committed content
    tracked:     [ status ];                  # carried/queryable lifecycle field;
                                              # NOT committed, NOT a sealed-verdict input
}

# ---- Edge types (the v1 seven, unchanged) ----
edge refines {                                # child -> parent; in design commitment; acyclic declared (satisfaction recursion)
    from:        Requirement;
    to:          Requirement;
    binds:       true;
    propagates:  true;
    fingerprint: flat-sealed;
    acyclic:     true;
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

# ---- Edge types added by the ADR extension ----
edge answers_to {                             # an ADR answers a requirement
    from:        ArchitecturalDecisionRecord;
    to:          Requirement;
    binds:       true;
    propagates:  true;
    fingerprint: flat-sealed;
}
edge adheres_to {                             # an implementation adheres to an ADR
    from:        Implementation;
    to:          ArchitecturalDecisionRecord;
    binds:       true;
    propagates:  true;
    fingerprint: flat-sealed;
}

edb { node/2, edge/4, node_field/3, edge_state/2, eval_time/1, authorised_fsm/1 }

rules {
    # --- terseness helper: an edge that is currently active ---
    active_edge(E, T, F, To) :- edge(E, T, F, To), edge_state(E, "active").

    # --- requirement shape ---
    is_parent(R) :- edge(_, "refines", _, R).
    leaf(R)      :- node(R, "Requirement"), not is_parent(R).

    has_active_verifies(R)   :- active_edge(_, "verifies",   _, R).
    has_active_implements(R) :- active_edge(_, "implements", _, R).

    # --- a test spec's outcome is OK: a passing confirm, or a failing one validly waived ---
    spec_ok(TS) :- active_edge(_, "confirms", O, TS), node_field(O, "result", "PASS").
    spec_ok(TS) :- active_edge(_, "confirms", O, TS), node_field(O, "result", "FAIL"),
                   active_edge(_, "excuses", W, O), waiver_valid(W).

    # --- a waiver is valid: unexpired vs the SEALED eval_time, approved by an authorised FSM ---
    waiver_valid(W) :- node(W, "Waiver"),
                       node_field(W, "expiry",   Exp), eval_time(Now), before(Now, Exp),
                       node_field(W, "approver", App), authorised_fsm(App).

    # a verified spec whose outcome is not OK (failing, missing, or stale)
    has_unmet_spec(R) :- active_edge(_, "verifies", TS, R), not spec_ok(TS).

    # --- ADR adherence (the extension's contribution) ---
    impl_adheres_to_adr(Impl, ADR) :- active_edge(_, "adheres_to", Impl, ADR).

    # an applicable ADR (one that answers R) that an implementation of R does NOT adhere to
    impl_violates_adr(Impl, R) :- active_edge(_, "implements", Impl, R),
                                  active_edge(_, "answers_to", ADR, R),
                                  not impl_adheres_to_adr(Impl, ADR).

    has_adr_violation(R) :- impl_violates_adr(_, R).

    # --- failure propagated UPWARD (positive recursion; the only negation is at `satisfied`) ---
    unsatisfied(R) :- leaf(R), not has_active_verifies(R).
    unsatisfied(R) :- leaf(R), not has_active_implements(R).
    unsatisfied(R) :- node(R, "Requirement"), has_unmet_spec(R).                  # enforce-if-present
    unsatisfied(R) :- node(R, "Requirement"), has_adr_violation(R).               # ADDED: ADR failure mode
    unsatisfied(R) :- is_parent(R), active_edge(_, "refines", C, R), unsatisfied(C).
    unsatisfied(R) :- is_parent(R), edge(E, "refines", _, R), not edge_state(E, "active").  # suspect decomposition

    # --- verdict (queried over the in-scope requirements) ---
    satisfied(R) :- node(R, "Requirement"), not unsatisfied(R).

    # --- REPORT-ONLY: reads the tracked `status`; never upstream of `satisfied` ---
    # "an applicable ADR for this requirement is still only proposed"
    adr_pending(R) :- active_edge(_, "answers_to", ADR, R), node_field(ADR, "status", "proposed").
}
