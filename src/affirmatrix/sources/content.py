"""The content extractor — Implementation and TestSpecification records.

Locates each node's canonical content form in Python source with ``ast`` and
hashes it (SEG-SREQ-001): ``apiHash`` / ``bodyHash`` for an implementation,
``specHash`` / ``implHash`` for a test specification, and the
``:implements:`` / ``:verifies:`` docstring-field markers that declare its
edges.

**The parser is a locator only.** Its output never enters a hash; span
boundaries are defined parser-independently, and the canonical content form for
Python source is the verbatim byte span. Never hash
``ast.get_docstring(clean=True)`` — it normalizes indentation, and a hash over
normalized text no longer answers for the bytes on disk.

Because the marker lives inside the hashed docstring, re-pointing it changes
the intent hash and correctly trips the edge suspect.

Deferred past iteration 0; only the span-hashing primitive lands early.
"""
