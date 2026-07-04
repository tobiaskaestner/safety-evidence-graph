# sphinx-needs Spike — Pre-Registered Predictions (WP-5)

**Written before probe execution.** Baseline rehearsed on **sphinx-needs 8.1.1 /
Sphinx 8.2.3**: the fragment builds clean, needs.json exports, typed extra links get
auto back-links, and a schema-validation pass runs by default. Recon facts predictions
build on: the package ships `needs_schema.py` (jsonschema_rs), `needs_schema_definitions`
with **bounded network validation** (an explicit max-nesting constant in
`schema/config.py`), `needs_warnings` + `needs_constraints` (per-need expression
checks), `external_needs.py` + `needimport`. SEG's own Phase-B reqs worktree uses
sphinx-needs — findings feed directly back.

**The fragment:** SYS001 ← refines ← REQ001; ADR001 answers REQ001; IMPL001
implements REQ001 + adheres ADR001; TST001 verifies REQ001. All five as custom
`needs_types`; edges as `needs_extra_links` (deprecated alias of `needs_links`).

---

## N1 — The richest link-type vocabulary in the set; semantics = navigation only
**Prediction (high confidence).** Config-defined, named, *directed* link types with
per-direction labels and auto-computed back-links — a real edge-type vocabulary
(closest applied cousin of SEG's edge taxonomy). A link to a nonexistent ID produces
a build warning (dead-link reporting), i.e. referential integrity is checked. But no
engine semantics distinguish `refines` from `verifies` — filtering/diagrams only.
**Probe.** Point `:refines:` at a bogus ID → expect warning; check needs.json link
representation; confirm nothing behaves differently per link type.

## N2 — Declarative schema validation, bounded traversal: SHACL-shaped, but non-recursive
**Prediction (medium confidence — the headline).** `needs_fields`-level JSON schemas
(e.g. status enum) fail the build with configurable severity on violation; and
`needs_schema_definitions` can express *link-target* constraints ("a req's refines
must target a sys") validated across the graph to a **bounded depth** — the explicit
max-nesting constant is the wall. So sphinx-needs has climbed to SEG's layer-2
(shapes) territory declaratively, but: no recursion/fixpoint (bounded), no
user-defined derived relations, no verdict object. This is the sharpest apparatus
cell: the applied field approaches non-recursive SHACL while SEG's DEC-007 sits in
the recursive-but-stratified island above it.
**Probe.** (a) status enum schema + violating value → severity/exit behavior;
(b) a link-target type constraint via needs_schema_definitions → violate it → observe;
(c) confirm the nesting bound from source/docs and that nothing recursive is
expressible.

## N3 — needs_warnings / needs_constraints: per-need expression checks, eval-based
**Prediction (high confidence).** Named per-need boolean expressions (Python-eval
filter strings) that raise build warnings (fail with `-W`) or mark
`constraints_passed: false`. Genuinely user-definable checks — but per-need (no joins
across needs, no closure), and eval'd Python strings (Turing-complete in principle,
unauditable — the DEC-007 contrast again, in a filter-string costume).
**Probe.** A constraint `status == 'Approved'` on req; violate; observe warning +
`constraints_passed`; attempt a cross-need condition to find the expressiveness edge.

## N4 — No review/affirmation state; no content binding
**Prediction (high confidence).** Nothing records reviewed-ness, stamps, or hashes;
editing REQ001's text is silent everywhere (needs.json carries full `content` but no
hash of it). Drift axis position: **none** (like StrictDoc; the DIFF-report nuance
StrictDoc has is absent here too — git only).
**Probe.** Edit content → rebuild → diff needs.json fields; grep needs.json for any
hash/stamp field.

## N5 — Source binding: none at all (weakest of the set)
**Prediction (high confidence).** An `impl` need is authored prose; no locator, no
existence check against code, no marker mechanism in sphinx-needs itself. (SEG's own
usage pairs sphinx-needs with *SEG's* extractor doing `:implements:` docstring
markers — i.e., SEG supplies exactly the missing half.)
**Probe.** Confirm no config/directive references source files; note the contrast
cell.

## N6 — Evidence representable by convention; nothing consumes it
**Prediction (medium confidence).** A test-outcome need type with a schema-typed
status is *conventionally* representable (weaker than StrictDoc's first-class
TEST_RESULT importers — no JUnit reader in sphinx-needs core; `needservice`/external
data would be DIY). No semantics consume pass/fail; no staleness.
**Probe.** Model OUT001 pass/fail as a custom type; confirm nothing computes; check
core for any test-report ingestion (expect none).

## N7 — Exchange/composition: the only by-reference cross-project story in the set
**Prediction (medium confidence).** `-b needs` exports needs.json (full content, no
integrity fields); `needimport` copies needs from a needs.json; `needs_external_needs`
*links live* to another project's needs.json via base_url — cross-project linking by
reference, unique in the WP set. But: no hash/signature, no version pin, no staleness
concept — an imported/external need can drift arbitrarily with nothing noticing
(the exact gap SEG's version-pin/seal fills).
**Probe.** Export needs.json + grep integrity fields; wire needs_external_needs to a
second copy; check what happens when the external file changes content for a linked
id (expect: silence).

## N8 — No commitment, no proof
**Prediction (high confidence).** No export carries a recomputable commitment or
signature; builds are reports.
**Probe.** Covered by N4/N7 greps; confirm.

---

## Scoring
Per probe in RESULTS.md (section format): verdict / observed / matrix-cell impact.
Synthesis: drift axis (predict: none), extensibility spectrum (predict: between
Doorstop and SEG — declarative *shapes* + eval-string checks, no recursion),
evidence wall (predict: convention-representable, semantics/freshness absent),
composition (predict: by-reference linking without integrity — the best foil for
SEG's sealed exchange).
