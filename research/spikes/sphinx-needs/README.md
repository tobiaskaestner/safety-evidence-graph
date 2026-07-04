# SEG Spike Kit — sphinx-needs (WP-5)

The SEG worked fragment as a sphinx-needs project. Baseline **rehearsed on
sphinx-needs 8.1.1 / Sphinx 8.2.3** (HTML + needs.json build green); probes N1–N8
NOT run. Special relevance: SEG's own Phase-B reqs worktree uses sphinx-needs, and
SEG's extractor supplies exactly the source-binding half sphinx-needs lacks (N5).

## Layout
- `conf.py` — five custom `needs_types` (sys/req/adr/impl/tst) + five
  `needs_extra_links` (refines/answers/adheres/verifies/implements; NB deprecated
  alias of `needs_links` in 8.x).
- `index.rst` — the fragment (SYS001/REQ001/ADR001/IMPL001/TST001).

## Run
1. `pip install sphinx sphinx-needs` (record versions in RESULTS.md).
2. `sphinx-build -b html . <scratch>/sn_html` — baseline green, one deprecation
   warning.
3. `sphinx-build -b needs . <scratch>/sn_json` — needs.json export.
4. Work PREDICTIONS.md N1→N8 in order; reset between destructive probes:
   `git checkout HEAD -- conf.py index.rst` (RESULTS.md excluded).
5. Record in RESULTS.md (per-probe sections) and transcribe to
   `research/notes/seg_tool_landscape.md` §3.
