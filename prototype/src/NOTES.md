# SEG Phase A Prototype — Surfaced Unknowns and Observations

Throwaway prototype. This file collects findings for the real implementation.
Organised by theme; each item states what we learned and what it implies.

---

## Visualisation

**DOT export proved essential, not optional.**
The state-aware DOT overlay (satisfaction colours on nodes, link-state colours
on edges, scope dimming, double-border for mutated nodes) gave immediate,
unambiguous feedback on proof state that the JSON output could not. Recommended
as a first-class output in the real tool, not an afterthought.

**Scope dimming is the right model for partial proofs.**
When `proof --dot` dims out-of-scope nodes, the in-scope subgraph reads cleanly
and the boundary is obvious. The dimming must follow `seg:Confirms` and
`seg:Excuses` edges all the way to outcomes and waivers — stopping at
TestSpecification leaves the outcome nodes dimmed even when they are in scope
(we hit this bug and fixed it during the prototype run).

**The suspect-origin double border worked well.**
`peripheries=2` on mutated nodes lets a viewer immediately trace:
mutated node → solid-red directlyOutdated edge → dashed-red
transitivelySuspect edges further up the chain. Without it, transitivelySuspect
edges read as floating red with no visible cause.

**Graph direction matters.**
`rankdir=RL` (sinks on the left) places top-level requirements leftmost and
evidence nodes (outcomes, impls) rightmost, which matches the natural
proof-reading direction. `rankdir=LR` does the opposite.

---

## Performance

**Merkle computation hits a performance cliff around 10 K nodes.**
The recursive `_fill_merkle` in loader.py recomputes every node's Merkle hash
on every load. With the prototype's naïve traversal:

| Store        | Nodes   | Load time |
|---|---|---|
| small        | ~30     | <0.01 s   |
| medium       | ~235    | 0.04 s    |
| large        | ~2 230  | 0.24 s    |
| extra-large  | ~110 K  | ~2 hours  |

The extra-large run confirmed all 26 835 requirements satisfied, but the
2-hour wall time makes it useless interactively. The real implementation must:
- Store Merkle hashes in repo G alongside node/edge records.
- Recompute only the affected subtree when a node changes (incremental update
  walking the Refines DAG from the changed node upward).
- Never recompute the whole graph on load.

**JSON parsing is not the bottleneck.**
Parsing the 34 MB extra-large file is fast; almost all the time is in SHA-256
computation. Python's `hashlib` is fast per call, but 110 K × 3 sub-hashes ×
recursive Merkle traversal adds up.

---

## Hashing and Link States

**Edge hashes bind both endpoint node hashes — intended but far-reaching.**
Changing a requirement's description text invalidates:
- all `seg:Implements` edges pointing *to* it (to_iri changed),
- all `seg:Verifies` edges pointing *to* it (to_iri changed),
- the `seg:Refines` edge pointing *from* it (from_iri changed).

The Refines edge becoming `directlyOutdated` is surprising at first glance
(the refinement relationship itself did not change), but it is correct: the
edge was affirmed against the old text and needs re-affirmation against the
new one. The real implementation should surface this clearly in affirmation UX.

**`doublyOutdated` is a meaningful signal.**
When both endpoints of an edge change together, it is more likely a coordinated
refactor than an accidental divergence. Displaying it distinctly from
`directlyOutdated` is worth preserving.

**`broken` was never exercised.**
None of our prototype scenarios removed a node from the graph. The `broken`
link state (endpoint node no longer exists) needs a dedicated test scenario
and clear UX in the real tool — a broken edge cannot be affirmation-cleared,
it requires an endpoint fix or edge deletion.

**All edges initialised as ACTIVE in the prototype.**
The hand-crafted store is treated as pre-affirmed. In the real system, every
newly created edge starts as `PENDING` and enters the affirmation backlog.
The prototype never exercises the PENDING → ACTIVE affirmation path.

**PENDING and DIRECTLY_OUTDATED both block satisfaction identically.**
The coverage check treats any non-ACTIVE link state as a gap. This is the
right policy, but the real UX should distinguish the two in gap messages:
"no affirmed Verifies edge" vs. "Verifies edge outdated — re-affirmation
needed" are different calls to action.

---

## Satisfaction and Scope

**enforce-if-present fires correctly on non-leaf requirements.**
When a non-leaf requirement carries direct `seg:Verifies` / `seg:Implements`
edges, those must pass in addition to all children being satisfied (DEC-001).
The prototype confirmed this through the `store-deep-mid-coverage.json`
scenario: breaking only the mid-level implementation left the leaf reqs
satisfied but failed the mid-level req.

**Scope expansion must be total.**
`generate_proof` expands the initial scope through `seg:Refines` children,
then `seg:Implements` / `seg:Verifies` to impls and test specs, then
`seg:Confirms` to outcomes, then `seg:Excuses` to waivers. Missing any of
these hops produces a silent partial scope — nodes appear in the graph but
are treated as out-of-scope. The real implementation should document the
full expansion algorithm and test each hop.

**Scoping a non-leaf obligates its entire subtree.**
This is stated in DEC-001 but it is easy to forget. If SYS-REQ-001 is in
scope, every MID-REQ and leaf REQ under it is implicitly obligated. The
partial-vs-total scope signal (DEC-002) handles the top-level case, but the
real tool should also warn when a scoped non-leaf has children that are not
in scope (would be a silent gap in the obligation).

---

## Store Design and Schema

**The `[A-Z][A-Z0-9-]*-[0-9]+` ID pattern is flexible enough.**
It accommodates multi-segment identifiers such as `SYS-REQ-001`, `MID-REQ-003`,
`REQ-0001-042` without schema changes. The regex engine backtracks to find the
rightmost `-[0-9]+` suffix.

**Majority-SHA stale detection is a prototype-only hack.**
Using `Counter(repoBShas).most_common(1)` to infer the "current" repo-B SHA
works when most outcomes are from the same run, but breaks if the store has
many outcomes from different runs at roughly equal frequency. The real
implementation must receive the current SHA explicitly (from the git worktree
or a config file) rather than inferring it.

**Multiple test outcomes per test spec (multi-run) work without changes.**
Several outcomes from different `runId`s can all confirm the same test spec.
Satisfaction only requires that no confirming outcome is stale or unwaived-FAIL.
Having multiple PASS outcomes is redundant but harmless.

**Cross-requirement test specs (one TS verifying multiple reqs) work.**
The loader emits one `seg:Verifies` edge per entry in the `verifies` list.
Satisfaction is computed independently per requirement, so a cross-req TS
contributes Verifies coverage to each target. No special casing needed.

---

## Real-Implementation Landmines (from DEC-003)

- **Do not hash `ast.get_docstring(clean=True)`** — it normalises indentation
  and breaks the raw-byte guarantee. Use `ast.get_source_segment` instead.
- **Comments are invisible to `ast`** — a `#`-pragma marker cannot be used for
  `:implements:` / `:verifies:` markers; they must live in the docstring.
- **Tree-sitter as a future unified locator** — `ast` for Python, doxygen for C
  are two different locator engines. Consolidating on tree-sitter (which ships
  both grammars and gives byte-exact offsets) is a deferred Phase-B call but
  worth tracking.

---

## Open Questions for the Real Implementation

1. **Affirmation UX.** How does the FSM navigate the affirmation backlog?
   The prototype shows the backlog (non-ACTIVE strong edges) but provides no
   workflow for recording a ReviewEvent and transitioning an edge to ACTIVE.

2. **Incremental Merkle update.** Which nodes in the Refines DAG need
   recomputation when a single node changes? The answer is all ancestors in the
   Refines DAG (walking `seg:Refines` edges upward). This is straightforward
   but needs an explicit algorithm and test.

3. **Expiry of waivers.** WAV-001 carries an `expiry` date. The prototype
   treats all waivers as valid. The real implementation must check
   `expiry >= today` and surface expired waivers as a new gap type.

4. **`broken` edge lifecycle.** If a node is deleted, all edges to/from it
   become `broken`. How does the tool detect this at sync time, and what is
   the resolution path (re-add the node, or explicitly delete the edge)?

5. **Partial-scope proof safety.** DEC-002 provides the partial-vs-total signal
   but leaves the safety conclusion to the human. The tool should make it
   impossible to misread a partial-scope "ready" proof as a system-level claim.
   Consider a mandatory warning banner in the proof output when
   `isTotalScope = false`.

6. **Multi-person affirmation.** DEC-004 notes that the current prototype has
   a single FSM who is also author and reviewer. The real system needs
   separation of duties. This affects ReviewEvent schema and the affirmation
   gate logic.
