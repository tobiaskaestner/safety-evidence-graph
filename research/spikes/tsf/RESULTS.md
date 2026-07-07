# TSF (trudag/dotstop) Spike — RESULTS (WP-7)

**Run 2026-07-07.** trudag **0.4.0**, distribution `trustable`, installed from
gitlab.eclipse.org/eclipse/tsf/tsf @ **58f38df0**; Python 3.12; probes executed
in a scratch git repo per README (fixture as committed in this kit). clingo
5.8.0 (python module) for T8.

**Probe-hygiene note (two incidents, both caught).** Two drift probes were
initially no-ops (sed patterns that matched nothing: T4's `return 0;` never
existed in `scheduler.c`; T5b's pattern had already been rewritten by T2a).
Both "null results" were retracted and re-run with a verified non-empty
`git diff` before observation. Rule for future kits: **never read a
no-status-change result without confirming the edit landed.**

---

## T1 — Drift trigger & sidedness

- **Verdict:** CONFIRMED (two-sided, content-hash, no manual bump) — one
  sub-point REFUTED (raw-bytes hashing).
- **Observed:** Editing the *child*'s body flips the upstream link
  (`EXP-SCHED -> ASSERT-LOCK => SUSPECT`) AND the item to `unreviewed`; the
  same edit flips the item's *downstream* links too; editing the *parent*
  flips the same link — fully two-sided, triggered by content alone.
  **Surprise 1:** a trailing-newline-only edit does NOT trip anything — the
  hash is over parsed/normalized statement content (`Item.sha256` =
  name + text + normative + reference shas), not file bytes. **Surprise 2:**
  reverting content restores `LINKED`/`reviewed` — status is *derived* by
  comparing stored vs recomputed sha, never latched. **Surprise 3:** items and
  links are born reviewed (creation records the sha = the stamp).
- **Table-cell impact:** drift axis = **two-sided content hash** — the
  comparison doc §1 endpoint claim must be caveated. Granularity: normalized
  item content (SEG: raw source byte spans, DEC-003).

## T2 — Suspicion closure (transitivity, auto-clear)

- **Verdict:** CONFIRMED (no closure).
- **Observed:** After a leaf edit, only the leaf is `unreviewed` and only
  *adjacent* links `SUSPECT`; the two-hop link and grandparent item are
  untouched. `set-item` re-stamps the node sha but adjacent links STAY
  suspect — `set-link` must be issued per link; nothing auto-clears on
  descendant re-affirmation (contrast DEC-005). (The *revert* auto-clear of T1
  is hash-comparison behavior, not a closure.)
- **Table-cell impact:** stored-vs-derived — TSF stores affirmations but
  derives no transitive suspicion; SEG's "alone in combining stored
  affirmation + derived closure" survives, resting on the derived half.

## T3 — Affirmation storage

- **Verdict:** CONFIRMED (the sha IS the stamp; two-sided; anonymous).
- **Observed:** `set-item` writes the recomputed item sha to the node in
  `.dotstop.dot`; `set-link` writes the link sha; `Item.sha_link` =
  sha256(parent.sha256 + child.sha256) — the stored link stamp covers both
  endpoints (and, transitively, referenced artifact content). NO actor,
  timestamp, or justification anywhere in `.dotstop.dot` — the affirmation is
  an **anonymous content stamp** (contrast SEG's affirmation events; NB the
  git commit does carry an author, but the tool records none).
- **Table-cell impact:** affirmation = stored, content-bound, two-sided,
  identity-free.

## T4 — Source binding (file / source-span references)

- **Verdict:** CONFIRMED — **first content-bound source reference in the
  applied set** (after retraction of the initial no-op probe, see hygiene
  note).
- **Observed:** A verified edit to referenced `src/scheduler.c` makes
  PREM-IMPL `unreviewed` and BOTH its incident links `SUSPECT` (multi-parent:
  both parents flagged). Mechanism: `reference.sha` (sha256 of artifact
  content) is folded into `Item.sha256`. Reference types: `file` (working-tree
  read), `gitlab` (remote), `artifact` (subgraph of another project — T7),
  and **`SourceSpanReference` — an abstract extension base** that hashes the
  raw bytes of a [line,char]-span "found at reference-time — say, by looking
  up a function name": DEC-003's locate-then-hash shape as a DIY extension
  point, not a built-in.
- **Table-cell impact:** source binding = locator-WITH-hash at file
  granularity (unique in the set); span granularity = extension base only.
  SEG delta narrows to: built-in span binding + parser-locates-only TCB
  discipline + the closure above it (T2).

## T5 — Scoring semantics; suspect-gates-score?

- **Verdict:** mean-propagation CONFIRMED; gating prediction **REFUTED — the
  informative way: suspect state DOES gate the score.**
- **Observed:** (a) SME scores live in item frontmatter
  (`score: {tom: {value: 0.8, justification: …}}`); leaves report "SME with
  References", inner nodes "Derived from supporting Statements"; hand-computed
  mean matches exactly: ASSERT-COOP 0.8, ASSERT-LOCK = (0.8+0.8+0.6)/3 =
  0.73333 = EXP-SCHED (multi-parent leaf counted once per parent path).
  (b) **`score:` is NOT part of `Item.sha256`** — adding/changing a score does
  not trip review status: the trust number sits OUTSIDE the affirmation
  boundary (a committed/tracked split with the verdict input on the tracked
  side). (c) Making the scored leaf suspect (verified edit, no re-review) →
  its score is ZEROED (`PREM-TEST = 0.0; Missing`) and the zero propagates
  (root 0.73333 → 0.53333). **An unreviewed statement contributes nothing:
  integrity gates scoring** — TSF independently implements the design summary
  §15 hypothesis ("a clean integrity state is necessary but not sufficient
  for a high trust score"). Coupling is one-directional: suspicion gates
  scores; scores are invisible to affirmation.
- **Table-cell impact:** verdict/coverage cell = hardwired probabilistic
  roll-up (mean), suspect-gated, recomputed statelessly every run; evidence
  wall = **crossed** (first non-SEG tool whose computation consumes evidence
  values). Routes to design summary §15 (FSM applies — cross-worktree).

## T6 — Commitment / seal

- **Verdict:** prediction PARTIALLY REFUTED — a global recomputable root
  EXISTS; but it is unverified-on-consumption and unsigned (see T7).
- **Observed:** `export` writes an artifact carrying `/resolved/sha` =
  sha256(dot-graph string + every item sha + serialized scores) — a flat,
  recomputable commitment over structure AND scores (one step beyond
  rtemsspec's item-cache hash, which excludes results); plus git metadata
  (`Commit SHA`, tag) and a hashed `config_version`. NO signature anywhere.
  Bonus recon: `export --sensitivity` ships built-in sensitivity analysis —
  the "cheap on the unfolded side" dividend (duality note §6.4) as a product
  feature.
- **Table-cell impact:** commitment = present as *data* (flat root over graph
  + scores), absent as *checked invariant* (T7); no seal, no signature.

## T7 — Composition round-trip (artifact; traveling scores; tamper)

- **Verdict:** record-not-recompute CONFIRMED at **maximal strength**.
- **Observed:** (a) Consumption is via `ArtifactReference` (`type: artifact`,
  roots) on a downstream item; `import` targets needs items (fixture had no
  needs graph — that half **not exercised**; export warned "artifact will
  have no needs"; NB `_import_new_and_existing_links` sets imported links to
  SUSPECT — affirmation-gated arrival, from source read). (b) Pre-computed
  scores travel in the artifact; the downstream item does NOT inherit them —
  the downstream SME reads the upstream case and assigns their own score
  (score transfer is human-mediated). (c) **Tamper tests:** flipping a score
  inside the shipped artifact (0.6→0.99) → undetected (schema check only;
  `read_artifact` never recomputes `/resolved/sha`); rewriting a guarantee
  *text* inside the artifact → undetected (`ArtifactReference.content` is the
  dot-subgraph string with its *stored* shas — never recomputed against item
  texts). (d) **Honest re-publish** (upstream item edited, re-stamped,
  re-exported) → downstream referencing item flips `unreviewed` — the docs'
  "prompts a review" is real, keyed on the artifact's declared sha set
  changing. Net: integrity across the boundary holds **iff the producer
  regenerates hashes honestly** — recorded hashes travel, nothing recomputes
  them; a consumer cannot distinguish a tampered artifact from an authentic
  one (no seal check, no signature).
- **Table-cell impact:** exchange = richest integrity *transport* in the set
  and still no *verification*: the DEC-017 foil sharpened — not only verdicts
  (scores) travel, the commitment itself travels unverified.

## T8 — Analysis: SEG hosts / generates TSF

- **Verdict:** CONFIRMED at the semantics level (score calculus).
- **Observed:** `t8_clingo_score.lp` (this kit) reproduces trudag's exact
  output on the fixture — mean propagation over the DAG in scaled integers
  (`#sum`/`#count`, integer division): 80000/60000 leaves → 73333 root =
  trudag's 0.73333; the T5b suspect-gate as one rule (drop
  `reviewed(prem_test)` → 53333 root = trudag's 0.53333). Single answer set,
  stratified, ~10 rules. TSF's entire verdict layer (mean + gate +
  unscored-is-zero) is expressible as a SEG verdict ruleset; with T1/T3/T4
  (drift, stamps, references = SEG's edge/affirmation/source-binding
  mechanics) the **hosting** direction is structurally complete, and the
  **generation** direction (argument view as projection) has its evaluation
  semantics demonstrated. Strain honestly recorded: 1e5 integer scaling
  stands in for reals (precision-bounded, fine for 5-decimal parity);
  calibration/justification strings are data, not semantics; the §6.5
  negation obstruction is untouched by this demo (the score program is
  positive + default negation on `reviewed`, stratified).
- **Impact:** routes to `seg_tsf_duality.md` §6 (triangle demonstrated on the
  score edge) + paper seed §1a role 2; NOT a matrix cell. Novelty caveat
  stands: check Rushby ETB / AdvoCATE before claiming generation as novel
  (`seg_prior_art.md` gaps).

## Surprises / format fixes needed

- PyPI has no `trudag`; install from Eclipse GitLab (distribution
  `trustable`). `create-item` arg order is `PREFIX ID PATH`; must run inside
  a git work tree; scratch-repo commits need `-c commit.gpgsign=false`.
- Items/links born reviewed (creation stamps); revert auto-clears
  (comparison, not latch); whitespace edits normalized away.
- `score:` frontmatter outside the item hash (T5b) — the trust number is
  never affirmed.
- A real global root (`/resolved/sha`) that nothing ever verifies (T6/T7).
- Built-in sensitivity analysis on export (duality §6.4 dividend, shipped).
- Two no-op-sed probe incidents (see hygiene note) — both retracted and
  re-run verified.

## Synthesis (transcribed to seg_tool_landscape.md WP-7 + §3 column)

- **Drift axis:** two-sided content hash, normalized item-content granularity
  — TSF joins SEG at the axis endpoint; SEG's remaining drift delta = raw
  byte-span granularity + derived closure (T2).
- **Stored vs derived:** stored two-sided anonymous stamps; NO derived
  suspicion closure, no auto-clear on re-affirmation. SEG's combination claim
  survives on the derived half.
- **Evidence wall:** CROSSED — first non-SEG tool computing over evidence
  values (suspect-gated probabilistic mean; hardwired, not programmable).
- **Source binding:** first locator-with-hash in the set (file granularity
  built-in; DEC-003-shaped span binding as abstract extension base).
- **Commitment:** flat recomputable root over graph+scores EXISTS as data;
  verified by no one; unsigned.
- **Exchange/composition:** scores and commitment travel unverified
  (record-not-recompute at maximal strength); honest re-publish does prompt
  downstream review; needs/assumptions half not exercised.
- **Standing edits routed:** comparison §1 drift-axis caveat (LANDS),
  comparison §3 dotstop-churn extension (LANDS), design summary §15 update
  (routed to FSM — TSF independently implements the hypothesis, T5).
