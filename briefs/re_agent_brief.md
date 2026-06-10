# Requirements Engineer Agent Brief — SEG

## Mandate

The Safety Evidence Graph (SEG) is the tool we are building, and we intend it to
eventually generate an integrity proof **of itself**. Your job: author the
**requirements for the SEG tool**, as sphinx-needs, so the Software Engineer can
implement against them and the Test Engineer can verify them. These requirements
are the contract the rest of the team builds on.

Source material — derive requirements from these, do not invent design:
the SEG design summary and `seg_decision_log.md` (DEC-001…004).
Where intent is unclear, ask.

## Scope of this first slice

**One system requirement plus 3–4 software requirements that refine it**, on the
**hashing + graph-build core** — the foundational behaviour (compute stable
content hashes for nodes, derive node/Merkle hashes, build the graph from nodes
and references). This is a deliberately small **complete subtree**, not the whole
tool. Later slices extend it iteration by iteration.

Do not author requirements for areas beyond this slice yet (proof generation,
gates, suspect detection, extractors, CLI) — they come in later iterations.

## Rules

- **ID scheme:** `SEG-SYS-nnn` for system requirements, `SEG-SREQ-nnn` for
  software requirements. IDs are stable and permanent once issued — SWE/TE will
  reference them in `:implements:` / `:verifies:` markers.
- **Decomposition:** the slice is a `refines` tree — software requirements refine
  the system requirement (child → parent). `refines` must be acyclic (DEC-001).
- **Leaf rule (DEC-001):** the software requirements are leaves; each must be
  concrete enough to be directly implemented and tested (≥1 implementation and
  ≥1 test will eventually attach). The system requirement is a non-leaf, covered
  transitively by its children — it carries no direct implementation/test.
- Keep each requirement **atomic, testable, and implementation-agnostic** (state
  *what*, not *how*). One verifiable claim per software requirement.
- Author as **sphinx-needs** in a `doc/requirements` sphinx project you scaffold
  from scratch (point conf.py / paths at the local folders as advised). The build
  must emit a reproducible `needs.json` (`needs_reproducible_json = True`) — that
  file is what the SEG requirements extractor will consume.

## Deliverable

- A scaffolded `doc/requirements` sphinx-needs project.
- The first slice: 1 `SEG-SYS-nnn` + 3–4 `SEG-SREQ-nnn`, with `refines` links.
- A successful build producing `needs.json`.

## Non-goals

- No implementation, no tests, no code markers — requirements only.
- No requirements outside the hashing + graph-build slice.
- No four-branch topology / worktrees — author in the local `doc/requirements`
  folder; it is folded onto branch A later.

## Collaborative action plan (checkpoint script)

Work one step at a time. At each **⏸ PAUSE**, stop and wait for the human to
review and decide before continuing.

1. **Scaffold** the `doc/requirements` sphinx-needs project (conf.py, index,
   reproducible needs.json output). **⏸** Human reviews the setup and the build.
2. **Draft the system requirement** (`SEG-SYS-nnn`) for the hashing + graph-build
   core — the single top-level claim this slice establishes. **⏸** Human reviews
   and approves the system requirement *before* it is decomposed.
3. **Decompose** into 3–4 `SEG-SREQ-nnn` software requirements that `refine` it,
   each atomic and testable. **⏸** Human reviews the decomposition (coverage,
   atomicity, IDs) and may adjust.
4. **Build** and confirm `needs.json` is produced and well-formed. **⏸** Human
   reviews the final slice and signs off as the contract for SWE/TE.
