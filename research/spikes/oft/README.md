# SEG Spike Kit — OpenFastTrace half (Session A1)

Same SEG worked fragment as the Doorstop kit, expressed in OFT 4.2.0 format.

**Caveat:** authored against the OFT user guide, NOT executed in the build
sandbox (jar host was unreachable there). First step O0 = confirm it imports;
fix any format slips and note them (that's data too).

## Run
1. Ensure Java 17+ and OFT. Either put `openfasttrace-*.jar` in this folder or
   have the `oft` launcher on PATH.
2. `./run.sh` — runs a verbose trace; exit 0 means all deeply covered.
3. Work PREDICTIONS.md O0→O8 in order. Reset between probes:
   `git checkout -- . src/`.
4. Fill RESULTS.md with pasted OFT status lines.

## Layout
- doc/system.md, requirements.md, design.md (ADR), tests.md (TST)
- src/scheduler.c — impl coverage tags (→req and →dsn)
- NB: there is deliberately no TestOutcome file — O7 is about discovering it
  cannot exist.
- PREDICTIONS.md (pre-registered, don't edit during run) / RESULTS.md / run.sh
