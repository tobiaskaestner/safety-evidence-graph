# Doorstop Spike — Pre-Registered Predictions (A1)

**Written before probe execution** (setup rehearsed on Doorstop v3.1 in a
sandbox; only the baseline was built — probes P3–P10 have NOT been run).
Check `doorstop --version` locally; behavior may differ across versions.

**The fragment under test** (from `seg_definition_language.md` §2, plus one
refines hop for the transitivity probe):

```
SYS001  (system requirement)            ← refines        ← REQ001
REQ001  hash_fields≈[text, rationale]   ← answers_to     ← ADR001
ADR001  hash_fields≈[header, text], tracked≈[status]
IMPL001 file_span≈ref keyword            implements→REQ001, adheres_to→ADR001
```

Doorstop mapping: documents SYS → REQ → {ADR, IMPL}; `attributes.reviewed:
[rationale]` on REQ (committed extended attr); `status` on ADR deliberately
NOT review-contributing (tracked analogue); IMPL `ref` points at a keyword in
`src/scheduler.c`.

**Workflow:** baseline is git-committed and fully reviewed/cleared. Run probes
in order; between probes, reset with `git checkout -- .` (and re-run
`doorstop` to confirm clean). Record outcomes in `RESULTS.md`.

---

## P1 — Links are untyped

**Prediction (high confidence).** A link is `{UID: stamp}` and nothing else.
`implements` vs `adheres_to` are distinguishable only by the *document* the
target lives in; there is no slot for per-link type, let alone SEG facets
(`binds`/`propagates`/`fingerprint`).
**Probe.** Inspect `impl/IMPL001.yml` links (both already present). Optionally
add an extra key to a link mapping and run `doorstop` — expect it ignored or
rejected.
**Table cell if confirmed.** Doorstop: edge typing = by-document only; facets =
absent.

## P2 — Cross-document links (the multi-parent wall)

**Original prediction.** Doorstop enforces the document tree; linking IMPL001
→ ADR001 (ADR is not IMPL's parent document) yields a warning or error.
**Status: REFUTED DURING SETUP (v3.1).** The link was accepted silently and
validation stayed clean. **Re-confirm locally**, and check `doorstop -v` and
`doorstop publish` output for buried warnings.
**Revised question for the probe.** Even if tolerated: does the cross-document
link get a stamp, and does it participate in suspect detection (P3) like a
tree link? If yes, the "tree-only" wall is softer than assumed and the table
cell must say so — the *real* wall then rests on P1 (untyped) + P9 (no
semantics over the link).

## P3 — Parent content change ⇒ suspect links (the DOORS behavior)

**Prediction (high confidence).** Edit REQ001 `text` → REQ001 becomes
unreviewed, and the links ADR001→REQ001 and IMPL001→REQ001 are both reported
**suspect**. This is hash-seeded, one-hop direct suspicion — Doorstop has it.
**Probe.** Edit the text, run `doorstop`, read the warnings.
**Table cell.** Direct suspicion: present (content-hash stamps).

## P4 — Child content change ⇒ link NOT suspect (one-sidedness)

**Prediction (high confidence; the headline probe).** Edit IMPL001 `text` →
IMPL001 goes unreviewed, but IMPL001→REQ001 is **not** suspect: the link stamp
records the *parent's* content only. A drifted source endpoint passes
unnoticed at the link level. SEG's `edgeHash` covers `from ‖ to ‖ type ‖
h(from) ‖ h(to)` — both endpoints.
**Probe.** Edit IMPL001 text, run `doorstop`, grep for suspect.
**Table cell.** edgeHash analogue: one-sided (parent-only).

## P5 — Tracked-field analogue

**Prediction (high confidence).** Change ADR001 `status: proposed → accepted`
→ no unreviewed, no suspect, validation clean. Doorstop's
`attributes.reviewed` allowlist IS a field-routing split (committed vs
tracked) for extended attributes.
**Probe.** Edit status, run `doorstop`.
**Table cell.** Field roles: partially present (extended attrs only; `text`/
`header`/`ref` routing is fixed, not author-controlled — note which built-ins
turn out to be stamped, see P6/P8).

## P6 — Committed extended attribute reaches the link stamp?

**Prediction (MEDIUM confidence — genuinely uncertain).** Change REQ001
`rationale` → REQ001 goes unreviewed (rationale is in `attributes.reviewed`).
Uncertain half: do the *child links* (ADR001→REQ001, IMPL001→REQ001) also go
suspect — i.e., does the link stamp incorporate extended reviewed attributes,
or only core fields? Lean: yes, link stamps reuse the item stamp. If NO: a
finding — Doorstop's committed-field set differs between item review and link
suspicion, a subtlety SEG's single nodeHash avoids.
**Probe.** Edit rationale, run `doorstop`.

## P7 — No transitive suspicion

**Prediction (high confidence).** Edit SYS001 `text` → REQ001→SYS001 goes
suspect; ADR001→REQ001 and IMPL001→REQ001 stay clean. The taint does not
propagate; the two-hop derivation SEG computes as a closure is absent.
Clearing (`doorstop clear REQ001 SYS001` or interactive review) removes the
suspect — manual re-affirmation, equivalent to SEG's, but nothing transitive
ever existed to auto-clear.
**Probe.** Edit SYS001, run `doorstop`, inspect which links are flagged.
**Table cell.** Transitive suspicion: absent. Auto-clear: vacuous (nothing
derived).

## P8 — Referenced source content is not fingerprinted

**Prediction (MEDIUM confidence).** `ref` is a *locator only*: Doorstop checks
the keyword exists somewhere, it does not hash the file or span. Editing the
body of `src/scheduler.c` (keeping the keyword line) → no unreviewed, no
suspect: **implementation content can drift invisibly**. Deleting the keyword
line → a validation error (ref not found), i.e. existence is checked, content
is not.
**Probe.** Two edits to `src/scheduler.c`, run `doorstop` after each.
**Table cell if confirmed.** This is the sharpest cell: Doorstop has SEG's
parser-as-locator *without the hash half* — location discipline, no content
commitment. (Also check the newer `references:` list syntax in the docs for a
sha option before finalizing the cell — 15 min doc read, no build.)

## P9 — No custom verdict semantics

**Prediction (high confidence).** There is no mechanism — config, hook, or
rule language — to express `impl_violates_adr` ("an implementation of R
violates if some ADR answers R and the implementation lacks adheres_to to
it"). Doorstop's checks are fixed: links exist, items reviewed, links
cleared, refs found. Anything else means external Python against the doorstop
API — i.e., writing SEG's verdict layer yourself.
**Probe.** Time-boxed 20-minute documentation read. Do NOT build the
workaround.
**Table cell.** Verdict semantics: fixed; user-definable rules: absent.

## P10 — Publish ≠ proof

**Prediction (high confidence).** `doorstop publish all ./pub` emits
human-readable reports (HTML/MD/CSV). No commitment artifact, no signature,
no envelope a third party can verify without trusting the working copy.
Verdict reproducibility in SEG's sense (recompute from sealed proof alone) has
no counterpart.
**Probe.** Publish, inspect output.
**Table cell.** Sealed proofs: absent. Composition: absent (nothing to
compose).

---

## Scoring

For each probe record in `RESULTS.md`: observed behavior (paste the relevant
doorstop output line), verdict (CONFIRMED / REFUTED / SURPRISE), and the
comparison-table cell it settles. Refutations are wins: P2 already moved a
cell, and the paper's §3 is only as strong as the cells we tried to break.
