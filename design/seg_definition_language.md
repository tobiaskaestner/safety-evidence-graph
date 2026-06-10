# SEG — Definition Language (grammar sketch & compilation model)

**Status:** Working sketch. Surface syntax shown is illustrative (final form likely a
structured data format — YAML/JSON — not a bespoke parser; see ADR). What is
*decided* is the field model, the facet model, the compilation targets, and the
static invariants below.

**Related:** `seg_adr_projection_core.md` (the projection-core stance this extends to
the schema layer), `seg_glossary.md`, `seg_prior_art.md`, `seg_reconciliation.md`.

---

## 1. What the definition is

A graph-type definition declares the *vocabulary and bindings* the fixed integrity
mechanics operate over: a namespace, the source/store/evidence repos, the node types
(with their field model), the edge types (with their facets), the projected input
relations (`edb`), and a stratified-Datalog `rules` block for verdicts. It is
trusted-base and proof-bound. Satisfaction is **not** free code — it is the stratified
ruleset (DEC-007).

The definition is itself *projected* (transpiled) to three back-ends — this is the
projection-core stance applied one level up, to the schema:

- **SHACL** shapes — structural well-formedness.
- **Stratified Datalog** program — verdicts (satisfaction, suspicion).
- **Core / commitment config** — hashing, drift, fingerprint membership.

## 2. Worked example (the refined ADR/Requirement/Implementation fragment)

```
namespace "https://zephyrproject.org/seg/zephyr-rtos#"

repo RequirementsRepo { role: source }
repo CodeRepo         { role: source }
repo EvidenceRepo     { role: evidence }
repo GraphStore       { role: store }

node Requirement {
    source_in:   RequirementsRepo
    identity:    id                       # IRI local-part; stable; NOT hashed
    hash_fields: [ text, rationale ]      # committed content; change = drift
}
node ArchitecturalDecisionRecord {
    source_in:   RequirementsRepo
    identity:    adr_id
    hash_fields: [ title, decision_body ] # committed content
    tracked:     [ status ]               # carried/queryable; NOT committed; NOT verdict input
}
node Implementation {
    source_in:   CodeRepo
    identity:    symbol
    hash_fields: [ file_span ]
}

# All three design relations are committed: the proof must attest that this ADR /
# implementation was affirmed against this requirement's / ADR's hashed content.
edge answers_to {
    from: ArchitecturalDecisionRecord  to: Requirement
    binds: true   propagates: true   fingerprint: flat-sealed
}
edge implements {
    from: Implementation  to: Requirement
    binds: true   propagates: true   fingerprint: flat-sealed
}
edge adheres_to {
    from: Implementation  to: ArchitecturalDecisionRecord
    binds: true   propagates: true   fingerprint: flat-sealed
}

edb { node/2, edge/4, link_state/2, status/2 }   # relations PROJECTED from the core

rules {
    impl_adheres_to_adr(Impl, ADR) :-
        edge(E, "adheres_to", Impl, ADR), link_state(E, "active").

    # an applicable ADR this impl does NOT adhere to is a violation
    impl_violates_adr(Impl, Req) :-
        edge(E1, "implements", Impl, Req), link_state(E1, "active"),
        edge(E2, "answers_to", ADR, Req),  link_state(E2, "active"),
        not impl_adheres_to_adr(Impl, ADR).

    has_active_impl(Req) :-
        edge(E, "implements", Impl, Req), link_state(E, "active").

    some_impl_violates(Req) :- impl_violates_adr(_, Req).

    # UNIVERSAL reading: implemented AND no implementation violates an applicable ADR.
    # Reads only committed-content relations -> verdict is reproducible from the proof.
    satisfied(Req) :-
        node(Req, "Requirement"),
        has_active_impl(Req),
        not some_impl_violates(Req).

    # REPORT-ONLY: may read tracked status; MUST NOT feed `satisfied` (static invariant 3).
    adr_pending(Req) :-
        edge(E, "answers_to", ADR, Req), link_state(E, "active"),
        status(ADR, "proposed").
}
```

## 3. The field model (three roles)

Every node field has exactly one role, decided by *what a change to it does*:

| Role | A change means… | Hashed? | In commitment? | Verdict input? |
|---|---|---|---|---|
| `identity` | a *different node* | no | no (it *is* the IRI local-part) | as the node id only |
| `hash_fields` | **drift** (suspect + moves design root) | yes | yes | yes (committed) |
| `tracked` | lifecycle/metadata; *not* drift | no | no | **no** (report-only) |

`identity` is stable and never hashed (content drifts, identity does not).
`hash_fields` is what the proof attests. `tracked` (e.g. ADR `status`) is real data the
graph carries and may be queried/shape-checked, but is outside the commitment and
outside any sealed verdict.

## 4. The facet model (per edge type)

`strong` is retired; edge types carry explicit facets:

| Facet | Values | Compiles to | Meaning |
|---|---|---|---|
| `from` / `to` | node types | SHACL + Datalog | domain/range typing |
| `binds` | bool | core/commitment | stores `edgeHash` at affirmation; drift-detected |
| `propagates` | bool | Datalog | suspicion flows along the edge |
| `fingerprint` | `none` / `flat-sealed` / `flat-openable` / `deep` (retired) | core/commitment | design-root membership & mode |
| `acyclic` | (entailed) | SHACL-SPARQL / structural pass | DAG constraint — see §6 |

`fingerprint` is decided by one question only: **must the proof attest this
relationship was affirmed against these specific contents?** If yes → `flat-sealed`
(or `flat-openable` when individual members must later be opened for selective
disclosure; `deep` is retired, DEC-012). It is *not* a "backbone vs evidence"
judgement. *Note (DEC-013, DEC-014):* the configurable per-edge `fingerprint` facet
is outside the v1 self-hosting slice — v1 integrity is `edgeHash` (local) + a
`flat-sealed` design root over the fixed design set (global); `flat-openable` and
`deep` defer to the composability phase. The model still defines `fingerprint` so
Phase C can express it.

## 5. Compilation routing (four-way)

One parse tree, multiple emitters. Each declaration routes to a subset of back-ends:

| Declaration | SHACL | Datalog | Core/commitment |
|---|---|---|---|
| `namespace` | IRI base | constant scope | identifier scope |
| node `identity` | present + unique | node id in facts | IRI local-part (unhashed) |
| node `hash_fields` | datatype/presence shape | available as committed facts | folded into `nodeHash` |
| node `tracked` | shape (e.g. `status` enum) | projected as edb (e.g. `status/2`) | — (ignored) |
| edge `from`/`to` | property shape (`sh:class`) | relation schema | — |
| edge `binds` | — | — | store + drift-check `edgeHash` |
| edge `propagates` | — | suspicion rules | — |
| edge `fingerprint` | — | — | design-root membership + mode |
| `rules` | — | the program | — |

This is why "transpiler" really means *three emitters over one parse tree*. The `edb`
block is the contract that keeps the Datalog emitter honest about what it may assume
exists.

## 6. Static invariants (compile-time, fail-loud)

SEG's soundness rests on a small set of *static* checks over the definition + ruleset,
all decidable before anything runs. The transpiler must enforce all of them:

1. **Field-routing totality & exclusivity.** For each node type,
   `identity ∪ hash_fields ∪ tracked` equals its full field set, pairwise disjoint.
   A field in two roles ("changing it is and isn't drift") is a contradiction → error.
2. **Declared-acyclicity.** The union of all edge types declared `acyclic` (in the
   built-in model: `refines`, for satisfaction soundness) must induce a DAG — checked
   *jointly over the union*, not per edge type (a per-edge check would miss a
   cross-type cycle). The operative entailment is `satisfaction-role ⟹ acyclic`. The
   `fingerprint:deep ⟹ acyclic` entailment is **dormant** while `deep` is retired
   (DEC-012); it would re-add the deep-fingerprint union to this check if a `deep`
   edge type were reintroduced.
3. **Verdict purity (reproducibility).** No sealed verdict predicate (`satisfied`, …)
   may transitively depend on any `tracked`-derived edb relation. Tracked relations may
   be *queried* by report-only predicates, but must not sit upstream of a sealed
   verdict. This is what keeps the verdict a pure function of committed content +
   sealed evidence, hence reproducible from the proof by any verifier.
4. **Verdict determinism.** The satisfaction + suspicion program must yield *exactly
   one* answer set on well-formed (acyclic) input. Partly guaranteed statically (the
   program stays in the stratified fragment) and asserted at evaluation by the
   single-answer-set guardrail (demonstrated on clingo: a refines cycle produces two
   answer sets and trips the guard).

These four are the same *kind* of artifact: static, fail-loud guarantees that move
soundness questions to compile time. The trusted core is this handful of checks, not
the engines.

## 7. Verdict reproducibility (the sealed-vs-live decision)

**Decision:** `satisfied` (and any sealed verdict) is a *pure function of committed
content + sealed evidence*. `tracked` fields are query/report-only and never upstream
of a verdict (invariant 3). Consequence: any party verifying a proof recomputes the
*same* verdict — verdicts are reproducible from the proof alone.

**Escape hatch (sanctioned).** If some workflow value genuinely must gate a sealed
verdict (e.g. a regulator requires "all answering ADRs accepted"), the move is **not**
to let `satisfied` read a tracked field — it is to *promote that field to
`hash_fields`*, accepting that its changes now count as drift. The rule stays intact;
the cost of committing-to-status is paid explicitly (status changes re-suspect) rather
than smuggled in (verdict silently depends on unsealed state).

## 8. Open items

- Surface syntax: structured data format (YAML/JSON + schema) vs bespoke grammar.
  Leaning structured-data to avoid owning a parser near the TCB.
- `acyclic` on the SHACL side: SHACL-SPARQL vs a dedicated structural pass (core SHACL
  cannot express a global no-cycles constraint).
- Seal the *generated artifacts* (SHACL + Datalog), not the DSL source, so the
  transpiler stays out of the trusted base (verifier runs stock pySHACL + clingo).
- Glossary additions: `identity field`, `committed content`, `tracked field`,
  `verdict reproducibility`, `static invariant`, `field routing`.