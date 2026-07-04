# SEG — OSS Tool Comparison (distilled synthesis)

**What this is.** The paper-facing synthesis of the tool-landscape work — kept
**separate from `seg_prior_art.md`** by decision (2026-07-04): prior_art stays the
formalism/literature map; this document owns the applied-tool comparison. The working
evidence lives in `seg_tool_landscape.md` (WPs, axes, matrix) and the per-kit
RESULTS.md files under `research/spikes/` (pre-registered probes, raw output).

**Verified basis.** Doorstop 3.1 (P1–P10), OpenFastTrace 4.5.0 (O0–O8), StrictDoc
0.25.0 (S1–S9), sphinx-needs 8.1.1 (N1–N8) — all probe-cited; BASIL (WP-4) pending.

---

## 1. The verified spectra

- **Drift axis** — how a tool learns that content an edge relies on has changed:
  **none** (StrictDoc S3/S5; sphinx-needs N4/N7 — including *cross-project* links) →
  **one-sided content hash** (Doorstop P3/P4: link stamp = copy of the parent item's
  stamp; child drift invisible) → **two-sided manual counter** (OFT O3: content edits
  silent, revision bump breaks whole-chain, dual `orphaned`/`outdated`) →
  **two-sided content hash** (SEG `edgeHash`).
- **Stored vs derived** — Doorstop stores stamps but derives nothing (one-hop, P7);
  OFT derives everything but stores nothing (no affirmation concept, O3b); StrictDoc
  and sphinx-needs neither store nor derive. SEG is alone in combining a stored,
  content-bound human affirmation with a derived suspicion closure.
- **Extensibility spectrum** — what a user can make the tool check:
  nothing (OFT O4) → per-item arbitrary Python (Doorstop P9 `item_validator`) →
  whole-graph arbitrary Python (StrictDoc S9 `StrictDocPlugin`) → **declarative
  bounded-depth shapes + per-need eval strings** (sphinx-needs N2/N3 — severities
  *explicitly SHACL-derived*, hard `network_max_nest_level` bound) → user-authored
  *recursive* stratified Datalog bound to a commitment (SEG). sphinx-needs marks the
  recursion line from below; DEC-007 sits directly above it.
- **Evidence wall** — a test *outcome* with a value: unrepresentable (OFT O7;
  Doorstop by absence) → representable-but-inert (StrictDoc S7: JUnit/Robot/gcov
  readers produce TEST_RESULT nodes; nothing consumes PASSED/FAILED; path-only
  binding, no freshness) → convention-only (sphinx-needs N6). No tool computes
  anything from evidence; none binds it to the source state it attests.
- **Source binding** — locator-without-hash everywhere it exists at all: Doorstop
  `ref`/`references` (existence checked; opt-in sha is review-time bookkeeping, P8);
  StrictDoc `@relation` ranges (silently droppable, S5); OFT coverage tags (part of
  the item model); sphinx-needs none (N5 — SEG's own extractor supplies this half in
  Phase B). SEG's raw-byte-span hashing (DEC-003) has no counterpart.
- **Exchange/composition** — reports only (Doorstop P10) → one-way textual ReqM2
  with `dstversion` pins (OFT O8) → ReqIF both directions + JSON (StrictDoc S8) →
  **by-reference cross-project links** (sphinx-needs N7 `needs_external_needs`) —
  and the last is fully drift-blind: a rewritten external guarantee rebuilds with
  zero warnings. Nothing carries a commitment, a scope, or a discharge concept.

## 2. Adoption in OSS projects (researched 2026-07-04, web; evidence strength marked)

**Bottom line.** Every tool in the set has at least one verifiable OSS adopter;
evidence strength varies (docs-page vs README vs search-snippet vs vendor claim —
marked per row, full URLs in §6). One anticipated adopter turned out to be an
*informed rejecter* (RTEMS, §3), which is more valuable than an adoption.

| Tool | Adopter | Evidence |
|---|---|---|
| Doorstop | **Space ROS** — "Doorstop, along with git, is used to ensure requirements tracking and traceability"; FRET imports/exports Doorstop's Markdown format | docs page: space-ros.github.io/docs/rolling/Related-Projects/Doorstop.html |
| Doorstop | **RTEMS** — *evaluated and rejected* (see §3) | docs.rtems.org/docs/main/eng/req/tooling.html |
| OpenFastTrace | **Exasol** — OFT originates from itsallcode (Exasol-adjacent); e.g. exasol-testcontainers keeps requirements/design/coverage tags in OFT format | repo docs: github.com/exasol/exasol-testcontainers |
| OpenFastTrace | **Eclipse Ankaios** (SDV automotive workload orchestrator) — "requirement tracing using the OpenFastTrace requirement tracing suite" | docs page: eclipse-ankaios.github.io …/requirement-tracing/ |
| StrictDoc | **Zephyr** — requirements repo with shared `.sgra` grammar, `ZEP-SRS-` UIDs | **verified locally**: `/wrk/z/ws-safety/doc/reqmgmt` (pins strictdoc>=0.9.1) |
| StrictDoc | **linux-strictdoc** (PoC, StrictDoc author + ELISA) — implements the "ELISA Kernel Requirements Template" (Carminati/Paoloni): `SPDX-Req` tags in kernel source + sidecar `.sdoc`; experimental; NB recent commits mention auto-assigned identifiers *and hashes* — watch | repo README: github.com/strictdoc-project/linux-strictdoc |
| BASIL | **ELISA** — elisa-tech org; Red Hat contribution (L. Pellecchia); a deployed "ELISA BASIL Instance"; traces sw requirements ↔ test specs/cases/runs, integrates KernelCI/Testing Farm/GH/GL CI. Flask API + React + DB — the set's only app/DB-backed tool | repo README: github.com/elisa-tech/BASIL; ELISA workshop recaps |
| sphinx-needs | **Eclipse S-CORE** (Safe Open Vehicle Core) — docs-as-code with Sphinx/sphinx-needs, Bazel, PlantUML | project docs: eclipse.dev/score; OSS NA 2025 talk |
| sphinx-needs | **SEG itself** — Phase-B reqs worktree | this repo |
| sphinx-needs | automotive projects ">1,000 engineers, >100,000 objects" | **vendor claim** (sphinx-needs.com marketing) — do not cite as adoption evidence |

**The cluster observation.** Adoption concentrates in the Linux Foundation / Eclipse
safety ecosystem: ELISA (BASIL, linux-strictdoc), Zephyr (StrictDoc), Eclipse SDV
(Ankaios→OFT, S-CORE→sphinx-needs), space (Space ROS→Doorstop; RTEMS→custom). That
is *literally the OSS Summit safety-track audience* — the Prague talk's comparison
section addresses tools its listeners already run.

## 3. The RTEMS case study — an adopter independently confirms the probe findings

RTEMS selected Doorstop ("mainly due a recommendation"), hit six documented
limitations, concluded "no requirements management tool was available that fits the
need," and wrote their own Python tool "drawing heavy inspiration from Doorstop"
(docs.rtems.org, eng/req/tooling). Their limitations map onto the spike:

1. mandatory standard attributes on items that don't need them → the fixed item
   model (no per-type grammar; cf. StrictDoc S2 solving exactly this);
2. **links lack custom attributes ("role", "enabled-by")** → P1: links are untyped
   `UID: stamp` pairs, foreign keys silently erased;
3. no specialized item types per document hierarchy → same gap S2 measures;
4. **verification "too basic" for type-based rules** → P9: no rule language;
5. UID/hierarchy redundancy, no relative linking; 6. fixed alphabetical link order.

The trajectory adopt → hit the P1/P9 walls → build-your-own is the strongest market
signal in the set: the walls the spikes measured are the ones real safety projects
leave the tool over.

**What they built (WP-6 bounded source-read, rtems-central @ 8ace630 — evidence in
`seg_tool_landscape.md` WP-6).** The churn outcome fixes the walls — links carry
roles; the type system is *self-describing* (`type: spec` items interpreted by a
generic verifier — a structurally-realized meta-model dogfood) — and, most
strikingly, **independently reinvents SEG's commitment mechanics as build
machinery**: per-item SHA-256 content digests, links that store the linked item's
digest and fire on mismatch, and a global SHA-512 over the sorted digests of the
whole item set (the "overall item cache hash" — structurally a flat-sealed root).
All of it drives *build invalidation* for the qualification data package, not
assurance: there is no human affirmation, no suspect state, no programmable verdict,
and no sealed artifact a third party can verify. The sharpest way to say it: when
the field's best self-help reinvents hash-pinned links and a flat recomputable root,
it stops at incremental builds — the assurance semantics SEG attaches to exactly
these mechanics (affirmation, derived suspicion, user-authored verdicts, the sealed
proof) remain the delta.

## 4. Use in the papers

- **Paper 1 (Prague).** Lead the comparison with §2's cluster observation (the
  audience's own tools), then the composition gap: the one by-reference cross-project
  mechanism in the field is drift-blind (N7), exchanges are textual (O8/S8), and the
  ecosystem is already reaching for SPDX (`SPDX-Req` tags in linux-strictdoc) — the
  sealed `(G, A, I)` BOM answers a live, demonstrated need.
- **Paper 2 (design space).** The spectra in §1 are the facet-bundling evidence; the
  two boundary markers are sphinx-needs' SHACL-cited bounded validation (the
  recursion line, N2) and RTEMS' six limitations (facet bundling as the reason
  adopters churn, §3).

## 5. Citation stubs to harden before use

- Space ROS docs, "Doorstop" related-projects page (URL above; version the page).
- RTEMS Software Engineering manual, §Requirements/Tooling (URL above; snapshot the
  six limitations verbatim).
- Eclipse Ankaios docs, "Requirement tracing" (version 0.2 page seen).
- strictdoc-project/linux-strictdoc README (commit-pin; experimental status).
- elisa-tech/BASIL README (commit-pin); ELISA workshop recap (Munich 2025).
- Eclipse S-CORE docs page (eclipse.dev/score/docs.html).
- Not re-verified this session: the Exasol-testcontainers OFT statement came from a
  search snippet — open the repo doc before citing.
- rtems-central / rtemsspec: cite repo + commit 8ace630 (shallow clone read
  2026-07-04); the six Doorstop limitations and the spec-items model are also in the
  RTEMS Software Engineering manual (eng/req/tooling, eng/req/items).

## 6. Sources (as retrieved 2026-07-04)

- Space ROS — Doorstop related-projects page:
  <https://space-ros.github.io/docs/rolling/Related-Projects/Doorstop.html>
  (companion FRET page: <https://space-ros.github.io/docs/rolling/Related-Projects/FRET.html>)
- RTEMS Software Engineering manual, Requirements → Tooling:
  <https://docs.rtems.org/docs/main/eng/req/tooling.html>
- Eclipse Ankaios — Requirement tracing (v0.2 docs):
  <https://eclipse-ankaios.github.io/ankaios/0.2/development/requirement-tracing/>
- OpenFastTrace repository: <https://github.com/itsallcode/openfasttrace>
- Exasol testcontainers (OFT-format requirements — snippet-level evidence, recheck):
  <https://github.com/exasol/exasol-testcontainers>
- linux-strictdoc (ELISA SPDX-Req kernel PoC, experimental):
  <https://github.com/strictdoc-project/linux-strictdoc>
- BASIL repository: <https://github.com/elisa-tech/BASIL>
- ELISA Workshop Munich 2025 recap (BASIL/Red Hat context):
  <https://elisa.tech/blog/2025/12/03/recap-elisa-workshop-munich-germany-2025/>
- Eclipse S-CORE docs (sphinx-needs docs-as-code toolchain):
  <https://eclipse.dev/score/docs.html>
- sphinx-needs product site (vendor claims only): <https://www.sphinx-needs.com/>
- Zephyr StrictDoc usage: verified locally at `/wrk/z/ws-safety/doc/reqmgmt`
  (no URL needed; the west workspace copy is the evidence).
