# StrictDoc Spike — Results

StrictDoc version: 0.25.0   Date: 2026-07-04

### S1 — ROLE declared but semantics-free

- **Verdict:** CONFIRMED (with an upgrade on the carry half)
- **Observed:** Node role not declared in grammar ⇒ `Semantic error: Requirement
  relation type/role is not registered: Parent / bogus_role`, exit 1. Declared roles
  render in HTML and round-trip in JSON (`"ROLE": "refines"` etc.) and survive ReqIF
  export (S8). No engine behavior reads them (S6/S9: nothing computes over relations).
- **Table-cell impact:** Edge typing: declared, validated, carried, rendered — but
  *semantics-free*. Better than Doorstop (typed slot exists and round-trips); still no
  facet/verdict meaning.

### S2 — grammar = structural definition→validator

- **Verdict:** CONFIRMED
- **Observed:** `STATUS: Bogus` ⇒ `Semantic error: Requirement field has an invalid
  SingleChoice value: Bogus`, exit 1. Required field deleted ⇒ `Node is missing a
  field that is required by grammar: STATUS`, exit 1. Custom element tags (ADR, TEST)
  and per-element relation/role declarations all enforced. No field-role distinction
  (nothing like committed vs tracked), no hash-field selection, no semantics attach
  to the grammar.
- **Table-cell impact:** The only tool in the WP set with a user-definable, enforced
  structural schema — the applied-field cousin of SEG contribution #4, *structural
  half only*: the definition compiles to parse-time checks, not to verdict/commitment
  machinery.

### S3 — no review/affirmation state (drift axis: none)

- **Verdict:** CONFIRMED
- **Observed:** REQ001 STATEMENT reworded ⇒ export green, exit 0, zero flags (only the
  TOML deprecation warnings in the log). The `.sdoc` format stores no reviewed/stamp/
  hash field (grep 0). No revision pin either.
- **Table-cell impact:** Drift axis position: **none** — below both Doorstop
  (one-sided hash) and OFT (manual counter). Git history + the DIFF feature (S4) are
  the only change stories.

### S4 — MID/cache-hash are anchors, not commitments

- **Verdict:** CONFIRMED + SURPRISE
- **Observed:** `MID = uuid.uuid4().hex` (`helpers/mid.py`) — random anchor, not
  content-derived. But md5 *content* hashing exists (`helpers/md5.py`) with two
  consumers: the pickle/source cache, and the **DIFF/changelog feature**
  (`features/diff_and_changelog/project_diff_analyzer.py`: per-requirement and
  per-document md5 sets, similarity matching between two project trees).
- **Table-cell impact:** Content hashing exists *as an on-demand diff report between
  two trees* — never stored as a baseline, never binds a link, never gates a verdict.
  "The hash half exists as a report feature, not an integrity mechanism."

### S5 — source binding = locator with ranges, content-blind

- **Verdict:** CONFIRMED
- **Observed:** (a) function body rewritten, markers kept ⇒ exit 0, source page links
  intact (REQ001 ×39). (b) `@relation(REQ001…)` marker deleted ⇒ exit 0, **silent**
  (only TOML warnings), link vanishes from the source page (REQ001 39→4, residue =
  the surviving ADR001 marker); no error, no memory that coverage existed.
- **Table-cell impact:** Parser-as-locator without the hash half, like Doorstop P8 —
  richer locators (scopes/ranges, tree-sitter parsers) but equally content-blind and,
  unlike Doorstop's `ref`, *silently* droppable.

### S6 — coverage is report-only

- **Verdict:** CONFIRMED
- **Observed:** TST001's only `verifies` relation removed ⇒ exit 0, zero
  uncovered/orphan output. Coverage machinery that exists
  (`REQUIREMENTS_COVERAGE`/`TRACEABILITY_MATRIX_SCREEN` features) generates display
  screens.
- **Table-cell impact:** No verdict of any kind — not even OFT's hardwired one. The
  only failing checks are structural (grammar, unresolved UIDs).

### S7 — test reports representable; pass/fail semantics absent

- **Verdict:** CONFIRMED (both halves — the wall relocates)
- **Observed:** `report.pytest.junit.xml` ingests as a document (discovered by the
  *document* finder — a format-fix finding: it must be under `include_doc_paths`, not
  `include_source_paths`). Generates `TEST_RESULT` nodes: UID
  `tests.test_scheduler.test_lock_reentrant`, `STATUS: PASSED/FAILED`, `TEST_PATH`,
  `TEST_FUNCTION`, `File` relation → `tests/test_scheduler.py`. Chain navigable:
  TEST_RESULT →File→ test source →`@relation`→ TST001 →`verifies`→ REQ001. A `FAILED`
  status changes nothing: exit 0, no roll-up, nothing consumes it. Binding is by
  *path only* — no version/hash pin; a stale green report imports identically.
  (A `.gcov.json` coverage reader also exists.)
- **Table-cell impact:** REFUTES the OFT-O7 shape: evidence nodes with values ARE
  representable (unique in the WP set). The SEG wall relocates to **semantics**
  (nothing computes over pass/fail) and **freshness** (no staleness binding).

### S8 — ReqIF/JSON exchange; no integrity artifact

- **Verdict:** CONFIRMED
- **Observed:** `--formats=reqif-sdoc` (feature `REQIF`) exports clean; 0 hits for
  sha256/checksum/signature; relation roles survive (`refines` present in the .reqif).
  JSON export carries the full node set incl. roles and TEST_RESULTs. `import reqif` /
  `import excel` exist (round-trip not exercised).
- **Table-cell impact:** Exchange: ReqIF both directions + JSON — richest interchange
  in the WP set; entirely textual, no commitment, no scope/assumption concept.

### S9 — no rule language, no plugin hook

- **Verdict:** REFUTED on the letter, CONFIRMED in spirit
- **Observed:** `core/plugin.py`: `StrictDocPlugin.traceability_index_build_finished(
  traceability_index)` — a user plugin (via the Python config, `user_plugin`) receives
  the **whole traceability index** post-build. No rule language, no declarative
  checks; the CLI has no check/lint command.
- **Table-cell impact:** A hook exists and is *more* capable than Doorstop's per-item
  one (whole-graph). Same conclusion: expressing `impl_violates_adr` = writing the
  verdict layer yourself in arbitrary Python. Pre-registration caught the
  letter-refutation on both Python tools.

## Surprises / format fixes

- StrictDoc 0.25 ingests **Markdown files as documents**: the kit's own
  README/PREDICTIONS/RESULTS broke the export (heading-level rule) until
  `include_doc_paths` scoped the tree — the committed kit needed this fix (the
  rehearsal predated the meta-files).
- JUnit reports are **documents, not source files** (document_finder dispatches on
  `.junit.xml`); `include_doc_paths` must cover them.
- The TOML config format is deprecated (0.25) in favor of a Python config — which is
  also where `user_plugin` (S9) lives.
- Format-specific report suffixes required: `.pytest.junit.xml` etc.

## Cross-tool synthesis additions (vs Doorstop/OFT/SEG)

- **Drift axis position: none.** No stored review state, no revision pin; content-md5
  exists only as the on-demand DIFF report. Axis now has four verified settings:
  none (StrictDoc) / one-sided hash (Doorstop) / two-sided counter (OFT) /
  two-sided hash (SEG).
- **Extensibility spectrum:** OFT = nothing / Doorstop = per-item Python /
  StrictDoc = whole-graph Python / SEG = declarative stratified Datalog. SEG's
  auditability position is between "nothing" and "anything" — now with three
  verified points around it.
- **Evidence wall:** representation PRESENT (unique: TEST_RESULT nodes with
  pass/fail), semantics ABSENT (nothing consumes them), freshness ABSENT (path-only
  binding). The wall relocates rather than disappears.
- **Definition language:** StrictDoc is the applied existence proof that a
  user-definable, tool-enforced *structural* schema is wanted in this niche (Zephyr
  uses it via a shared `.sgra`); what no tool has is the definition compiling to
  *verdict + commitment* machinery — exactly SEG contribution #4's claim boundary.
