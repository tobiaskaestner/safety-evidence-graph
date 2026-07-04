# SEG Spike Kit — StrictDoc (WP-3)

The SEG worked fragment (`seg_definition_language.md` §2 + one refines hop), expressed
as a StrictDoc project. Baseline **rehearsed on StrictDoc 0.25.0** (export green,
custom grammar + source markers bind); probes S1–S9 have NOT been run.

Zephyr's real-world usage (`/wrk/z/ws-safety/doc/reqmgmt`, pinned `strictdoc>=0.9.1`)
was the inspiration: custom `[GRAMMAR]` with typed fields (`SingleChoice`), grammar
`IMPORT_FROM_FILE`, `Parent` relations. This kit exercises the same machinery
self-containedly, plus roles, custom element tags, and source traceability.

## Layout
- `strictdoc.toml` — project config; feature `REQUIREMENT_TO_SOURCE_TRACEABILITY`.
  (NB: TOML config is deprecated in 0.25.0 in favor of a Python config — kept because
  the Zephyr repo uses TOML; a probe notes it.)
- `docs/system.sdoc` — SYS001 (default grammar).
- `docs/software.sdoc` — custom grammar: `REQUIREMENT` (STATUS `SingleChoice`,
  optional RATIONALE; relation `Parent ROLE refines`) + custom tag `ADR`
  (relation `Parent ROLE answers`). REQ001, ADR001.
- `docs/tests.sdoc` — custom tag `TEST` (relation `Parent ROLE verifies`). TST001.
- `src/scheduler.c` — `@relation(REQ001, scope=file)` + `@relation(ADR001, scope=file)`
  markers (the impl is an *annotated source range*, not a node — itself a finding).
- `tests/test_scheduler.py` + `reports/report.pytest.junit.xml` — S7 fixture: an
  annotated test file and a two-case JUnit report (one pass, one failure). NB reports
  are *documents* (must be under `include_doc_paths`), suffix-dispatched
  (`.pytest.junit.xml`).

## Run
1. `pip install strictdoc` (rehearsed on 0.25.0 — record your version in RESULTS.md).
2. From this directory:
   `strictdoc export . --formats=html --output-dir <scratch>/sdoc_out`
   Baseline expectation: export completes; `_source_files/src/scheduler.c.html`
   exists and links REQ001/ADR001.
3. Work PREDICTIONS.md S1→S9 in order. Reset between destructive probes:
   `git checkout HEAD -- docs/ src/ strictdoc.toml` (RESULTS.md excluded).
4. Record in RESULTS.md (per-probe sections): observed output, verdict
   (CONFIRMED / REFUTED / SURPRISE), matrix-cell impact for
   `research/notes/seg_tool_landscape.md` §3.
