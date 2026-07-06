# SEG Spike Kit — Eclipse TSF / trudag / dotstop (WP-7)

The SEG worked fragment **recast as TSF statements** (truth-apt, indicative —
see `seg_tsf_duality.md` §1 for why the recast is not 1:1). Baseline
**rehearsed on trudag 0.4.0** (init → add-item ×5 → create-link ×5 → lint →
score all green; score correctly reports all-zero/Missing on the unscored
graph). Probes T1–T8 NOT run; `publish`/`show-item`/`show-link` deliberately
NOT rehearsed (probe territory).

## The recast (fragment → statements)

| SEG fragment | TSF statement | Role |
|---|---|---|
| SYS001 | `EXP-SCHED` — kernel schedules deterministically | Expectation (root) |
| REQ001 (refines SYS001) | `ASSERT-LOCK` — lock holder is not preempted | Assertion |
| ADR001 (answers REQ001) | `ASSERT-COOP` — cooperative counter, ISR latency bounded | Assertion |
| IMPL001 (implements REQ001, adheres ADR001) | `PREM-IMPL` — k_sched_lock realizes the primitive; references `src/scheduler.c` | Premise (leaf, multi-parent) |
| TST001 (verifies REQ001) + outcome | `PREM-TEST` — preemption test passes; references `tests/test_scheduler.py` | Premise (leaf) |

Links (parent → child = parent supported by child): EXP-SCHED→ASSERT-LOCK;
ASSERT-LOCK→{ASSERT-COOP, PREM-IMPL, PREM-TEST}; ASSERT-COOP→PREM-IMPL.

## Layout
- `EXP-SCHED.md ASSERT-LOCK.md ASSERT-COOP.md PREM-IMPL.md PREM-TEST.md` —
  items (YAML frontmatter + body; PREM-* carry `references:` type `file`).
- `src/scheduler.c`, `tests/test_scheduler.py` — reference targets (copied from
  the StrictDoc kit so cross-kit cells stay comparable).
- `setup.sh` — builds the graph (init, add-item, create-link) in the cwd.

## Run
1. **Copy the kit to a scratch git repo** — do NOT run in the research
   worktree: trudag writes `.dotstop.dot` at the *git toplevel* (it resolves
   `git rev-parse --show-toplevel`), which would land at the worktree root.
   ```
   cp -r research/spikes/tsf <scratch>/tsf && cd <scratch>/tsf
   git init . && git add -A && git -c commit.gpgsign=false commit -m fixture
   ```
2. `pip install "git+https://gitlab.eclipse.org/eclipse/tsf/tsf.git"` — the
   distribution is named **`trustable`** (NOT on PyPI as `trudag`). Record
   version AND commit in RESULTS.md.
3. `./setup.sh` (points at the venv's trudag; or set `TRUDAG=`) — expect five
   items + five links in `.dotstop.dot`, node and edge `sha`s populated.
4. `trudag lint && trudag score` — baseline: lint clean; score prints
   `0.0; Missing` per item + "Score set to zero" warnings.
5. Work PREDICTIONS.md T1→T8 in order; reset between destructive probes with
   `git checkout -- .` in the scratch repo (fixture is committed there).
6. Record in RESULTS.md (per-probe sections) and transcribe to
   `research/notes/seg_tool_landscape.md` §3/§4 (WP-7); route the three
   standing edits per §5 of that note.

## Gotchas (learned at rehearsal)
- trudag fails outside a git work tree (`fatal: this operation must be run in
  a work tree` surfaces as a GitCommandError traceback).
- `create-item` argument order is `PREFIX ID PATH` (docs-style `PATH
  PREFIX-ID` is wrong); `add-item FILEPATH` ingests a pre-existing file.
- Committing in a scratch repo may hang on GPG signing — use
  `git -c commit.gpgsign=false commit`.
