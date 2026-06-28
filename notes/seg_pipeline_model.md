# SEG Maturity Pipeline — model, target layout, and migration record

**Status:** model + skeleton **ratified** (2026-06-27); migration map **in progress**
(walked one stage/artifact at a time). This doc is the record we apply against;
nothing is `git mv`'d until its row is ratified here.

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

## Migration map

### Settled

| Source | Destination |
|---|---|
| `prototypes/spdx-v3.1-exchange/` (incl. its 6 `seg_demo_clingo_*.py` + `generated/` outputs) | `research/prototypes/spdx-v3.1-exchange/` |
| `prototypes/examples/*.dsl` | `research/prototypes/examples/` |
| `prototypes/graph-construction/` (incl. NOTES.md, README.md, schemas/) | `prototype/graph-construction/` |
| `prototypes/demos/*` — **all 8** (verified self-contained; none import `graph-construction`) | `research/prototypes/demos/` |
| top-level `prototypes/` | dissolved (children redistributed above) |
| `research/seg_prior_art.md`, `research/seg_paper_seed.md` | `research/notes/` |
| Root `README.md`, `BUNDLE_CONTENTS.md`, `CLAUDE.md`, `requirements.txt`, `.gitignore` | stay at root (cross-cutting) |
| `notes/sessions/` (session sidebar + distilled notes) | stays (cross-cutting workflow record) |

### Settled — `design/` per-file cut (item 2, ratified 2026-06-27)

`design/` dissolves; the 4 Development docs are design-of-record → `development/design/`;
the 3 Research docs are working drafts/conclusions → `research/notes/` (Research has no
`design/`). No file needs a content split (contrast DEC-003).

| Destination | Files |
|---|---|
| `development/design/` | `knowledge_graph_design_summary.md`, `seg_architecture_constraints.md`, `seg_python_realization.md`, `seg_cli_reference.md` |
| `research/notes/` | `seg_composability_cbd.md`, `seg_definition_language.md`, `seg_adr_projection_core.md` |

- Stream alignment: Development design docs pair with core-engine DECs (001–006);
  Research docs pair with composability/meta-model DECs (007, 010, 012–028).
- The ADR and `composability_cbd` carry Development *footprints* (engine recommendation,
  AC-003/014 ties) but move whole — the binding form already lives in
  `seg_architecture_constraints.md`.

### Settled — GAPS + glossary (item 4, ratified 2026-06-27)

| Artifact | Disposition |
|---|---|
| `notes/GAPS.md` | → `research/notes/` — it is the "SEG ↔ SPDX round-trip GAPS ledger"; every gap (G1–G12) is composability/SPDX, coupled to the DECs + the SPDX prototype. Single Research ledger, **not split**. |
| `notes/seg_glossary.md` | **Cross-cutting, single shared copy — not split.** Mechanism/architecture vocabulary used by every stage; splitting invites terminological drift. Home = the cross-cutting area (below). |

### Settled — funnel seeding (item 5, ratified 2026-06-27)

**Funnel starts empty** — confirmed expected. No charter, no harvested content; the
existing corpus is past the funnel. `funnel/` + `funnel/notes/` are created empty
(a `.gitkeep` placeholder so git tracks them); the user seeds ideas later. The two
files that resembled funnel are Research:

| Source | Destination |
|---|---|
| `research/seg_future_directions_research_context.md` | `research/notes/` — self-described "Research Context for Post-v1 Directions"; open *research* questions, not pre-research ideas |
| `notes/seg_open_threads.md` | `research/notes/` — research/design backlog. **Flag:** overlaps `notes/sessions/SESSIONS.md`; reconcile in item 6 |

DEC "still-open / edge-case" notes are research open-questions and stay with their
DEC; none harvested to funnel.

### Settled — remaining files (item 6, ratified 2026-06-27)

| File(s) | Destination |
|---|---|
| `notes/seg_reconciliation.md` | `research/notes/` |
| `notes/seg_spdx_fusa_handoff.md` | `research/notes/` → **later archived to `notes/sessions/`** (2026-06-28; a timestamped exploration handoff, same kind as `HANDOFF_layerB`) |
| `briefs/prototype_agent_brief.md` | `prototype/notes/` |
| `briefs/re_agent_brief.md`, `briefs/swe_agent_brief.md` | `development/notes/` |
| `briefs/ppt_overview_brief.md` | `notes/` (cross-cutting — outreach, no pipeline stage) |
| `generated/` | `research/prototypes/` (SPDX prototype outputs — travels with it) |
| `paper/` (empty) | `research/paper/` (paper is a research output; seed in `research/notes/seg_paper_seed.md`) |
| `notes/HANDOFF_layerB.md`, `notes/correction-3-handoff-prompt.md`, `notes/MANIFEST.md` | `notes/sessions/` — **archived** as spent session artifacts (DEC-017 applied; bundle reconciliation done) |
| `skills/SKILL.md` | **stays put** — discoverable project skill; moving risks breaking discovery |

- `briefs/` dissolves entirely (children redistributed); agent briefs exist only for
  the prototype + development stages.
- **Deferred to the propagation pass:** reconcile `seg_open_threads.md` (→ `research/notes/`)
  with `notes/sessions/SESSIONS.md` (overlapping session-pickup indexes).

### Cross-cutting area (ratified 2026-06-27): the residual `notes/`. No new `meta/`.
`notes/` becomes the explicit cross-cutting/meta area (no longer a catch-all): holds
`sessions/`, the shared `glossary`, the decision-log master index, and this
`seg_pipeline_model.md`. Stage-specific files leave `notes/` for their stage. Root
stays for repo-level files (README, CLAUDE.md, BUNDLE_CONTENTS). This fixes the
item-1 master-index home (`notes/decision_log_index.md`) and where this doc lives.

### Settled — decision-log split (item 1, ratified 2026-06-27)

`notes/seg_decision_log.md` (28 entries, DEC-011 vacant) splits into two stage files;
**DEC-IDs stay stable and globally unique** so existing `DEC-00x` citations keep
resolving. Insight that drove it: the log is the fossil of the two work streams —
DEC-001…006 = core engine; DEC-012…028 = composability/SPDX; 007–010 = direction bridges.

| Destination | Entries |
|---|---|
| `development/notes/decision_log.md` | DEC-001, 002, **003 (Python/marker binding half)**, 004, 005, 006 |
| `research/notes/decision_log.md` | DEC-**003 (language-agnostic raw-byte hashing principle half)**, 007, 008, 009, 010 (direction; AC-001/002/014/015/016 seam-footprint stays in the Development design docs), 012, 013, 014, 015, 016, 017, 018, 019, 020, 021, 022, 023, 024, 025, 026, 027, 028 |

- **DEC-003 is the one entry split across both files** (principle → Research, binding →
  Development); exact clause cut shown at apply time for review.
- **Master index** (`DEC-id → stage/file → one-liner`, with supersession arrows as
  cross-file links) lives in the cross-cutting area — final path with item 6.
- **Funnel:** no whole DEC; the "still-open / edge-case / GAPS" sub-items embedded in
  many DECs are harvested during funnel seeding (item 5).

### All map items settled (2026-06-27)

Items 1–6 ratified and logged above. The map is the plan; the apply log below records
execution.

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

## Process

propose → ratify (mark the row Settled) → log (update this doc) → apply (`git mv`).
No bulk reorganization; ratify and move one stage/artifact at a time.
