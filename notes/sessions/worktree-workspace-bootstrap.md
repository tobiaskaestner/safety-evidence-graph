# Phase-B workspace bootstrap — bare repo + worktrees (record)

Set up the Phase-B development workspace: converted the repo to a **bare repo as
container** and laid out the five worktrees (research + four development branches)
that DEC-002 calls for. Decisions below **extend/diverge from DEC-002** but were
deliberately *not* recorded as new DEC entries (user's call); this note is the
record. Executed 2026-06-29.

## Decisions ratified this session

1. **Bare repo as container.** `.bare/` holds the one repository; a `.git` pointer
   file (`gitdir: ./.bare`) at the root lets plain `git` work. Every branch —
   including `research` — is a **peer linked worktree**; no privileged checkout.
   Rationale: matches the west-like container model DEC-002 invokes and the user's
   wish for `research` to be "just another worktree".

2. **Orphan branches for the four dev branches.** `a-reqs / b-impl / c-results /
   g-graph` are **orphan** (disjoint histories, independent SHAs → each `repoXSha`
   stays meaningful). Rationale: research→development is a **maturity re-authoring**,
   not a git merge — research prototypes are throwaway (CLAUDE.md), features are
   re-authored test-first downstream. So no shared ancestry is needed; "never merge"
   (DEC-002) becomes a *structural* property (no merge base). Continuity carrier is
   the **DEC-ID / requirement citation**, not git lineage. The one near-verbatim
   transfer (docs-of-record graduating from `research/` to `doc/design/`) is a copy
   or cherry-pick, both of which work fine across unrelated histories.

3. **Letter-prefixed branch names** (diverges from DEC-002's bare `A/B/C/G`):
   `a-reqs / b-impl / c-results / g-graph`, in dirs `reqs/ impl/ results/ graph/`.
   The logical repo keys `repoA…repoG` (seg.yaml keys, `repoBSha`-style manifest
   fields) are **independent of branch names** and unchanged.

4. **Decision log: one home per slice, no mirroring.** The dev-binding slice
   (DEC-001…006) is to live physically on `b-impl`; the direction slice
   (DEC-007…028) stays on `research`. "**Binding to development**" ≡ committed to
   branch B; **promotion = the commit that lands the entry on B**. Eliminates
   two-copy drift instead of managing it. DEC-003's existing principle/binding split
   maps cleanly onto research/B. The cross-cutting index keeps one home on `research`.
   *(Promotion not yet executed — placement on B, e.g. `doc/design/` vs `notes/`,
   still open.)*

5. **Migration preserved unpushed commits** by `mv .git → .bare` (NOT a bare
   reclone, which would have dropped anything ahead of `origin`). Working tree was
   clean; only ignored files existed and were staged aside, not deleted.

## Resulting layout

```
safety-evidence-graph/
├── .bare/           the one repo (bare)
├── .git             pointer → ./.bare
├── seg.yaml         untracked; repoA→reqs repoB→impl repoC→results repoG→graph
├── .premigration/   safety net (pre-migration working tree; retained)
├── research/  [research]   be331de
├── reqs/      [a-reqs]     repoA — requirements
├── impl/      [b-impl]     repoB — implementation + test specs
├── results/   [c-results]  repoC — test outcomes
└── graph/     [g-graph]    repoG — graph state (ships seg.yaml.example + .gitignore)
```

Each dev worktree seeded with a role `README.md` (initial commit on its orphan
branch). Repo G also ships `seg.yaml.example` (versioned template) and a
`.gitignore` for `seg.yaml`, per `seg_cli_reference`.

## Open follow-ups

- **Decision-log promotion** of DEC-001…006 onto `b-impl` — needs the placement call.
- **Shared scaffolding** (`CLAUDE.md`, `.claude/skills`) across worktrees — the dev
  worktrees currently have only a README; `CLAUDE.md`/`.claude` now live *inside*
  `research/`, not at the container root.
- **Delete `.premigration/`** once satisfied (still retained as a net).
