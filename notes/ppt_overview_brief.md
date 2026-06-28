# PowerPoint Agent Brief — SEG 15-Minute Overview Deck

## Goal

Produce a slide deck for a **15-minute spoken overview** of the Safety Evidence
Graph (SEG), for a **technically literate audience new to SEG**. Goal: the
audience grasps the core idea, the structure, and why it matters — not the
implementation. This brief is self-contained; you do not need other project
files. Use the pptx skill.

## Tone & format

- ~10–12 slides (≈1 min each, leave breathing room). Don't exceed 12.
- Clear and concrete, minimal jargon; one idea per slide; short headlines.
- Speaker delivers the detail — slides carry headlines + a few anchor points +
  visuals, not paragraphs.
- Light, professional visual style.

## Explicitly leave out (below the talk's altitude)

Single-repo/worktree topology, the Python/`ast` realization, branch mechanics,
schema specifics, ID conventions, the agent/iteration workflow. This is the
concept, not the build.

## Slide-by-slide content

**1 — Title.** "Safety Evidence Graph (SEG)". Subtitle: *Turning the safety case
from a manual binder into a computed artifact that watches itself.*

**2 — The problem.** Safety certification (IEC 61508 and kin) demands proof that
software does what its requirements say. Today that proof is a hand-assembled
binder — and it's stale the moment it's signed: code changes, the binder doesn't.
Anchor: *evidence rots; nobody notices until the audit.*

**3 — The one idea (thesis slide).** The relationships between requirements,
tests, and code already exist — they're declared in the source itself. SEG's job
isn't to invent them; it's to **cryptographically bind each link to the content
of both things it connects.** Change either end and the link is automatically
flagged "suspect" until a human re-affirms it. One line on the slide:
*Content-hash bindings on declared relationships, with human affirmation as the
reset.*

**4 — The graph model (diagram slide).** Build this diagram:
- Five node types: **Requirement, Test Specification, Implementation, Test
  Outcome, Waiver.**
- Directed edges, all pointing *up* toward the claim they support:
  Test Specification → Requirement (**verifies**); Implementation → Requirement
  (**implements**); Requirement → Requirement (**refines**, child→parent);
  Test Outcome → Test Specification (**confirms**); Test Outcome → Implementation
  (**witnesses**); Waiver → Test Outcome (**excuses**).
- Two overlaid groups: a **design graph** (Requirement + Test Spec +
  Implementation, with refines/verifies/implements) that is **Merkle-hashed**,
  and an **evidence graph** that adds Test Outcome + Waiver (confirms/witnesses/
  excuses). Colour the two groups differently; keep it clean.

**5 — Where the work lives (four sources).** Nothing lives where the graph lives.
Requirements, code + test specs, and test results each sit in their own source;
the graph itself is separate. Engineers just *tag* their work at the source
(e.g. "this function implements REQ-042"); an extractor discovers the tags. Anchor:
*relationships are declared at the source, not maintained by hand in a matrix.*

**6 — The mechanism that makes it live (the heart).** Every node has a content
hash. A strong link stores a hash of **both** endpoints' content *at the moment a
human affirmed it*. A detector continuously recomputes; if either end changed, the
stored hash no longer matches → the link goes **suspect** and stays suspect until
the responsible person re-affirms. That single trick turns a static traceability
matrix into a live signal. (Note: test-result links can't be "re-affirmed" — the
only fix is to re-run the test.)

**7 — Humans hold the reset.** Suspect links form a visible **worklist**; a named
person reviews what changed and decides whether the relationship still holds.
Affirmation is a *judgment*, not a rubber stamp — that's where the safety value
is. Anchor: *the machine flags; the human decides.*

**8 — What a proof actually is.** Two halves, both required:
- **Design half** — a single Merkle-root fingerprint over the web of declared
  relationships: "this exact design graph is complete and internally consistent;
  recompute it and check."
- **Evidence half** — passing test results, each pinned to the exact code commit
  it ran against.
Guarded by gates (structural check → readiness check → release), and exported in
a standard format (SPDX) for an external auditor.

**9 — Integrity vs. trust (the honest limit).** A green proof is a *mechanical
attestation*: "for this scope, the design is consistent and the evidence passed."
Whether that means "the system is safe" is a **human judgment** about whether the
requirements captured everything that matters — the tool can't prove the
requirement set is complete. Anchor: *SEG proves integrity; people still own
trust.*

**10 — One-sentence takeaway (close).** *SEG is a knowledge graph that
cryptographically pins every safety claim to the exact content backing it, flags
the claim the instant that content drifts, and can fingerprint the whole
consistent state into an auditable proof on demand.*

## Build notes

- Slide 4 is the visual centrepiece — invest in it. Slides 3, 6, and 9 are the
  intellectual beats; keep them crisp.
- If you add slides, prefer splitting slide 6 (mechanism) over adding new topics.
