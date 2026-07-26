0002. Mono-repo with a federated document set
=============================================

Status
------

Accepted, 2026-07-24.

Context
-------

The research workspace this tool grew out of models the four-stream trust
topology as four branches checked out as worktrees: requirements,
implementation, results, and graph evolve under different owners, and the
separation is what makes the trust boundary between them visible. An OSS
repository, by contrast, must be clone-and-build for contributors.

Decision
--------

This repository is an ordinary **mono-repo**. Stream separation is carried
by content hashes (the engine's identity mechanism is topology-agnostic),
scoped per-document version tags (``docs/srs/v*``), and path-based
ownership. The requirement specification, test specification, and test
report live as **separate Sphinx documents** federated through a central
registry (``doc/documents.yaml``), each independently buildable and
versionable — the cygnus multi-document pattern. Build orchestration is a
first-party ``python -m doc`` driver (two-stage index/build); no CMake.

The four-stream topology is **retained as a supported configuration and
conformance fixture**, exercised by integration tests against the
four-worktree layout it came from.

Consequences
------------

- "Requirements lead code" moves from topology into review discipline.
- The multi-repo flagship case must stay CI-exercised (fixture, not
  folklore).
- This repo dogfoods its own tool: the specification documents are the
  first safety evidence graph affirmatrix seals (``case/``).
