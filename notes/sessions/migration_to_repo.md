# Migration to the stage pipeline — migration map (record)

The ratified source→destination map for the four-stage reorg (funnel → research →
prototype → development). Split out of `notes/seg_pipeline_model.md` (which keeps the
model, target layout, and the apply log); this file holds the detailed map that drove
the moves. Items 1–6 ratified 2026-06-27; see the pipeline doc's `## Apply phase` for
execution.

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
| Root `README.md`, `BUNDLE_CONTENTS.md`, `CLAUDE.md`, `requirements.txt`, `.gitignore` | stay at root (cross-cutting) — *but `README.md` later reclassified as prototype-specific and moved into `research/prototypes/spdx-v3.1-exchange/` (see tidy-ups below); `BUNDLE_CONTENTS.md` archived* |
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

