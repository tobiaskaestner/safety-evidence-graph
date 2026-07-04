# sphinx-needs Spike — Results

sphinx-needs version: 8.1.1   Sphinx: 8.2.3   Date: 2026-07-04

### N1 — link-type vocabulary; semantics = navigation only

- **Verdict:** CONFIRMED
- **Observed:** Bogus target ⇒ `WARNING: Need 'REQ001' has unknown outgoing link
  'BOGUS999' in field 'refines' [needs.link_outgoing]`; build succeeds (gate via
  `-W`). needs.json carries per-type link lists + auto-computed back-links
  (`answers_back`, `implements_back`). Nothing behaves differently per link type.
- **Table-cell impact:** Config-defined, named, directed edge vocabulary with
  referential-integrity warnings — the closest applied cousin of SEG's edge taxonomy;
  semantics-free beyond navigation/filtering.

### N2 — declarative schema validation, bounded traversal (HEADLINE)

- **Verdict:** CONFIRMED
- **Observed:** `needs_schema_definitions` with select/validate(local|network)
  accepted. Status-enum violation ⇒ structured `ERROR: Need 'REQ001' has schema
  violations` (severity, field, schema path, message
  `[sn_schema_violation.local_fail]`). Network constraint (req's `refines` must
  contain a `sys`, `minContains: 1`) violated ⇒ `Too few valid links of type
  'refines' (0 < 1) / nok: ADR001` with per-linked-need detail (`"sys" was
  expected`) `[sn_schema_violation.network_contains_too_few]`. `-W` gates exit 1.
  **Citable:** `schema/config.py` `SeverityEnum` docstring: "The levels are derived
  from the SHACL specification" + W3C URL; traversal is explicitly bounded
  (`network_max_nest_level`, max-nesting constant).
- **Table-cell impact:** The applied field's closest approach to SEG's shapes layer:
  declarative, typed, link-target validation across the graph with SHACL-derived
  severities — and a hard non-recursion bound. No fixpoint, no derived relations, no
  verdict object: exactly the boundary below DEC-007's recursive-stratified island.

### N3 — needs_warnings / needs_constraints (eval-based per-need checks)

- **Verdict:** CONFIRMED
- **Observed:** Constraint `status == 'Approved'` on a Draft req ⇒ `WARNING:
  Constraint … FAILED! severity: MEDIUM [needs.constraint]` (requires
  `needs_constraint_failed_options` per severity — crashes without, gotcha). The
  result **persists into needs.json**: `constraints_passed: False` +
  `constraints_results: {'approved_req': {'check_0': False}}`. Scope confirmed from
  source: `filter_single_need` — per-need only, no joins/closure. Expressions are
  eval'd filter strings.
- **Table-cell impact:** User-definable per-node checks whose *derived state exports*
  — but single-need scope and eval-string (unauditable) semantics.

### N4 — no review state, no content binding

- **Verdict:** CONFIRMED
- **Observed:** STATEMENT edit ⇒ build silent. needs.json: `hash`/`md5`/`stamp`/
  `review` all 0 (the two `sha` hits are the word "SHALL"); full `content` is
  exported, unhashed.
- **Table-cell impact:** Drift axis position: **none** (like StrictDoc, minus even
  the DIFF-report nuance — git only).

### N5 — source binding: none

- **Verdict:** CONFIRMED (by inspection)
- **Observed:** No marker/locator mechanism in core (needs live in rst/docstrings;
  `docname`/`lineno` point at documentation, not code). SEG's own Phase-B usage pairs
  sphinx-needs with SEG's extractor doing `:implements:` docstring markers — SEG
  supplies exactly the missing half.
- **Table-cell impact:** Weakest source story in the set: no locator, no existence
  check, no hash.

### N6 — evidence by convention; nothing consumes it

- **Verdict:** CONFIRMED (by inspection)
- **Observed:** A test-outcome need type with schema-typed fields is conventionally
  representable; core has no test-report reader (contrast StrictDoc's JUnit/Robot/
  gcov); the only computations are N2 schemas + N3 constraints — both user-authored,
  structural, per-need. No roll-up, no staleness.
- **Table-cell impact:** Evidence: convention-representable; semantics + freshness
  absent; no importer.

### N7 — exchange: by-reference cross-project, no integrity

- **Verdict:** CONFIRMED
- **Observed:** `needs_external_needs` (base_url + json_path + `EXT_` prefix) wires a
  second project's needs.json; a local `:refines: EXT_SYS001` resolves with no
  dead-link warning and renders linking out. Gotchas: a non-empty `version` is
  required (empty-string current_version rejected — falsy check). **Drift test:** the
  external need's content rewritten to a completely different guarantee ⇒ rebuild
  passes with zero warnings. No hash, no pin, no staleness anywhere. `needimport`
  (copy-in) exists, not exercised.
- **Table-cell impact:** The only by-reference cross-project story in the WP set —
  and it is integrity-free: an upstream can silently change what a downstream relies
  on. The exact gap SEG's hash-pinned boundary + seal fills.

### N8 — no commitment, no proof

- **Verdict:** CONFIRMED
- **Observed:** Covered by N4/N7 greps: no export carries any integrity artifact.
- **Table-cell impact:** Commitment/proof: absent.

## Surprises / format fixes

- **The severity model is explicitly SHACL-derived** — verbatim docstring citation
  with the W3C URL in `schema/config.py`. The applied field isn't accidentally
  SHACL-shaped; it cites SHACL. (Prime related-work sentence.)
- Constraint results (`constraints_passed`, `constraints_results`) persist into the
  needs.json export — derived check state travels with the data (unlike any other
  tool in the set), still without any integrity binding.
- `needs_extra_links` deprecated → `needs_links` (8.x); `needs_statuses` deprecated →
  field schema enums; `needs_constraints` requires `needs_constraint_failed_options`
  or it raises.
- Schema validation runs by default on every build and is fast (jsonschema_rs,
  ~10⁴ needs/s reported).

## Cross-tool synthesis additions

- **Drift axis position: none** — sharpened by N7: even *cross-project* reliance is
  drift-blind. Verified axis: none (StrictDoc, sphinx-needs) / one-sided hash
  (Doorstop) / two-sided counter (OFT) / two-sided hash (SEG).
- **Extensibility spectrum (final):** OFT nothing → Doorstop per-item Python →
  StrictDoc whole-graph Python → **sphinx-needs declarative bounded-depth shapes
  (SHACL-cited) + per-need eval strings** → SEG user-authored *recursive* stratified
  Datalog bound to a commitment. sphinx-needs is the closest applied point below the
  recursion line — and its explicit max-nest bound marks the line itself.
- **Evidence wall:** convention-representable, no importer, no semantics, no
  freshness.
- **Composition:** the set's only by-reference cross-project mechanism, with zero
  integrity — the cleanest foil for the Prague paper's sealed-exchange story.
