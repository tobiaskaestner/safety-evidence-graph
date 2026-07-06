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
| TSF (trudag/dotstop) | New candidate (2026-07-06) — the only *framework*-level entrant; closest structural overlap found (two-sided hashed links, suspect-until-review, scored evidence) | Eclipse TSF project (Codethink lineage); same Eclipse/LF safety cluster as the adoption table |

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
| A1 identity | typed YAML items per doc dir; links untyped `UID: stamp`, typed only by target doc (P1); cross-doc links first-class (P2) | artifact-type-in-ID (`req~name~rev`); typed coverage links; one auto-named impl item per tag (O2) | SDoc docs; **user-defined element tags** + typed fields via [GRAMMAR] (S2); relations typed {Parent,Child,File} + declared ROLE — validated, carried, semantics-free (S1); impl = annotated source range, not a node | | rst directives; config-defined need types + named directed link vocabulary w/ auto back-links, dead-link warnings (N1) |
| A2 fingerprint | item stamp over text/ref/links/extended-reviewed attrs; committed/tracked split for extended attrs (P5/P6); source refs NOT content-bound — opt-in sha is review bookkeeping (P8) | none — no content hash anywhere; manual revision integer is the only anchor (O3a) | none stored; MID = uuid4 anchor; content-md5 exists only for the on-demand DIFF report + cache (S4); no field-role split | | none — needs.json exports full content unhashed; no field-role split (N4) |
| A3 change/drift | one-hop, parent-only suspicion (P3/P4); no transitive propagation, auto-clear vacuous (P7); manual link-clear + item-review | manual-trigger, two-sided, whole-chain break (dual `orphaned`+`outdated`, O3b); re-trace auto-clears; nothing stored, no affirmation concept | **none** — no review state, no pin, edits silent (S3); markers silently droppable (S5); DIFF = on-demand two-tree changelog | | **none, incl. cross-project** — edits silent (N4); rewritten external need rebuilds clean (N7); dead-link warnings only |
| A4 verdict | hardwired checks; `item_validator` = per-item arbitrary-Python plugin, no rule language (P9) | recursive deep coverage PRESENT (O1, stateless fixpoint, coverage polarity); no rule/plugin/hook facility at all (O4); TestOutcome unrepresentable (O7) | no verdict at all — coverage screens are display-only (S6); **TEST_RESULT nodes with PASSED/FAILED representable** (S7, unique) but nothing consumes them; whole-graph Python plugin hook (S9) | | **declarative bounded-depth shape validation, SHACL-cited severities** (N2); per-need eval constraints, derived state exports (N3); no recursion/fixpoint (hard nest bound), no verdict object |
| A5 commitment/proof | absent — publish = HTML/CSV report, no stamps/hash/signature (P10) | absent — reports carry no integrity artifact (O8) | absent — HTML/JSON/ReqIF carry no integrity artifact (S8) | | absent (N8) |
| A6 exchange | none observed (publish/export are reports; import/export not deep-probed) | partial — ReqM2 XML exchange with `dstversion` pins, but textual: no content binding, no scope commitment (O8) | richest in set — ReqIF import+export, JSON, Excel; roles survive; textual, no commitment (S8) | | needs.json + needimport + **needs_external_needs by-reference cross-project links** (unique) — zero integrity/pin (N7) |
| A7 ecosystem | Space ROS (docs-verified); **RTEMS evaluated-and-rejected** — six limitations mapping onto P1/P9 (→ comparison §3) | Exasol projects; **Eclipse Ankaios** (docs-verified) | **Zephyr verified locally** (doc/reqmgmt); linux-strictdoc PoC (ELISA SPDX-Req tags) | ELISA (Red Hat; deployed instance) | Eclipse S-CORE (docs-verified); **used by SEG itself** (Phase-B reqs worktree) — adoption details: `seg_tool_comparison.md` §2 |
| A8 architecture | CLI over VCS working copy; stamps stored in item YAML; stateless recompute vs stamps; auto-stages edits into git index | stateless CLI tracer (Java); recomputes every run from sources; exit code = verdict | static-site generator + web server (Python); stateless rebuild each export; documents incl. junit/gcov reports; errors gate exit, nothing else does | | Sphinx extension; build-time, stateless; jsonschema_rs validation each build; `-W` gates |

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
**Status:** done (2026-07-04, O0–O8 on OFT 4.5.0 / Java 25; zero format fixes —
the docs-authored kit parsed first try). **Settles the standing paper-seed §8
suspicion-lifecycle check.** Full evidence in the kit's RESULTS.md. Headlines:
- **The recursive verdict IS present** (O1): deep coverage is a stateless fixpoint;
  a missing tag propagates `not ok` whole-chain, including upward. SEG's novelty is
  therefore NOT the fixpoint — it is content-bound two-sided affirmation +
  user-definable stratified semantics + the evidence subgraph (O7).
- **Drift = honor-system integer, but two-sided when triggered** (O3): content edits
  with the revision kept are silent (no content hash anywhere); a bump gives dual
  `orphaned`/`outdated` statuses on every stale coverer, whole-chain break, and
  re-trace clears everything with no stored state — **no affirmation concept exists**.
  The three-setting drift axis (Doorstop one-sided hash / OFT two-sided counter /
  SEG two-sided hash) is now evidence-backed.
- **No verdict programmability at all** (O4): the CLI is `trace`+`convert`; no rule,
  plugin, or hook facility — stricter than Doorstop's Python escape hatch.
- **TestOutcome is unrepresentable** (O5/O6/O7): no result field exists in CLI,
  format, or aspec schema; Status is stored but inert; the only workaround exiles
  pass/fail into CI glue. The design/evidence split is absent in both tools.
- **ReqM2 is a real exchange format, but textual** (O8): `dstversion` pins travel;
  no content binding, no scope commitment, no hash/signature anywhere.
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
**Status:** done (2026-07-04, S1–S9 on 0.25.0; kit commit 5486f76 + format fixes).
**Findings (full evidence in the kit's RESULTS.md).** 7 confirmed, S9 refuted on the
letter (a whole-graph Python plugin hook exists), S4 confirmed with a surprise
(content-md5 powers the on-demand DIFF changelog — a report, not an integrity
mechanism). Headlines:
- **The grammar is a real, enforced structural definition language** (S2:
  `SingleChoice`, required fields, custom element tags, declared relation roles — all
  parse-time-enforced; roles carried through JSON/ReqIF but semantics-free, S1). The
  applied existence proof for SEG contribution #4's *structural* half; the delta is
  the definition compiling to verdict + commitment machinery.
- **Drift axis position: none** (S3: no review state, no stamps, no pin; S5: source
  markers are content-blind locators, silently droppable).
- **The evidence wall relocates** (S7): JUnit/Robot/gcov readers make test results
  *representable* as TEST_RESULT nodes with PASSED/FAILED — unique in the WP set —
  but nothing consumes pass/fail (no roll-up, exit 0 on FAILED) and binding is
  path-only (no staleness). Representation present; semantics + freshness absent.
- **No verdict of any kind** (S6: report-only coverage screens; weaker than OFT's
  hardwired check) — extensibility = whole-graph arbitrary-Python plugin (S9).
- **Exchange: richest in the set** (S8: ReqIF both directions + JSON; textual, zero
  integrity artifacts).
Zephyr connection verified locally: `doc/reqmgmt` (shared `.sgra` grammar, `Parent`
relations, `ZEP-SRS-` UIDs, pinned `strictdoc>=0.9.1`).
**Goal.** Establish what StrictDoc actually is and does; verify the Zephyr connection
(motivating-instance adjacency for both papers).
**Questions.** The kit's pre-registered **S1–S9**
(`research/spikes/strictdoc/PREDICTIONS.md`) supersede the regenerated questions.
Known already from kit rehearsal (0.25.0) + the Zephyr repo
(`/wrk/z/ws-safety/doc/reqmgmt`, pins `strictdoc>=0.9.1`): SDoc format with a
**user-definable [GRAMMAR]** (typed fields incl. `SingleChoice`, required-ness, custom
element tags, declared relation roles) — Zephyr imports a shared `.sgra` grammar and
uses `Parent` relations with `ZEP-SRS-` UIDs. Headline predictions: the grammar is a
real *structural* definition→validator story (S2 — applied-field half of SEG
contribution #4, minus semantics); test reports are *representable* (JUnit/Robot
readers ship) with the evidence wall relocating to semantics+freshness (S7); drift
axis position = none at all (S3).
**Method.** Run the kit per its README (`strictdoc export`, probes in order, reset
`git checkout HEAD -- docs/ src/ strictdoc.toml`).
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
**Status:** done (2026-07-04, N1–N8 on 8.1.1/Sphinx 8.2.3; kit commit deeb395).
**Findings (full evidence in the kit's RESULTS.md).** All eight confirmed as
pre-registered. Headlines:
- **The schema system is explicitly SHACL-derived** (N2 — citable verbatim:
  `SeverityEnum` "levels are derived from the SHACL specification" + W3C URL):
  declarative, typed link-target validation across the graph
  (select/local/network, minContains, structured violation reports, `-W` gates) —
  with a **hard non-recursion bound** (`network_max_nest_level`). The applied field
  reaches SEG's shapes layer and stops exactly below the DEC-007
  recursive-stratified island.
- **Per-need eval-string checks whose derived state exports** (N3:
  `constraints_passed` persists into needs.json) — single-need scope, no closure.
- **Drift axis: none, including cross-project** (N4/N7): content edits silent, no
  stored state; `needs_external_needs` links by reference and a completely rewritten
  external guarantee rebuilds with zero warnings — the exact gap the sealed exchange
  fills.
- **No source binding at all** (N5) — SEG's own Phase-B usage pairs sphinx-needs
  with SEG's extractor precisely to supply that half.
- Evidence by convention only (N6); no commitment (N8); richest link-type
  *vocabulary* in the set with referential-integrity warnings (N1).

---

### WP-6 — RTEMS specification items / rtemsspec (bounded read; no kit, no matrix column)
**Status:** done (2026-07-04, source-read @ 8ace630; commit 2ff42a4)
**Goal.** Characterize the *churn outcome*: what RTEMS built after rejecting Doorstop
(comparison doc §3) — extends the case study from "why they left" to "what they built".
Not a candidate tool (RTEMS-internal toolchain), so no spike kit and no matrix column;
findings land in `seg_tool_comparison.md` §3.
**Questions.**
1. Link model: typed links with roles/attributes (`role`, `enabled-by`) — the P1 wall?
2. Type-based validation rules: declarative or Python — the P9 wall; new point on the
   extensibility spectrum?
3. Any content-hash / stamp / drift mechanism retained from Doorstop — or did drift
   detection get dropped with the tool?
4. Spec→code/tests/doc generation — the "definition compiles to artifacts" story
   (contribution-#4 adjacency).
**Method.** Docs + source read: RTEMS Software Engineering manual (eng/req/items.html,
eng/req/tooling.html) + `rtemsspec` in rtems-central (shallow clone, read-only).
Findings marked *not exercised* (no build).
**Findings (2026-07-04, rtems-central @ 8ace630; source-read, not exercised).**
1. **Q1 — the P1 wall is fixed:** every link is `{role, uid}` (`interface-function`,
   `constraint`, `interface-placement`, …), plus refinement links carrying
   `spec-key`/`spec-value`; items carry `enabled-by` expressions.
2. **Q2 — a self-describing declarative type system:** `type: spec` items define item
   types (typed attributes, `mandatory-attributes`, a `spec-refinement` hierarchy
   keyed on attribute values); `specverify.py` is a *generic interpreter* of those
   items. The meta-model is dogfooded in its own item format — the applied
   realization of DEC-007's "express the built-in type as the first definition",
   structural half only (no verdict rules; coverage/completeness checks live in
   hardcoded tooling scripts).
3. **Q3 — content hashing retained and upgraded, but repurposed:** per-item SHA-256
   (`items.py data_digest`, canonical over the item data); **links store the digest
   of the linked item** and `has_changed` fires on mismatch (packagebuild); and an
   **"overall item cache hash"** — SHA-512 over the *sorted digests of all items* —
   a global, flat, recomputable commitment over the spec set (rtems.py). All of it
   serves *build invalidation* in the qualification-data-package pipeline. No
   review/affirmation, no suspect state, no seal (grep: none).
4. **Q4 — definition compiles to artifacts:** `spec2modules.py` /
   `rtems_spec_to_x.py` / `validation.py` generate C interfaces, validation test
   code, and docs from items; `runtests`/`testoutputparser` execute and parse test
   outputs inside the pipeline (their relation to any requirement-level verdict was
   not examined in this bounded read). Compile targets are code/tests/docs — not
   validators or verdicts.

### WP-7 — Eclipse TSF / trudag / dotstop (framework-level comparison + spike)
**Status:** registered 2026-07-06; docs-read done (preliminary findings below,
*not exercised*); spike agreed — kit to be pre-registered before execution.
**Goal.** Position SEG against the one *framework*-level entrant: TSF is not another
point on the tool spectra but the other pole of the same design space — an argument
graph with artifacts at the fringe, vs SEG's artifact graph with the argument at the
fringe. Two deliverables beyond the usual matrix column: (a) settle the **drift-axis
endpoint caveat** — `seg_tool_comparison.md` §1 currently ends the drift axis at
"two-sided content hash (SEG `edgeHash`)" as SEG-only, and dotstop's hashed links sit
at or near that point; (b) update the design summary's **§15 TSF hypothesis**
("integrity is a precondition checker for trust scoring") — written before TSF grew
its own hashing layer, superseded by the instance-of-meta-model reading below.
**Preliminary (docs-read, pages.eclipse.dev retrieved 2026-07-06 — verify all in spike).**
- Model: **Statements** (truth-apt) linked by logical support into a DAG; positional
  taxonomy (Expectation = root, Premise = leaf, Assertion = between); artifacts attach
  only at leaves via hashed References (file / gitlab / source-span / artifact-subgraph)
  or algorithmic Validations; fixed normative content on top (tenets TT-*, TA-*).
- Overlap cluster (unmatched by any WP-1…5 tool): dotstop links carry
  `sha = hash of concatenated file contents` (**two-sided content hash**); "any change
  to a Statement makes it Suspect, until it is reviewed by a human" (**suspect +
  affirmation**); "ultimately humans, not machines, have to decide whether the Links
  are valid" (**the FSM doctrine, stated independently**); leaf scores are *consumed*
  by a roll-up (**crosses the evidence wall**); remote graphs split into Resolved
  (frozen, pre-computed) + **Needs graph ("Assumptions of Use")** under namespaced
  import (**the `(G, A, I)` skeleton**).
- Divergence cluster: aggregation is probabilistic-quantitative (calibrated SME
  scores, mean/weighted-sum propagation) vs SEG's logical-qualitative verdicts — and
  TSF's *declared* link semantics (implication) does not match its *score* semantics
  (mean); **pre-computed scores travel** in the resolved graph (record) vs SEG's
  verdict-never-travels (recompute) — the sharpest single contrast; TSF ships content
  (tenet/TA catalogue) where SEG ships an empty meta-model; no global seal /
  third-party verification story found (absence unconfirmed).
- Lineage: dotstop is Doorstop-descended ("fully deprecated doorstop as a viable
  backend") — a **second Doorstop-churn datapoint** after RTEMS (§3 of the comparison
  doc), and this one churned toward content-hashed links.
- The duality/lineage synthesis behind this WP is captured in
  **`seg_tsf_duality.md`** (argument pole vs artifact pole; record-vs-recompute and
  human-placement as forced consequences; the two-lineages convergence) — hypothesis
  status, cite only after the spike.
- Layering hypothesis to test: **TSF is a candidate instance of SEG's meta-model**
  (DEC-007) — statement types as node types, support as one hashed+affirmed edge type,
  `acyclic` on, scoring as the (hardwired) verdict-ruleset slot; the score recurrence
  looks expressible in clingo via scaled-integer `#sum` aggregates. Strain point:
  real-valued calibrated confidence — a Paper 2 open question (new facet or not?).
**Questions (probe seeds for the kit's PREDICTIONS.md).**
1. Drift trigger & sidedness: edit each endpoint of a link in turn — does the link go
   suspect from both sides, on *content* change alone (no manual bump)? Places TSF on
   the drift axis; settles the §1 endpoint caveat.
2. Suspicion closure: does suspicion propagate *transitively* beyond the adjacent
   link, and does re-review of the changed item auto-clear derived suspicion
   (DEC-005 analog) — or is it per-link and manual?
3. Affirmation storage: what does "reviewed/cleared" persist — a content-bound stamp
   (hash at review time)? Two-sided? Where does it live (item file vs `.dot`)?
4. Source binding: do file / source-span references content-bind (changed artifact
   flags the premise)? Span granularity vs DEC-003 raw-byte-span hashing.
5. Scoring semantics: reproduce the mean/graphalyzer propagation by hand; is it
   deterministic; **does suspect state gate the score** (does suspect evidence still
   count?) — the §15-hypothesis question in operational form.
6. Commitment: any single recomputable root over the graph or the published artifact;
   any signature — or immutability by convention only.
7. Composition round-trip: publish a remote graph, import under a namespace — do
   pre-computed scores travel and get trusted (record-vs-recompute, GAPS G5 analog)?
   Does drift in referenced remote items really "prompt a review"?
8. Meta-model hosting (analysis probe, may outlive the spike): express TSF's model as
   a SEG definition and its score recurrence as a clingo ruleset — the "SEG hosts
   TSF" bridge, the stronger analog of paper-seed §8's reproduce-OFT-coverage idea.
**Method.** As WP-3/WP-5: pre-registered kit at `research/spikes/tsf/` (PREDICTIONS.md
frozen before execution, RESULTS.md during), fixture mirroring the SEG worked fragment
recast as statements; install trudag/dotstop (PyPI or gitlab.eclipse.org/eclipse/tsf),
pin the version in RESULTS. Matrix column added on execution (unlike WP-6, this *is*
exercisable tooling). Q8 lands in notes + paper seed, not the matrix.
**Findings.** — (spike pending; docs-read preliminaries above are not findings)

## 5. Output & downstream use

- Each WP fills its Findings + its matrix column; claims cite the WP section.
- **The distilled synthesis lives in `seg_tool_comparison.md`** (decision 2026-07-04:
  a separate document, NOT folded into `seg_prior_art.md`) — verified spectra,
  OSS-adoption research (Space ROS/RTEMS/Exasol/Ankaios/ELISA/S-CORE), the RTEMS
  case study, and the per-paper use. This note stays the working WP/evidence doc.
- `seg_paper_seed.md` §2/§4/§8 were consolidated against WP-1/WP-2 (commit 9f6a9d1);
  a second consolidation pass after WP-4 (BASIL) closes the set.
- New citations to add on completion: StrictDoc, BASIL, sphinx-needs (repo+version,
  as with OFT) + the adoption sources in `seg_tool_comparison.md` §5; TSF
  (pages.eclipse.dev/eclipse/tsf/tsf + gitlab.eclipse.org/eclipse/tsf/tsf,
  trudag version-pinned at spike time).
- WP-7 outcomes propagate to **three** standing edits: the drift-axis endpoint caveat
  in `seg_tool_comparison.md` §1, the dotstop second-churn-datapoint extension to its
  §3, and the §15 TSF-hypothesis update in
  `development/design/knowledge_graph_design_summary.md` (owner: FSM — cross-worktree).
