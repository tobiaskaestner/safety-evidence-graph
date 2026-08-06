"""The content extractor — Implementation and TestSpecification records.

Locates each node's canonical content form in Python source with ``ast`` and
hashes it (SEG-SREQ-001): ``apiHash`` / ``bodyHash`` for an implementation,
``specHash`` / ``implHash`` for a test specification, and the docstring-field
markers that declare its identity and its edges.

Both ``:implements:`` and ``:verifies:`` name a requirement, so a ``Verifies``
edge runs from a test specification to the requirement, never to another
specification. A test carries ``:test-id:`` as well, because implementation
identity is the dotted path and needs no marker, whereas a specification
identity is manual and deliberately independent of the test function's name and
location — so for tests it has to be stated rather than derived.

**The parser is a locator only.** Its output never enters a hash; span
boundaries are defined parser-independently, and the canonical content form for
Python source is the verbatim byte span. Never hash
``ast.get_docstring(clean=True)`` — it normalizes indentation, and a hash over
normalized text no longer answers for the bytes on disk.

Because the marker lives inside the hashed docstring, re-pointing it changes
the intent hash and correctly trips the edge suspect.

Deferred past iteration 0; only the span-hashing primitive lands early.
"""
