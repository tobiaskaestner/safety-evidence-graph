# SEG Maturity Pipeline — model, target layout, and migration record

**Status:** model + skeleton **ratified** (2026-06-27); migration **complete**
(2026-06-28), walked one stage/artifact at a time. The detailed migration map moved
to `notes/sessions/migration_to_repo.md`; this doc keeps the model, target layout,
and the apply log.

> Placement note: this doc describes a repo-wide reorganization and is itself
> cross-cutting; it currently lives in `notes/` and will find its final home once
> the stage spaces exist.

## The model — one maturity funnel

Each stage **gains commitment and loses generality** as an idea flows down it:

1. **Funnel** — divergent idea exploration. No commitment, no filter. Unit = a
   candidate idea/question. Exit = "worth deepening." *(No content today; new space.)*
2. **Research** — convergent, *general-grounds*: literature grounding + **small,
   self-contained throwaway prototypes** that prove a point independent of SEG, →
   conclusions that hold for anyone. Unit = a justified claim. Exit = "solid enough
   to shape the real prototype."
3. **Prototype** — SEG-specific, quick-and-dirty additions to **the actual SEG
   prototype**, learning through feedback; *not* proper SW engineering. Unit = a
   working-but-throwaway feature validating a direction. Exit = "design element matured."
4. **Development** — matured design drives **test-first, traceable SW engineering**
   (the Phase B worktrees). Unit = a requirement-led, tested implementation.

The pivot between 2 and 3: a *self-contained micro-prototype proving a general
claim* (Research) vs. an *addition to the SEG prototype artifact itself* (Prototype).

## Target layout

```
funnel/        notes/                     ← new; raw ideas, open questions (notes only)
research/      notes/                     ← conclusions, lit, paper seeds, working-draft
                                             "design-shaped" docs (notes only — no design/)
               prototypes/                ← self-contained throwaway prototypes
                 spdx-v3.1-exchange/        (incl. its embedded clingo demos + outputs)
                 demos/                     (most of prototypes/demos/*)
                 examples/                  (*.dsl)
prototype/     notes/                     ← stage 3 general notes
               design/                    ← design-of-record at prototype maturity
               graph-construction/        (the original SEG prototype)
development/   notes/                     ← stage 4 general notes (decision_log, handoffs)
               design/                    ← design-of-record (summary, constraints, realization, CLI)
               (Phase B worktrees reqs/ impl/ results/ graph/ stay put — DEC-002)
```

**Conventions (ratified):** split documents by stage; **same basename in different
stage folders is fine** — the folder names the stage (so a per-stage `decision_log.md`
is allowed). Each stage has a `notes/` folder for general notes; **`design/`
(design-of-record) exists only in `prototype/` and `development/`** — funnel and
research hold notes only (their design-shaped docs are working drafts/conclusions,
not yet design-of-record). The decision log is a *record* → `notes/`, not `design/`.
Moves use `git mv` to preserve history.

## Apply phase — applied (2026-06-28)

- **(a) moves** `f02c9f1` — stage dirs created; all settled relocations done as
  history-preserving `git mv`; `prototypes/`/`design/`/`briefs/`/`generated/`/`paper/`
  dissolved. `BUNDLE_CONTENTS.md` later archived to `notes/sessions/` (committed in c1).
- **(b) decision-log split** `4731d54` — `seg_decision_log.md` → two stage slices +
  `notes/decision_log_index.md`; DEC-003 split at the Decision/Rationale boundary.
- **(c1) propagation — CLAUDE.md** `40ead15` — binding-docs paths + Phase-A reframe.
- **(c2) propagation — README + stage docs** `c794beb` — repointed all stale path /
  `seg_decision_log.md` citations to the stage layout + the index.
- **(c3) propagation — demo imports + this status** — fixed two broken runtime imports
  (`seg_demo_clingo_forward_v1` → `seg_demo_clingo_forward` in `compliant_item.py` /
  `forward_export.py`; gates re-run 3/3); flipped this doc to applied.

**Migration complete (2026-06-28).** Follow-ups resolved: `seg_spdx_fusa_handoff.md`
archived to `notes/sessions/` (`888d816`); `seg_open_threads.md` ↔ `SESSIONS.md`
reconciled into distinct roles (`aae734d`). **Left by decision:** the cosmetic `_vN`
mentions in demo docstrings (legitimate lineage notes; not worth a per-line sweep).

### Post-migration tidy-ups (2026-06-28)

- **`generated/` folded into its prototype** — the prior-run snapshot moved from the
  shared `research/prototypes/generated/` to `research/prototypes/spdx-v3.1-exchange/generated/`;
  these BOMs/graphs are outputs of that one prototype, not a cross-prototype artifact.
  README repointed (both refs); demo scripts unaffected (they write cwd-relative, not
  into this snapshot).
- **`notes/sessions/archive/`** introduced to hold spent session artifacts out of the
  way; `BUNDLE_CONTENTS.md`, `HANDOFF_layerB.md`, `MANIFEST.md` moved there. Frozen
  session notes that mention these by name keep their historical references.
- **spdx prototype restructured into packages** — the flat 16-file
  `spdx-v3.1-exchange/` split three ways: `lib/` (5 import-only common-logic modules:
  graph, ruleset, composition, commitment, graphviz), `demos/` (the 6 `seg_demo_clingo_*`
  model-level gates), and the top level kept as the runnable three-party round-trip
  (`producer`/`spdx_export`/`supplier`/`consumer`) + `validate`. Both subfolders are
  packages (`__init__.py`); imports repointed to `lib.*`, demos run as
  `python -m demos.<name>` (README step 4 updated). All 6 gates re-verified
  (forward 5/5, forward_export 3/3, compliant_item 3/3, conformsto 3/3; the other two
  exit 0).
- **Root `README.md` reclassified and moved** — it was entirely about the SPDX
  round-trip (title "SPDX ↔ SEG safety-BOM round-trip"), not the repo, so it moved
  from the root into `research/prototypes/spdx-v3.1-exchange/README.md`. Self-referential
  paths localized (`generated/`, "run from this directory"); repo-level cross-refs
  (`notes/decision_log_index.md`, `research/notes/GAPS.md`) kept root-relative as they
  live at repo level.
- **README tree introduced** — a lean repo-level `README.md` (what SEG is + the pipeline
  + a delegating table) plus one README per top-level stage folder (`funnel/`,
  `research/`, `prototype/`, `development/`) and `notes/`. The root stays short by
  routing to the folder READMEs; `skills/` keeps `SKILL.md` as its doc (no README).

## Process

propose → ratify (mark the row Settled) → log (update this doc) → apply (`git mv`).
No bulk reorganization; ratify and move one stage/artifact at a time.
