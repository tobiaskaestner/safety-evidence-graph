# Doorstop Spike — Results (fill during execution)

Doorstop version: 3.1 (matches kit rehearsal)        Date: 2026-07-04

| P# | Prediction (short) | Observed (paste key output) | Verdict | Table-cell impact |
|----|--------------------|------------------------------|---------|-------------------|
| P1 | links untyped | `links:` = bare `- ADR001: We0z…` / `- REQ001: 96y4…` UID:stamp pairs; injected `type: implements` key present before `doorstop`, absent after — validation clean (exit 0) throughout | CONFIRMED + SURPRISE | Edge typing: by-document only; facets: absent. Surprise: validation *rewrites* item YAML and silently drops foreign link keys — migration data would be erased, not ignored |
| P2 | cross-doc link tolerated? (REFUTED in sandbox — reconfirm) | Baseline `doorstop -v`: no buried warnings. After ADR001 text edit: `WARNING: IMPL: IMPL001: suspect link: ADR001` + `WARNING: ADR: ADR001: unreviewed changes`; exit still 0 | REFUTED (reconfirmed) | Cross-doc links are first-class: tolerated, stamped, suspect-participating. "Tree-only" wall does not exist (v3.1); real wall = P1 (untyped) + P9 (no semantics). NB: warnings do not affect exit code |
| P3 | parent edit ⇒ suspect | REQ001 text edit ⇒ `WARNING: REQ: REQ001: unreviewed changes` + `IMPL: IMPL001: suspect link: REQ001` + `ADR: ADR001: suspect link: REQ001`; no flag on REQ001→SYS001 (child-side change invisible — pre-confirms P4) | CONFIRMED | Direct suspicion: present (content-hash stamps, one hop, parent-only) |
| P4 | child edit ⇒ NOT suspect | IMPL001 text edit ⇒ only `WARNING: IMPL: IMPL001: unreviewed changes`; zero suspect-link warnings (IMPL001→REQ001 stays green with drifted child endpoint) | CONFIRMED | edgeHash analogue: one-sided (parent-only); SEG's two-endpoint edgeHash has no counterpart — headline cell |
| P5 | status edit ⇒ nothing | `status: proposed → accepted` ⇒ validation fully clean (0 warnings) | CONFIRMED | Field roles: partially present — `attributes.reviewed` allowlist = committed/tracked split for extended attrs |
| P6 | rationale edit ⇒ unreviewed; child links suspect? | Config verified (`reviewed: [rationale]`). Rationale edit ⇒ `REQ001: unreviewed changes` + suspect on IMPL001→REQ001 AND ADR001→REQ001 | CONFIRMED (lean held) | Link stamps reuse the item stamp incl. extended reviewed attrs; no item-review/link-suspicion divergence |
| P7 | SYS edit ⇒ one-hop suspect only | SYS001 text edit ⇒ `SYS001: unreviewed changes` + `REQ001: suspect link: SYS001` ONLY — ADR001/IMPL001 links stay green. `doorstop clear REQ001 SYS001` removes the suspect (SYS001 stays unreviewed — item review is a second, separate manual act) | CONFIRMED | Transitive suspicion: absent. Auto-clear: vacuous (nothing derived). Affirmation is two manual acts: link clear + item review |
| P8 | source body edit ⇒ invisible drift | (a) body rewrite, keyword kept ⇒ validation fully clean; (b) keyword line deleted ⇒ `ERROR: … external reference not found`, exit 1 (errors gate; warnings don't). Addendum (source-read + behavioral): `references:` + `extensions: item_sha_required` stores a whole-file sha256 **at review time** (`review()` in `core/item.py`); validation (`find_references()`) checks existence only, never recomputes/compares — file edit with sha enabled still validates clean; sha silently updates on next review (5931b0ee… → 7df8e0be…) | CONFIRMED (incl. sha addendum) | Sharpest cell: parser-as-locator **without the hash half** — even the opt-in sha is review bookkeeping, not drift detection; content drift stays invisible either way |
| P9 | impl_violates_adr inexpressible | Source inspection (stronger than the planned doc read): `extensions: item_validator` (document.py:835–870) dynamically imports a Python file exposing `item_validator(**kwargs)`, invoked per item, yields issues. No declarative/rule facility anywhere | REFUTED on the letter, CONFIRMED in spirit | A *hook* exists (arbitrary per-item Python plugin) — but no rule language: expressing impl_violates_adr = writing the verdict layer yourself in Turing-complete, unauditable code. Sharpens the DEC-007 contrast rather than weakening it |
| P10 | publish = report, not proof | `doorstop publish all ./pub` ⇒ HTML docs + index + traceability.csv/html; only integrity-string hits are bundled jquery/bootstrap; CSV = bare UID rows; no stamps/hashes/signature in any published artifact | CONFIRMED | Sealed proofs: absent. Composition: absent (nothing to compose). Verifier must trust the working copy |

## Surprises / notes

- **Doorstop auto-stages edits into the git index** (VCS integration runs on item
  save/rewrite), so the kit's reset recipe `git checkout -- <path>` silently restores
  the *edited* version from the index. Correct reset between probes:
  `git checkout HEAD -- adr/ impl/ req/ sys/ src/` (RESULTS.md excluded).
- **Exit-code semantics:** validation warnings (unreviewed, suspect) leave exit 0;
  only errors (e.g. ref not found) exit 1. A CI gate on the exit code misses drift.
- **Doorstop's project root = the VCS working-copy root.** After de-nesting the kit
  into the outer repo (commit 284d579), `references:` paths must be given relative to
  the *outer* repo root or they silently resolve nowhere (`sha: null`, no error).
- Link stamp = verbatim copy of the target item's review stamp (SYS001's `reviewed`
  == REQ001's stored link stamp for SYS001) — the concrete mechanism behind P3/P4/P6.
- The kit's P11 mention in the OFT synthesis section has no referent here (kit ends
  at P10); read it as the evidence-split observation (no TestOutcome representation —
  true for Doorstop by absence of any outcome-bearing item type in the model).
