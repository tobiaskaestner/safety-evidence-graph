# SEG — OSS Tool Landscape (comparison / categorization work packages)

**What this is.** The comparison/categorization of open-source docs-as-code
traceability & assurance tools, organized as **one resumable work package (WP) per
tool**. Operating mode: **the human drives, the agent co-drives/steers**; each WP is
self-contained so a session can break after any WP and resume later. Findings are
recorded *in this note* (per-WP Findings section + the matrix in §3) and only then
cited from the paper seed.

**Why (purpose, 2026-07-04).** Serves **Paper 1 (Prague)** first: ecosystem
positioning for an audience that uses these tools — which of them has a proof/
commitment object, a programmable verdict, a cross-project exchange story, an SPDX
connection. Serves **Paper 2** second: the facet-*bundling* analysis and the
still-standing suspicion-lifecycle novelty check (`seg_paper_seed.md` §8). Supersedes
the browser-era Doorstop/OFT work packages, which were never run and did not survive
the repo migration (only their goals did — paper seed §8, `seg_prior_art.md`
closest-applied section).

**Standing caution.** Everything below about StrictDoc and BASIL is *unverified
recollection or user-provided context* until its WP is run. Verify against the tool's
own repo/docs/behaviour before any claim hardens; the first question of every WP is
"is the tool what we think it is?"

---

## 1. The tool set

| Tool | Why it is in | Known ecosystem anchor (verify in WP) |
|---|---|---|
| Doorstop | Closest applied prior art (redrawn boundary, paper seed §2) | RTEMS, Space ROS |
| OpenFastTrace (OFT) | Closest applied prior art; the standing §8 semantics check | itsallcode; OSS safety projects |
| StrictDoc | New candidate (2026-07-04) | Used in the Zephyr project (user-provided — verify) |
| BASIL | New candidate (2026-07-04) | ELISA (elisa-tech/basil) — the community driving the SPDX FuSa profile |
| sphinx-needs | Same niche; used by SEG itself (reqs worktree, Phase B) | Sphinx docs-as-code world |

## 2. Comparison axes

Derived from the redrawn novelty boundary (paper seed §3) and the facet vocabulary —
established SEG/literature terms only:

- **A1 — Item model & identity.** Typed items? ID scheme? Storage format
  (YAML/text/DB)? VCS-native or app/DB-backed?
- **A2 — Content fingerprinting & field selection.** Any content hash? Over which
  fields (cf. Doorstop's normative-fields SHA-256; SEG's `hash_fields` vs `tracked`)?
- **A3 — Change reaction (the drift analog).** Break-on-change? Review stamps /
  affirmation? Suspect marking? *Transitive* propagation, and does it auto-clear on
  re-check? (OFT WP carries the standing paper-seed §8 verification.)
- **A4 — Coverage/validity semantics.** What question does the tool answer, and is it
  *hardwired* ("is everything covered?") or *programmable* (user-authored validity)?
- **A5 — Whole-case commitment / proof object.** Any single recomputable commitment
  over the whole graph? Any sealed, independently verifiable proof artifact?
- **A6 — Cross-project exchange & composition.** Import/export formats (ReqIF, SPDX,
  needs.json, …)? Any story for relying on another project's results?
- **A7 — Ecosystem position.** Who uses it; which community maintains it; adjacency
  to Zephyr / ELISA / SPDX.
- **A8 — Architecture/statefulness.** Stateless recompute-every-run (OFT-style) vs
  stored state (DB, stamps); web app vs CLI vs doc generator.

Axes A2–A5 carry Paper 2 (facet bundling, novelty); A6–A7 carry Paper 1 (Prague).

## 3. The matrix (fill per WP; cite the WP's Findings for every cell)

| Axis | Doorstop | OFT | StrictDoc | BASIL | sphinx-needs |
|---|---|---|---|---|---|
| A1 identity | typed YAML items per doc dir; links untyped `UID: stamp`, typed only by target doc (P1); cross-doc links first-class (P2) | | | | |
| A2 fingerprint | item stamp over text/ref/links/extended-reviewed attrs; committed/tracked split for extended attrs (P5/P6); source refs NOT content-bound — opt-in sha is review bookkeeping (P8) | | | | |
| A3 change/drift | one-hop, parent-only suspicion (P3/P4); no transitive propagation, auto-clear vacuous (P7); manual link-clear + item-review | | | | |
| A4 verdict | hardwired checks; `item_validator` = per-item arbitrary-Python plugin, no rule language (P9) | | | | |
| A5 commitment/proof | absent — publish = HTML/CSV report, no stamps/hash/signature (P10) | | | | |
| A6 exchange | none observed (publish/export are reports; import/export not deep-probed) | | | | |
| A7 ecosystem | RTEMS, Space ROS (prior-art record, not spike-verified) | | | | |
| A8 architecture | CLI over VCS working copy; stamps stored in item YAML; stateless recompute vs stamps; auto-stages edits into git index | | | | |

---

## 4. Work packages

Template per WP: **Status** (open / in progress / done + date) · **Goal** ·
**Questions** · **Method** · **Findings** (empty until run). Run order is a
suggestion; any order works. Small fixtures live under
`research/prototypes/tool-landscape/<tool>/` (create on first use).

**Recovered spike kits (2026-07-04).** The browser-era Doorstop/OFT work packages
*did* survive and are loaded at `research/spikes/{doorstop,oft}/` — ready fixtures
mirroring the SEG worked fragment (`seg_definition_language.md` §2) plus
**pre-registered prediction sheets** (P1–P10, O0–O8) with confidence levels and a
RESULTS template each. WP-1/WP-2 below now *execute those kits*; the kits'
PREDICTIONS.md are pre-registered — **do not edit during execution**. Their "table
cell" pointers refer to the pre-migration paper's §3 table; those cells now land in
this note's §3 matrix. Raw output is pasted into the kit's RESULTS.md during the run;
the settled verdicts/cells are then transcribed into the WP's Findings here (this
note is the record of record).

### WP-1 — Doorstop
**Status:** done (2026-07-04, P1–P10; ingest sketch still open)
**Goal.** Verify the mechanics the paper cites (fingerprint, stamps, suspicion) via
the recovered kit; then sketch whether SEG could ingest a Doorstop tree (seed §8).
**Questions.** The kit's pre-registered **P1–P10**
(`research/spikes/doorstop/PREDICTIONS.md`) supersede the regenerated questions —
they cover link typing (P1/P2), suspect mechanics incl. the one-sidedness and
transitivity probes (P3–P7), source-content drift via `ref` (P8), verdict
programmability (P9), and publish-vs-proof (P10). Notes:
- **P2 is already REFUTED** (setup, Doorstop v3.1): a cross-document link was
  accepted silently — re-confirm locally; the revised question is whether it stamps
  and participates in suspect detection.
- The ingest sketch (old Q4) stays as a follow-on after P1–P10.
- Probe→axis: P1/P2→A1 · P3–P6,P8→A2/A3 · P7→A3 · P9→A4 · P10→A5/A6.
**Method.** Per the kit README: `pip install doorstop` (kit rehearsed on v3.1 —
record the actual version), `doorstop` clean on the committed baseline, probes in
order, reset between destructive probes against HEAD (`git checkout HEAD -- <paths>`
— see the RESULTS.md reset gotcha). Budget: one evening; P9 is a 20-min doc read.
**Findings (run 2026-07-04, Doorstop 3.1 — full evidence in the kit's RESULTS.md).**
All ten probes settled: 8 confirmed, P2 refuted as pre-registered, P9 refuted on the
letter. Headlines:
- **Suspicion is one-hop and parent-only** (P3/P4/P7): a link stamp is a verbatim
  copy of the *target* item's review stamp — child-endpoint drift is invisible at the
  link level; no transitive propagation exists; clearing is two separate manual acts
  (link clear + item review), auto-clear vacuous. SEG deltas: two-endpoint `edgeHash`,
  derived transitive suspicion, auto-clear.
- **Referenced source content is never content-bound** (P8): the legacy `ref` checks
  keyword existence only (error if missing); the opt-in `references:` sha
  (`item_sha_required`) is *review-time bookkeeping* — validation never recomputes it,
  so a rewritten implementation body validates clean even with the sha enabled.
  Parser-as-locator without the hash half, now source- and behaviour-verified.
- **Field routing exists for extended attributes** (P5/P6): `attributes.reviewed` is
  a committed/tracked split; link stamps reuse the item stamp including extended
  reviewed attrs (no item/link divergence).
- **Cross-document links are first-class** (P2 refuted): tolerated, stamped,
  suspect-participating. The real wall is P1+P9: links are untyped `UID: stamp` pairs
  (foreign keys silently erased by normalization), and validity is hardwired — the
  `item_validator` extension (P9 surprise) is an arbitrary per-item Python plugin, not
  a rule language, which sharpens the DEC-007 auditability contrast.
- **Publish is a report, not a proof** (P10): HTML/CSV, no stamps/hashes/signature.
  Also: warnings don't gate the exit code, errors do.
Open remainder: the SEG-ingests-a-Doorstop-tree mapping sketch (old Q4).

### WP-2 — OpenFastTrace
**Status:** open — spike kit adopted (2026-07-04); **kit never executed anywhere**
(authored against the OFT 4.2.0 user guide; the jar host was unreachable in the
authoring sandbox), so O0 (import sanity) is genuinely open and format fixes are
themselves findings.
**Goal.** The standing paper-seed §8 check: pin down transitive-break +
re-trace-clear semantics, so the suspicion-lifecycle claim is worded exactly right.
**Questions.** The kit's pre-registered **O0–O8**
(`research/spikes/oft/PREDICTIONS.md`) supersede the regenerated questions:
- O1 + O3 answer the §8 gate (old Q1–Q3): O1 = deep-coverage defect propagates up
  (recursive verdict PRESENT — an SEG-parity cell, polarity coverage-not-taint);
  O3 = drift is a *manual two-sided revision counter* (content edits silent, bump ⇒
  Outdated) — no content hash. Re-trace-clear is implicit in statelessness; confirm.
- O4 answers the verdict-ruleset reproduction question (old Q4) as a time-boxed doc
  check (monotone `Needs` only; no negation, no user-defined relation).
- **Net additions the regenerated WP lacked:** O7 — TestOutcome is *unrepresentable*
  (no artifact type for a result; the evidence-subgraph wall) and O8 — ReqM2
  export/import is textual multi-source merge, i.e. *partial* on the composition
  axis, no scope commitment.
- Probe→axis: O0 sanity · O1,O4→A4 · O2,O6→A1 · O3→A2/A3 · O5,O7→A4/A5 · O8→A5/A6.
**Method.** Java 17+, `./run.sh` per the kit README (exit code is the verdict);
reset between probes via the kit's embedded git.
**Findings.** —

### WP-3 — StrictDoc
**Status:** open
**Goal.** Establish what StrictDoc actually is and does; verify the Zephyr connection
(motivating-instance adjacency for both papers).
**Questions.**
1. Verify the basics: storage format (SDoc?), item model, link model.
2. Any content hashing, change tracking, or review/approval state? (Expected: little —
   verify, don't assume.)
3. Coverage/validity: what checks does it run; hardwired or configurable?
4. Exchange: ReqIF? needs.json? SPDX? What does Zephyr use it for, concretely (which
   repo/branch — find the actual usage)?
**Method.** `pip install strictdoc`; init a sample project; exercise trace/export
commands. Locate Zephyr's StrictDoc usage in the Zephyr org (web check).
**Findings.** —

### WP-4 — BASIL
**Status:** open
**Goal.** Establish what BASIL is and does; position it against SEG for the ELISA/
SPDX-FuSa audience (the Prague paper's community).
**Questions.**
1. Verify the basics: architecture (web app + DB + REST API?), item model
   (spec-to-code/test "snippet" coverage?).
2. How is a claim of coverage recorded — asserted by a user, or computed? Any
   integrity binding to source content (hashes, pins)?
3. Evidence handling: how are test results attached; any drift notion when code moves
   under a mapped snippet?
4. Exchange/SPDX: any import/export; any stated relation to the SPDX FuSa profile or
   ELISA safety-case work?
**Method.** Likely the heaviest: clone elisa-tech/basil, try the containerized dev
setup (podman/docker); if deployment is disproportionate, fall back to a docs+source
read with findings marked *not exercised*.
**Findings.** —

### WP-5 — sphinx-needs
**Status:** open
**Goal.** Characterize the tool SEG itself uses for requirements (Phase B reqs
worktree) on the same axes — including the cross-project angle.
**Questions.**
1. Item model: need types, options, links — what is enforced vs convention?
2. Any content hash / change detection / review state on a need?
3. Validity: `needs` filters/warnings — what can a *user-authored* check express
   (closest thing to a programmable verdict in the set)?
4. Exchange: `needs.json` export / `external_needs` import — how far is that from a
   composition story (what integrity, if any, travels with it)?
**Method.** Already a project dependency; exercise on a scratch Sphinx project or the
reqs worktree (read-only). Docs + behaviour.
**Findings.** —

---

## 5. Output & downstream use

- Each WP fills its Findings + its matrix column; claims cite the WP section.
- When the matrix is full enough: distill (a) the Prague positioning paragraph
  (Paper 1 — A6/A7-led) and (b) the facet-bundling table (Paper 2 — A2–A5-led), and
  update `seg_prior_art.md` closest-applied + `seg_paper_seed.md` §2/§8 (retire the
  "hands-on check pending" caveat once WP-2 answers it).
- New citations to add on completion: StrictDoc, BASIL, sphinx-needs (repo+version,
  as with OFT).
