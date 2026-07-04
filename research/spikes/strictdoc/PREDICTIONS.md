# StrictDoc Spike — Pre-Registered Predictions (WP-3)

**Written before probe execution.** Baseline rehearsed on StrictDoc **0.25.0** (export
green, custom grammar accepted, source markers bind); S1–S9 NOT run. Two facts learned
during rehearsal that predictions build on: (a) the CLI is
`{about, export, format, import, manage, new, server, version, launcher}`; (b) the
package ships JUnit/Robot XML **test-report readers** (`backend/sdoc_source_code/
test_reports/`) — so the OFT-O7 "unrepresentable" prediction must NOT be copied here.
(c) The export cache keys source files by an apparent content hash — probe S5 asks
whether anything user-facing consumes it.

**The fragment:** SYS001 ← refines ← REQ001; ADR001 answers REQ001; impl = annotated
range in `src/scheduler.c` (`@relation` markers ×2); TST001 verifies REQ001.

---

## S1 — Relation types are {Parent, Child, File}; ROLE is a declared label without semantics
**Prediction (high confidence).** The relation TYPE vocabulary is fixed; `ROLE` is a
free-text label that must be *declared* in the grammar (an undeclared role on a node
is a parse error — structural enforcement exists), but no engine behavior ever reads
the role: `refines` vs `answers` vs `verifies` render identically in traceability and
affect nothing. Better than Doorstop P1 (a type slot exists and round-trips) — but the
slot is *decorative*.
**Probe.** (a) Add `ROLE: undeclared_role` to a relation → expect parse error.
(b) Grep exported HTML/JSON for role strings: do they appear at all, and does any
view distinguish them?

## S2 — The grammar IS a definition→validator story (structural only)
**Prediction (high confidence).** `SingleChoice` violation (`STATUS: Bogus`) and a
missing `REQUIRED: True` field each fail the export with a grammar error. StrictDoc is
the only tool in the WP set with a **user-definable schema enforced by the tool** —
the structural half of SEG contribution #4, in the applied field. What it lacks
(predict, verify by doc/source read): any field-role distinction (no committed vs
tracked, no hash-field selection), and any satisfaction/verdict semantics attached to
the grammar — the definition compiles to parse-time checks only.
**Probe.** Break STATUS choice; delete a required field; time-boxed check for any
semantic knob in the grammar syntax.

## S3 — No review/affirmation state; drift axis absent entirely
**Prediction (high confidence).** Nothing in the `.sdoc` format records reviewed-ness
or link freshness: edit REQ001's STATEMENT → export stays green, nothing flags, no
file records that anything changed (git is the only history). No stamp, no suspect
concept, no revision pin. On the drift axis StrictDoc sits at **none** — weaker than
Doorstop (one-sided hash) and OFT (manual counter).
**Probe.** Edit REQ001 STATEMENT, re-export, diff outputs for any flag; grep the
format/docs for review/approval machinery (STATUS is a plain grammar field — inert
metadata like OFT's, S2 territory).

## S4 — MID is an anchor, not a commitment
**Prediction (medium confidence).** The MID feature (`--reqif-enable-mid`,
machine identifiers) generates random stable IDs for element anchoring/matching,
not content hashes; no integrity semantics. The content-hash-looking cache key from
rehearsal is **cache invalidation only** — no user-facing integrity feature reads it.
**Probe.** Enable MID / read its docs+source; locate the cache-key computation and
its consumers.

## S5 — Source binding is a locator with ranges; content drift invisible
**Prediction (high confidence).** Editing the function body (markers kept) → nothing
anywhere changes verdict-wise (re-export green, links intact). Deleting a marker →
the link silently disappears from the traceability views (stateless recompute; no
error, no "previously covered" memory). Like OFT O1's polarity question: does an
uncovered requirement *fail* anything? → S6. The `scope=` ranges are richer locators
than Doorstop's keyword (`ref`) but equally content-blind.
**Probe.** (a) body edit → re-export, compare source page; (b) delete the REQ001
marker → re-export, observe silence vs error; check exit codes.

## S6 — Coverage is a report, not a verdict
**Prediction (medium confidence).** No built-in check fails the export when a
requirement has no children/tests/source coverage. Traceability screens *display*
coverage; exit code stays 0. If a project-config check option exists (e.g. warnings
on unlinked), it is opt-in and structural, not a satisfaction predicate.
**Probe.** Remove TST001's relation → export; check exit code + any warning. Grep
project_config for check/validation options.

## S7 — Test reports import as nodes, but nothing consumes pass/fail (the relocated wall)
**Prediction (medium confidence — the interesting one).** JUnit/Robot XML readers
ingest test results into the tree (likely as generated items linked to requirement
UIDs). REFUTES the OFT-O7 shape: the *data* is representable. But (a) **no verdict
semantics**: no built-in question "is REQ001 satisfied?" consumes pass/fail — a failed
test and a passed test both just render; (b) **no staleness binding**: nothing pins a
report to the source/requirement version it ran against — a stale green report
satisfies the display forever. The SEG wall relocates from representation (OFT) to
*semantics + freshness* (StrictDoc).
**Probe.** Feed a minimal JUnit XML (one pass, one fail vs REQ001/TST001); observe
representation; search for anything that changes color/status/exit code based on
`failure`; check what timestamp/version linkage exists.

## S8 — Exchange: ReqIF both directions; no integrity artifact anywhere
**Prediction (high confidence).** `import reqif` + `export --formats=reqif-sdoc`
round-trip (richer than OFT's export-only ReqM2 and Doorstop's nothing); JSON/Excel
exports exist. No export carries a hash, signature, or any recomputable commitment.
Composition story: textual interchange, no scope/assumption concept.
**Probe.** Export ReqIF + JSON; grep for integrity strings; note what survives a
round-trip (UIDs? roles? grammar?).

## S9 — No user-definable checks: no rule language, no plugin hook
**Prediction (medium confidence).** Nothing like Doorstop's `item_validator` exists:
no plugin/hook facility, no rule language; `impl_violates_adr` is inexpressible
without forking or external scripting against the JSON export. The extensibility
spectrum gains a fourth point: StrictDoc = *rich structural schema, zero semantic
extensibility*.
**Probe.** Time-boxed (20 min) doc + `project_config.py`/CLI source sweep for any
validation-extension point.

---

## Scoring
Per probe in RESULTS.md (section format): observed output (paste), verdict
(CONFIRMED / REFUTED / SURPRISE), matrix-cell impact. Cross-tool synthesis addition:
where StrictDoc lands on the drift axis (predict: none), the extensibility spectrum
(predict: schema-rich/semantics-zero), and the evidence wall (predict: representation
present, semantics+freshness absent).
