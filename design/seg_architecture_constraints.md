# SEG Architecture Constraints
 
Structural constraints the `seg` engine must satisfy, extracted for the Software
Engineer from the decision log and the design summary. Each constraint is binding;
the cited decision carries the rationale. This document is *what the engine's shape
must obey* — distinct from the design summary (the concept) and the decision log
(the why). Read alongside the SWE brief.
 
Legend: **[now]** applies to v1 as built today; **[seam]** a v1 structural
requirement that exists so a later version can plug in without a rewrite;
**[future]** a constraint that activates in a later version but should not be
designed against.
 
## Seams (isolate the variable parts)
 
**AC-001 — Taxonomy behind one provider. [seam]**
Node/edge types, the strong flag, and hash-field selection are accessed through a
single internal graph-model/schema provider — never hardwired (`Requirement`,
`refines`, …) through the engine logic. v1 populates it from hardcoded constants,
framed as "the built-in safety-evidence graph type." (DEC-007)
 
**AC-002 — Satisfaction behind one evaluator. [seam]**
Requirement satisfaction is a pure, deterministic, side-effect-free predicate over
the typed graph, behind a `SatisfactionEvaluator` interface. v1's DEC-001
leaf/non-leaf logic lives in that form — written declaratively (it is essentially
a Datalog program in Python), not woven into imperative gate code. (DEC-001,
DEC-007)
 
**AC-003 — Input behind one record-producing interface. [seam]**
The engine consumes node/edge records through one interface; the iteration-0
store-loader and the later real extractors are interchangeable adapters. Swapping
them is an adapter change, not a rewrite. (SWE brief §4)
 
## Hashing & integrity (fixed, universal)
 
**AC-004 — Raw-byte hashing, parser-as-locator. [now]**
Content sub-hashes are SHA-256 over raw source byte spans. The parser
(`ast`/tree-sitter/doxygen) only *locates* the span; its output never enters a
hash. Span boundaries are defined parser-independently. Never hash
`ast.get_docstring(clean=True)` output — slice the raw span. (DEC-003)
 
**AC-005 — The graph stores only hashes. [now]**
No node or edge content is persisted in the graph. When content is needed (e.g. the
affirmation diff), it is fetched transiently from the versioned source repos and
discarded. (Design summary; DEC-006)
 
**AC-007 — Determinism & reproducibility. [now]**
Hashing, the design-root commitment, satisfaction evaluation, and `needs.json` consumption are
deterministic and reproducible across runs and environments. Same inputs → same
hashes, same root, same verdict. (DEC-003)
 
**AC-013 — Integrity mechanics are not configurable. [now]**
Content→hash binding, suspicion propagation along strong edges, the flat-sealed
design root over the design set (DEC-014; deep aggregation retired, DEC-012), and
link-state semantics are fixed engine behaviour, parameterized only by
the declared vocabulary — never redefinable per graph type. (DEC-007)
 
## Authority & affirmation
 
**AC-006 — Capability, not authority. [now]**
The engine *provides* proof-generation and affirmation mechanisms; the FSM
*operates* them. The engine never generates an authoritative proof on its own and
never auto-affirms. (DEC-004; SWE brief)
 
**AC-009 — Affirmation anchor is mandatory. [now]**
When writing a ReviewEvent, the engine records the per-endpoint source-repo commit
SHAs (`seg:affirmedAt.from`/`.to`), including for bootstrap bulk affirmations. This
capture cannot be backfilled. (DEC-006)
 
**AC-010 — Transitive suspicion is derived. [now]**
`transitivelySuspect` is computed, not affirmed; it auto-clears on descendant
re-affirmation. Affirmation sets only `directlyOutdated`/`doublyOutdated` edges
back to `active`. (DEC-005)
 
## Conformance & boundaries
 
**AC-008 — Schema conformance. [now]**
The engine emits only records valid against the schemas (draft 2020-12). The
would-be-store is *not* schema-validated — it holds content, which the graph never
stores. (SWE brief §4)
 
**AC-012 — Branch/worktree boundaries. [now]**
Engine code lives in `impl/` (`src/seg/`, `tests/`); engine output is destined for
`graph/`, raw artifacts for `results/`. The engine never writes outside its owned
branch. (DEC-002)
 
## Future-proofing
 
**AC-014 — Engine as a library; CLI is a thin layer. [seam]**
The engine is a library with a clean programmatic core; the CLI is a thin
presentation layer over it, with no logic buried in command handlers. Any later
interface (REST, review UI, TUI) is then a thin adapter over the same core. A
read API serves committed state only; a write API is permitted solely as a
human-in-the-loop, git-committed review backend — never headless. (DEC-008)
 
**AC-015 — Repo topology behind config. [seam]**
The repo set, names, roles, and the node-type→source-repo mapping are read from
config, never scattered as `repoA/repoB/...` literals through the engine,
extractors, or manifest-writer. v1 ships the built-in four-repo safety topology
behind this seam. When configurable (future): `sourceRepo` becomes a
config-validated logical name, the `EvidenceManifest` records a `{repo → SHA}` map,
and `snapshotId` hashes the configured set — all proof-bound. (DEC-009)
 
**AC-016 — Preserve composition-enabling invariants. [seam]**
No v1 code, but v1 must not break what compositional proof (DEC-010) will need:
every proof is independently verifiable (design root recomputable from its
nodeManifest), every proof publishes its scope explicitly, requirement IRIs are
globally unique and stable, and the satisfaction evaluator (AC-002) stays
extensible to an additional discharge case (satisfied-by-external-proof). (DEC-010)
 
**AC-011 — Trusted-base config is proof-bound. [future]**
When vocabulary, hash-field selection, or satisfaction rules become configurable,
each is versioned, hashed, and bound into the proof (a proof records which
definition/ruleset, at which version, produced it). v1 keeps these factored (via
AC-001/AC-002) so this binding is addable without restructuring. (DEC-007)