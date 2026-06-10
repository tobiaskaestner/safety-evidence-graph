# SEG Glossary

**Phase:** defining. We work in dependency order (not alphabetical), so each
definition leans only on terms already pinned above it. Defined terms move into
**Definitions**; the rest wait in **Pending**.

**Naming convention:** head-noun first, qualifier after a comma or in parens
(e.g. `suspicion, direct`). Override freely.

**Scope note:** mechanism / architecture vocabulary. The concrete catalogue of
the 5 built-in node types and 7 built-in edge types lives in the design docs;
pull a specific type name in here if it needs pinning.

---

## Definitions

### Batch 1 — integrity foundation (content → hash)

**parser-as-locator / raw byte span** — A discipline for how content enters the
hash layer. A language- or format-specific parser is used *only to locate* the
region of a source artifact that constitutes a node's content, returning a
positional anchor (byte offset + length, or equivalent) into the raw file; the
bytes in that region, exactly as stored on disk, are the *raw byte span*. The
hash is taken over those raw bytes — never over the parser's structured output
(AST, tokens, normalised form). This keeps hashes independent of parser version,
parser bugs, and normalisation choices, so two parties hashing the same bytes
agree regardless of tooling. The parser locates; it does not transform. (A node
may have more than one span; the logical-field → span mapping is
`hash-field selection` / `binding adapter`, defined in the structural batch.)

**nodeHash (content hash)** — The content hash of a node instance: SHA-256 over
the raw byte span(s) that constitute the node's content. It is *content-local* —
a function of the node's own bytes alone, never of neighbours, incident edges, or
graph position. Computed transiently by extractors at evaluation time and
persisted only inside sealed proof documents, never in the graph store (repo G).
Identical bytes ⇒ identical nodeHash; any content edit ⇒ a different nodeHash.
(When a node type declares several logical hash fields, the nodeHash is taken
over the canonical concatenation of their spans; the exact field set per type →
structural batch.)

**edgeHash** — The affirmation-time, one-hop fingerprint binding an edge instance
to its two endpoints' content:

`edgeHash = SHA-256( from ‖ to ‖ type ‖ nodeHash(from) ‖ nodeHash(to) )`

where `from`/`to` are the endpoint identities, `type` the edge type, and the
nodeHashes are the endpoints' content hashes captured *at affirmation*. (`‖` is an
unambiguous, length-prefixed concatenation; its canonical encoding is part of the
trusted base.) It reaches *exactly* its two endpoints and no further — local and
topology-indifferent. The affirmed value is stored in the graph store; recomputing
it later from the endpoints' current nodeHashes and finding a mismatch means an
endpoint's content has drifted since affirmation. That mismatch is the local
detection that *seeds* suspicion. Because it never reaches past one hop, an
edgeHash alone cannot detect any transitive effect. (Only edge types whose `binds`
facet is set carry an edgeHash — facet defined in the structural batch.)

**affirmation / re-affirmation** — The human act of asserting that an edge
correctly holds between its two endpoints *as they currently stand*. At
affirmation the edge's `edgeHash` is computed over the endpoints' current
nodeHashes and written as the affirmed value, and the edge enters the `active`
state. *Re-affirmation* is the same act after an edge has gone `suspect` (an
endpoint drifted): the human re-checks the edge against the changed content and,
if it still holds, captures a fresh edgeHash over the new nodeHashes, returning
the edge to `active`. Affirmation is the *only* moment an edgeHash is written —
the trust-injection step. The mechanism records integrity; a human asserts
correctness. (`active` / `suspect` → states batch.)

**merkleHash / design root** — The global integrity fingerprint of the design
graph — the deliberate global counterpart to the local `edgeHash`. The *design
root* is a **`flat-sealed` set commitment**: the design-graph node/edge set is put
in canonical order and hashed to a single root, sealed into the design half of a
proof (DEC-012). Two consequences distinguish it from `edgeHash`:

- *Whole-set / non-localising.* Any change to a committed member changes the root
  — tamper-evident over the entire set at once — but a changed root tells you
  *something* in the set changed, not *which* member, and carries no per-node
  verdict.
- *Cycle-tolerant.* A set commitment imposes no hierarchy, so the design graph
  need not be acyclic for the root to be defined (contrast the retired `deep`
  mode, whose recursive fold was undefined on a cycle).

(Historically the design root was computed by `deep` topology-aware aggregation up
the `refines` DAG; DEC-012 retired that for a set commitment after no verifier was
found that needed the per-node aggregates. The per-node `merkleHash(N)` survives
only in the dormant `deep` mode. Which edges enter the root, and in which mode, is
the `fingerprint` facet. Per-node verdicts such as satisfaction and suspicion
*localisation* live in the derived verdict layer, not here.)

### Batch 2 — structural vocabulary + facets

*Structural primitives*

**node type** — A declared kind of node in a graph-type definition: a named
category (e.g. Requirement) carrying a logical hash-field structure (which of its
fields constitute hashable content → `hash-field selection`) and a declared
source (where instances draw their content from). Instances of a type share
structure but each has its own `nodeHash`. The built-in safety model declares
five: Requirement, TestSpecification, Implementation, TestOutcome, Waiver.

**edge type** — A declared kind of directed relation in a graph-type definition: a
named relation (e.g. refines) with a `domain` and `range` and its facet settings
(`binds`, `propagates`, `fingerprint`, `acyclic`). All instances of a type obey
the same endpoint typing and carry the same facets. The built-in model declares
seven: refines, verifies, implements, calls, confirms, witnesses, excuses.

**domain / range** — The endpoint typing of an edge type: `domain` is the node
type its instances point *from* (source), `range` the node type they point *to*
(target). An edge instance is structurally well-formed only if its source is of
the domain type and its target of the range type. Direction runs domain → range
(e.g. refines: domain Requirement, range Requirement, oriented child→parent). The
first check the generic checker performs.

**sink (edge class)** — An edge type that terminates rather than transmits: in v1,
one that neither propagates suspicion nor participates in the Merkle.
Post-decomposition, a sink is the facet complement of a contributing edge —
`propagates = false` and `fingerprint = none` (whether a given sink also `binds`
is a separate per-type question). Built-in sinks: confirms, witnesses, excuses.
Contrast `strong`.

**leaf node** — Relative to a recursive edge type, a node with no incoming edges
of that type — the base case of the recursion. For `refines` (child→parent), a
leaf requirement is one no other requirement refines: satisfaction bottoms out
there (a leaf is satisfied directly by its evidence, a non-leaf by its children).
(Under the retired `deep` aggregation mode, a leaf — no incoming deep edge —
reduced to its own `nodeHash`; dormant since DEC-012.) "Leaf" is always relative
to a named edge relation, never absolute.

*Facets (per-edge-type attributes that `strong` used to bundle)*

**binds (facet)** — When set, instances of the edge type store an `edgeHash` at
affirmation and are subject to drift detection (a mismatch on re-derivation seeds
suspicion). The local, one-hop integrity facet; independent of `propagates` and
`fingerprint`. *Open per-type question:* whether `witnesses` binds via an edgeHash
or instead anchors freshness through a commit-pin.

**propagates (facet)** — When set, suspicion arriving at one endpoint flows across
the edge to the other and onward, contributing to the transitive-suspicion
closure. The conduit facet. Cycle-tolerant: propagation is a least-fixpoint
closure that terminates on cyclic data, so a propagating edge type need not be
acyclic. *Open per-type question:* direction of flow — domain→range for all
current edges, or are there range→domain cases.

**fingerprint (facet)** — A facet declaring whether and how an edge type
contributes to the design fingerprint (`design root`). Modes: `none` (excluded);
`flat-sealed` (instances enter a set commitment — sort, hash to the scalar root;
the default for fingerprinted edges); `flat-openable` (the same set committed as a
Merkle/vector commitment retaining per-member inclusion paths, for selective
disclosure); and `deep` (recursive in-neighbour aggregation — **retired**, DEC-012,
defined but with no current consumer). The fingerprinted edges form the
`design graph`.

**deep aggregation (fingerprint mode)** — The `fingerprint = deep` mode: instances
are folded into a per-node `merkleHash` by recursive in-neighbour aggregation —
topology-aware and acyclicity-dependent. **Retired (DEC-012):** defined and
re-openable, but no built-in edge type sets it and the engine need not compute it,
because no verifier was found that needs the per-node topology-bound aggregates (a
set commitment binds the topology for tamper-evidence, and the only tree-unique
capability — succinct member opening — belongs to `flat-openable`, which `deep`'s
fold cannot provide).

**flat aggregation (fingerprint mode)** — The `fingerprint = flat` family:
instances enter the design root as members of a **set commitment** (canonical sort,
then hash), imposing no hierarchy — topology-blind and cycle-tolerant. Two
sub-modes:
- **`flat-sealed`** — accumulate the sorted set to a single scalar root. Commits
  the set (tamper-evident) but opens nothing; the default, and the mode the v1
  design root uses (DEC-012).
- **`flat-openable`** — commit the sorted set as a Merkle tree and retain it, so an
  individual member opens with an O(log n) inclusion path (a vector commitment).
  Reserved for authority-decoupled selective disclosure (DEC-012); mechanics
  (sibling order, path format) remain open.

**acyclic (facet)** — A per-edge-type structural constraint: instances must form a
DAG, enforced fail-loud by the generic checker. In the built-in model it is
*declared* (via the `constraint slot`) for edge types feeding a recursive
satisfaction predicate (`refines`), turning satisfaction's silent mis-verdict on a
cycle into a loud structural error — the operative entailment
`satisfaction-role ⟹ acyclic`. The historical entailment `fingerprint:deep ⟹
acyclic` (deep aggregation undefined on a cycle) is **dormant** while `deep` is
retired (DEC-012); it would re-apply only if a `deep` edge type were reintroduced.
See `entailment lattice`.

*Bundle + induced subgraphs*

**strong (edge property — under decomposition)** — The v1 boolean that bundled, in
one flag, what are now separate facets: `binds` + `propagates` + `fingerprint =
deep` (and hence, by entailment, `acyclic`). The bundle was coherent only because
all four coincided on `refines`; it fractures on edges like `calls` (legitimately
cyclic, so unable to be `deep`). "Strong" is being retired in favour of the
explicit facets and survives only as a historical label and the name of the
`strong subgraph`.

**strong subgraph** — The subgraph induced by the edge types carrying the legacy
`strong` property (operationally: the `propagates` edges) — the domain over which
suspicion propagation runs. Since `propagates` and `fingerprint` are independent
facets (DEC-012 era), this subgraph and the `design graph` need not nest; `calls`
is the motivating case of an edge that may propagate without being fingerprinted.
Its exact extension depends on per-type facet assignments still open.

**deep-fingerprint subgraph** — The subgraph induced by edge types with
`fingerprint = deep`. **Dormant (DEC-012):** with `deep` retired, no built-in edge
type populates it, so it is empty in the built-in model. Retained as a concept for
a possible future `deep` reintroduction.

**design graph** — The static design structure committed by the `design root`,
defined as the nodes and edges whose edge types carry a `fingerprint` other than
`none` (DEC-012; formerly the `deep-fingerprint subgraph` — superseded when the
root became a flat set commitment). One of three graph scopes, with `full graph`
(all nodes + all edges) and `evidence graph` (the runtime-attestation side); the
design / evidence split mirrors `proof`'s two halves.

---

## Pending (merged, alphabetical)

- active (link state)
- auto-clear
- binding adapter
- broken (link state)
- constraint slot
- derived state
- drift
- entailment lattice
- evidence graph
- full graph
- gate (commit / proof / release)
- graph-type definition
- hash-field selection
- integrity (local, hash-anchored)
- least-fixpoint semantics
- link state
- meta-model
- pending (link state)
- proof (sealed; design + evidence halves)
- satisfaction
- satisfaction ruleset
- stratified Datalog
- suspect (link state)
- suspect-detection seed (seed set)
- suspicion propagation
- suspicion, direct
- suspicion, transitive
- transitive closure
- trust (global, derived)
- trusted base / TCB (proof-bound)
- verdict
- verdict layer
