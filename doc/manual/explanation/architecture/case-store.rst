The case store
==============

``case/`` holds affirmatrix's own safety evidence graph — the nodes, edges,
review events and proofs for this repository's requirements, source markers
and test reports, sealed by the tool itself once the engine lands. It is an
artifact store, not a document, which is why it sits outside ``doc/``.

Its persisted state is an independent commit lineage (ADR-0009): an orphan
branch, ``case``, that shares no history with the code branch and is never
merged into it. In a working checkout, ``case/`` is a ``git worktree`` of that
branch, and the directory is ignored by the code branch. The separation is
structural, not disciplinary — a commit on the store lineage can only touch
the case, because its tree contains nothing else, and a commit on the code
branch cannot touch the case at all. A commit to the lineage by an authorised
committer is a store act; the kind of store act that introduces review events
is an affirmation.

A fresh clone has no case. Building the tool and running its suite need none;
verifying the evidence requires fetching the branch and adding the worktree:

.. code-block:: console

   git fetch origin case
   git worktree add case case

The graph's state is the committed state of that lineage; anything
uncommitted is a draft.
