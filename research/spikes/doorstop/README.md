# SEG Spike Kit — Doorstop half (Session A1)

A ready-built Doorstop tree mirroring the SEG worked fragment
(seg_definition_language.md §2) plus one refines hop. Baseline is reviewed,
cleared, and git-committed: `doorstop` validates clean.

## Run
1. `pip install doorstop` (kit rehearsed on v3.1 — note your version in RESULTS.md)
2. Unzip, `cd` in. The directory is a git repo (history included).
3. `doorstop` — confirm clean baseline.
4. Work through PREDICTIONS.md P1→P10 in order. After each destructive probe:
   `git checkout -- . && doorstop` to confirm you're back to baseline.
5. Record everything in RESULTS.md. Paste actual output lines — they go into
   the paper's §3 evidence.

## Layout
- sys/ req/ adr/ impl/ — the four documents (REQ has the committed extended
  attribute `rationale`; ADR carries the tracked `status`)
- src/scheduler.c — the referenced implementation source (P8 target)
- PREDICTIONS.md — pre-registered, do not edit during execution
- RESULTS.md — fill as you go

Budget: one evening. P9 is a 20-minute doc read, not a build.
