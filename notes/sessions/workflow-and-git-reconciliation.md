# Workflow setup + git history reconciliation

- **Session:** `179da4bc-fd43-43d5-a5cb-58eb2fce0768` (2026-07-01)
- **Status:** paused — awaiting user review of the reconstructed commits; **nothing pushed**
- **Resume:** `claude --resume 179da4bc-fd43-43d5-a5cb-58eb2fce0768`

## Goal
Move SEG research from the claude.ai web app into this repo: establish a
"separate conversations you can look back at" workflow, then reconcile the
exported file bundle (manual `_vN` versioning) into real git history.

## What was done
1. **Research workflow** — one Claude Code session per topic. `notes/sessions/SESSIONS.md`
   is the curated sidebar (topic → session UUID → status → distilled note);
   revisit with `claude --resume <id>`. Distilled past sessions into
   `notes/sessions/prototype-build.md` and `notes/sessions/schema-testdrive.md`.
2. **Git history reconstruction** — the 2026-06-25 CLI-migration bundle (96 untracked
   files, web-session workspace + design docs) reconciled into **8 commits** on
   `research`, purely additive (no rewrite of existing history). Chosen strategy:
   *generational evolution*, *dates anchored to known signals*, *supersede the SPDX dir*.
   - Design-doc chains replayed as edits to canonical files: `seg_composability_cbd`
     v5→v6→v7, `seg_definition_language` v5→v6, `knowledge_graph_design_summary`
     v5_1→v6_1 (visible in `git log -- <file>`).
   - `prototypes/spdx-v3.1-exchange/` **superseded** with the evolved `-2` content
     (6 gates de-suffixed, new commitment/composition/graphviz modules; `spdx_import.py`
     dropped, old README/GAPS/bom removed — their content lives at root README / notes / generated).
   - Demos & examples collapsed to latest; all `_vN` suffixes dropped (lineage now in git).
   - `CLAUDE_.md` → `CLAUDE.md`; `.DS_Store` ignored.
3. **CLAUDE.md refresh** (commit `3375a20`) — updated to DEC-028: fixed moved
   paths, DEC-001..028 / AC-001..016 ranges, `prototypes/` layout, skill locations,
   and added the composability/contract/SPDX-exchange pillar the v4 file predated.

## Key decisions
- **No more `_vN` suffixes** — git commits are the versioning now. (Exception:
  `seg_example_v1_*.dsl`, where `v1` = the SEG *grammar* version.) See memory `versioning-convention`.
- Commit dates reconstructed (anchored 06-10…06-25), **not** recorded per-change — stated in commit messages.
- Dropped as superseded/dup (history only): `partial_discharge_v1` (per MANIFEST),
  `composition_v2/v3`, `partial_discharge_v2`, `baseline__1__` dup, `plus_composition_v1` + `_1_v5`.

## Open / next steps
- **User reviewing the commits now.** If unhappy: `git reset --hard 8790327` rewinds the whole reconstruction.
- **Push decision pending** — all local on `research`, origin/research not updated.
- ~~Root README.md stale~~ — **done** (commit `05073ed`): refreshed to DEC-028, de-suffixed gates, `prototypes/spdx-v3.1-exchange/` paths. (CLAUDE.md refreshed in `3375a20`.)
- If any dropped dup file should be a standalone, restore from git history.

## Pointers
- `notes/sessions/SESSIONS.md` — the thread sidebar.
- `notes/seg_decision_log.md` — authoritative record (DEC-001…028).
- `BUNDLE_CONTENTS.md` / `notes/MANIFEST.md` — original bundle provenance.
- `git log --format='%h %ad %s' --date=short -9` — the reconstructed history.
