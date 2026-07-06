# TSF (trudag/dotstop) Spike — Pre-Registered Predictions (WP-7)

**Written before probe execution.** Baseline rehearsed on **trudag 0.4.0**
(distribution `trustable`, installed from gitlab.eclipse.org/eclipse/tsf/tsf —
NOT on PyPI as `trudag`; pin the commit in RESULTS at execution time). Rehearsal
stopped deliberately *before* `publish`/`show-item`/`show-link` — anything that
reports per-link stored state is probe territory (T3/T5), not baseline.

**Recon facts predictions build on** (from docs-read 2026-07-06 +
baseline rehearsal only):
- trudag requires running **inside a git work tree** (`get_workdir` calls
  `git rev-parse --show-toplevel`).
- Items = `PREFIX-ID.md`, YAML frontmatter (`normative: true`, optional
  `references:` list) + markdown body; links live decoupled in `.dotstop.dot`.
- `.dotstop.dot` stores `sha` on **both nodes and edges** (confirmed at format
  level during rehearsal; behavior untested).
- `trudag score` on an unscored graph: "Score not provided for Item … Score set
  to zero", all items report `0.0; Missing` — the documented unscored-is-zero
  rule, confirmed live.
- CLI surface: init / add-item / create-item / create-link / set-item ("set
  status of item to reviewed") / set-link ("set link status … to LINKED") /
  score / publish / lint / export / import / remove-import / diff / plot /
  manage (deprecated).

**The fragment (recast as statements — see README):** EXP-SCHED (expectation,
root) ← ASSERT-LOCK ← {ASSERT-COOP, PREM-IMPL, PREM-TEST}; ASSERT-COOP ←
PREM-IMPL (multi-parent). PREM-IMPL references `src/scheduler.c`, PREM-TEST
references `tests/test_scheduler.py` (type `file`).

---

## T1 — Drift trigger & sidedness: two-sided, content-hash, no manual bump
**Prediction (high confidence — the drift-axis placement).** Editing the *child*
item's body flips the parent→child link out of its reviewed state; editing the
*parent* does the same — two-sided — and the trigger is the content hash alone
(no revision integer, no manual step; contrast OFT O3a). A whitespace-only edit
also trips it (hash over file bytes, no normalization) — weaker confidence on
this sub-point; Doorstop normalizes before stamping, dotstop may not.
**Probe.** Review/clear a link (set-item/set-link), edit child body → observe
link + item status; reset; edit parent → observe; reset; whitespace-only edit →
observe. Record *what statuses exist* (suspect vocabulary).
**Consequence if confirmed:** TSF occupies the **two-sided content hash** point
on the drift axis — `seg_tool_comparison.md` §1's endpoint must be caveated:
SEG's remaining drift delta is granularity (raw byte spans vs whole item file)
plus everything T2 measures.

## T2 — Suspicion closure: local only; no transitive propagation, no auto-clear
**Prediction (medium confidence).** A changed item makes *adjacent* links (and
itself) suspect; nothing propagates further up the DAG as stored state (no
transitive suspect closure like SEG's DEC-005 derivation), and there is no
auto-clear on descendant re-review — each affected link/item is cleared
manually one at a time. NB the *score* recomputes globally every run
(stateless, OFT-like), so suspicion may be *implicitly* transitive through
score effects only if T5's gating holds — keep the two channels separate when
recording.
**Probe.** Three-level chain EXP→ASSERT→PREM: review everything, edit PREM →
inspect status of the EXP→ASSERT link (expect: untouched); re-review the
changed leaf → check whether anything else clears by itself.

## T3 — Affirmation storage: the link sha IS the stamp, two-sided, content-bound
**Prediction (medium confidence).** "Reviewed" persists as the recorded hash in
`.dotstop.dot` (item sha; link sha = hash over both endpoints' contents —
docs-read: "hash of concatenated file contents"); review status is *derived* by
comparing stored vs recomputed sha (Doorstop-stamp-like mechanics but
two-sided). No separate reviewer/date/actor field — the affirmation has no
identity or event record (contrast SEG's affirmation events; grep for any
author/timestamp to be sure).
**Probe.** set-item/set-link on a suspect pair → diff `.dotstop.dot` before/
after; grep the tree for any actor/timestamp trace; establish whether the link
sha covers both endpoint contents (edit each side, watch which shas change).

## T4 — Source binding: locator-WITH-hash — the first in the applied set
**Prediction (medium-high confidence — the second headline).** A `type: file`
reference content-binds the artifact: after editing `src/scheduler.c`, the
referencing premise (PREM-IMPL) becomes suspect / flagged for re-review. If
confirmed, TSF is the **only tool in the WP set whose source references are
content-bound** (Doorstop P8: bookkeeping only; StrictDoc S5: droppable ranges;
sphinx-needs N5: nothing) — locator-with-hash, at *file* granularity. SEG's
delta narrows to **span** granularity (DEC-003 raw-byte-span) + the parser-
locates-only TCB argument. Source-span reference type exists per docs — test
it; predict file-type works, span-type granularity/robustness unknown.
**Probe.** Edit the referenced C file (function body change) → score/status of
PREM-IMPL; try a `source-span`-type reference if the format is discoverable;
note failure modes.

## T5 — Scoring: mean-propagation reproducible; suspect state does NOT gate the score
**Prediction (low-to-medium confidence — the §15-hypothesis test; genuinely
uncertain, informative either way).** Leaf scores (however set — SME value in
frontmatter or via CLI; mechanism to be discovered) propagate as the
documented mean/weighted recurrence, reproducible by hand on the 5-node
fragment. The interesting half: **review/suspect status and score are parallel
channels** — a suspect item still contributes its stale score (status reported
alongside, not multiplied in). If instead suspicion zeroes or blocks the score,
TSF itself realizes the design summary §15 hypothesis ("integrity is a
precondition checker for trust scoring") — record which.
**Probe.** Set leaf scores, hand-compute expected root score, compare; make one
leaf suspect (T1 edit) without re-scoring → re-run score → does the number
change/drop/error?

## T6 — Commitment: no global recomputable root, no seal
**Prediction (medium-high confidence).** Neither `.dotstop.dot` nor the
`export`ed artifact carries a single commitment over the whole graph (contrast
rtemsspec's "overall item cache hash", WP-6!) — no signature, no third-party
verification story; "immutable once published" is convention. Per-item and
per-link shas exist; nothing aggregates them.
**Probe.** `export` the artifact → inspect for any root hash/signature field;
grep the package source for an aggregate-hash computation (sha512/sorted/
concat patterns); tamper with an exported artifact field → does `import`
notice?

## T7 — Composition: pre-computed scores travel and are trusted (record, not recompute)
**Prediction (medium confidence — the record-vs-recompute foil).** The exported
"resolved graph" carries scores; `import` under a namespace makes them usable
downstream *as recorded* — the consumer does not (and cannot) recompute them,
since the upstream working graph isn't shipped. Needs-graph items ("Assumptions
of Use") import as local obligations, but there is no discharge check bound to
a version pin (contrast DEC-023) and no seal to break on a dropped assumption
(contrast DEC-020): deleting a needs item downstream is predicted silent.
Drift of referenced remote items "prompts a review" per docs — verify what
that concretely does.
**Probe.** Export from the rehearsal project; import into a second scratch
project under a namespace; inspect what arrived (scores? hashes? needs items);
delete/ignore an imported needs item → observe; change the upstream artifact
file → re-something → observe the "prompts a review" claim.

## T8 — Analysis probe (no tool execution): SEG hosts / generates TSF
**Prediction (medium confidence; may outlive the spike).** (a) *Hosting:* TSF's
model fits a SEG definition — statement node type (content = the .md body),
one `supports` edge type (binds both endpoints, propagates suspicion,
acyclic), references as source binding. (b) *Generation (the sharpened form,
duality note §6.4):* the score recurrence is expressible as a clingo ruleset
over scaled integers (`#sum` aggregates, weights 1/outdegree as rational
scaling) — SEG emits a TSF-shaped argument view (derivation DAG + evaluation)
as a write-only projection. Deliverable: a definition sketch + a runnable
clingo fragment reproducing T5's hand-computed root score. Strain to record
honestly: real-valued calibration, and both obstructions in
`seg_tsf_duality.md` §6.5.
**Probe.** Author both sketches against the T5 numbers; note exactly where
expressiveness strains. Cross-check the AdvoCATE/Rushby kin gap
(`seg_prior_art.md` gaps list) before wording any novelty claim.

---

## Scoring
Per probe in RESULTS.md (section format): verdict / observed / matrix-cell
impact. Synthesis targets: **drift axis** (predict: two-sided content hash at
item-file granularity → §1 endpoint caveat lands), **stored vs derived**
(predict: stored affirmation, NO derived closure → SEG's "alone in combining"
claim survives, narrowed to the derived half), **evidence wall** (crossed:
values consumed by the score — first non-SEG crossing; freshness = T5's
gating answer), **source binding** (predict: first locator-with-hash in the
set; SEG delta = span granularity), **commitment** (predict: absent despite
ubiquitous hashing — the rtemsspec contrast), **exchange** (predict: artifact
with traveling scores — the record-vs-recompute foil for Paper 1).
