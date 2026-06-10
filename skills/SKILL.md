---
name: seg-requirements-authoring
description: >-
  Use when authoring, decomposing, or reviewing SEG requirements. Encodes the
  EARS (Easy Approach to Requirements Syntax) sentence patterns, the
  good-requirement quality rules (atomic, testable, implementation-agnostic,
  unambiguous), and the SEG-specific ID and decomposition conventions
  (SEG-SYS / SEG-SREQ, refines child→parent, acyclic). Trigger whenever writing
  or critiquing requirement needs in doc/requirements.
---

# SEG Requirements Authoring

Every SEG requirement statement is written in an **EARS** pattern, satisfies the
**quality rules**, and follows the **SEG conventions** below. The statement text
is the need's main body — it becomes the requirement's hashed content, so word it
precisely and minimally.

## 1. EARS patterns

Pick the simplest pattern that fits. The system name is the specific actor
(e.g. "the SEG engine", "the content extractor", "the CLI"), and the binding verb
is always **shall**.

| Pattern | Keyword | Template | SEG example |
|---|---|---|---|
| Ubiquitous | (none) | The `<system>` shall `<response>`. | The SEG Toolbox shall derive every node and edge hash solely from raw source bytes. |
| State-driven | **While** | While `<precondition>`, the `<system>` shall `<response>`. | While any in-scope strong edge is not active, the SEG engine shall refuse to generate a proof for that scope. |
| Event-driven | **When** | When `<trigger>`, the `<system>` shall `<response>`. | When a node's source byte span changes, the content extractor shall compute a different hash for that node. |
| Optional feature | **Where** | Where `<feature is included>`, the `<system>` shall `<response>`. | Where a repository uses SHA-256 object IDs, the engine shall accept 64-character repo SHAs. |
| Unwanted behaviour | **If / then** | If `<unwanted condition>`, then the `<system>` shall `<response>`. | If a requested proof scope omits a child of an in-scope requirement, then the engine shall refuse generation. |
| Complex | (combine) | While `<…>`, when `<…>`, the `<system>` shall `<response>`. | While a scope is partial, when generation completes, the engine shall report it as covering a subset of top-level requirements. |

Prefer ubiquitous/event/state forms for normal behaviour; use **If/then** for
error and rejection behaviour. Reach for **complex** only when a single condition
genuinely won't express the requirement.

## 2. Quality rules (complement EARS)

- **One verifiable claim per requirement.** No compound "… and …" hiding two
  requirements; split them.
- **Testable.** Phrased so a single test can pass or fail against it. If you can't
  imagine the test, rewrite the requirement.
- **Implementation-agnostic.** State *what*, not *how*. No data structures,
  algorithms, libraries, or file formats in the statement.
- **Unambiguous.** No vague terms (fast, efficient, robust, user-friendly) without
  a measurable criterion.
- **Consistent terminology.** Use the design vocabulary exactly: node, edge,
  suspect, active, scope, leaf/non-leaf, satisfied. Don't introduce synonyms.
- **Binding voice.** "shall" for requirements. Avoid "should", "may",
  "shall be able to", "support".
- **Necessary and traceable.** Every requirement exists to be implemented and
  tested and links into the refinement tree.

## 3. SEG conventions

- **IDs.** `SEG-SYS-nnn` for system (non-leaf) requirements, `SEG-SREQ-nnn` for
  software (leaf) requirements. IDs are permanent once issued — SWE/TE reference
  them in `:implements:` / `:verifies:` markers.
- **Decomposition.** `refines` points **child → parent** (a software requirement
  refines a system requirement). The `refines` graph must be **acyclic** (DEC-001).
- **Leaves are concrete.** A `SEG-SREQ` is a leaf: it must be specific enough that
  at least one implementation and one test can attach to it directly.
- **System requirements are non-leaf.** A `SEG-SYS` is covered **transitively** by
  its children (DEC-001); it carries no direct implementation or test. Keep it a
  genuine higher-level claim, not a leaf in disguise.
- **Subject naming (house rule).** A `SEG-SYS` requirement's subject is always
  **the SEG Toolbox** (the system as a whole). A `SEG-SREQ` requirement's subject
  is a specific **named software component** (e.g. the content extractor, the
  graph builder, the proof generator), drawn from the agreed component vocabulary.
  Naming the component is *allocation* and is fine; describing *how* it works is a
  design leak and is not. If a requirement needs a component that isn't named yet,
  settle the name with the design first — don't invent one ad hoc.
- **Authoring.** sphinx-needs in `doc/requirements`; the build emits a reproducible
  `needs.json`. The statement field carries the EARS sentence.

## 4. Worked example (hashing / graph-build slice)

```
SEG-SYS-001  (Ubiquitous, non-leaf)
  The SEG Toolbox shall derive every node and edge hash solely from raw source
  bytes, never from a parsed or normalized representation.

  SEG-SREQ-001  (Ubiquitous, refines SEG-SYS-001)
    The content extractor shall compute each content sub-hash as the SHA-256 of
    the verbatim source byte span it covers.

  SEG-SREQ-002  (Event-driven, refines SEG-SYS-001)
    When the source byte span of a node changes, the content extractor shall
    compute a different node hash.

  SEG-SREQ-003  (Ubiquitous, refines SEG-SYS-001)
    The content extractor shall compute identical hashes for identical source
    byte spans across repeated runs.
```

One non-leaf parent, three atomic, testable, implementation-agnostic leaves, each
a single EARS sentence.

## 5. Self-review checklist (before finalizing a requirement)

- [ ] Correct EARS pattern, simplest that fits
- [ ] Exactly one verifiable claim
- [ ] A concrete test could pass/fail against it
- [ ] States *what*, not *how*
- [ ] No vague/unmeasurable terms; consistent vocabulary
- [ ] ID assigned per scheme; `refines` link set (leaf → its parent)
- [ ] Leaf is implementable/testable; system req is a genuine non-leaf claim
