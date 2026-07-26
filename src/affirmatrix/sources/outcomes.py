"""The outcome extractor — TestOutcome records from test artifacts.

Reads the run's artifacts, maps each result's nodeid back to the stable
``SEG-TS-nnn`` identity (so moving or renaming a test changes neither identity
nor hashes), records the commit SHA the run executed against, and derives the
``confirms`` and ``witnesses`` edges.

The recorded revision is the freshness mechanism: compared against the current
one when a package is generated, a mismatch makes the outcome stale, and a
stale outcome is *discarded* rather than failed — it blocks only if its removal
opens a coverage gap. The current revision is supplied explicitly, never
inferred from the outcomes themselves; guessing it from whichever revision
happens to be most common across the run is how a prototype learns that
inference and evidence do not mix.

pytest is this version's artifact format, not this component's identity.

Deferred past iteration 0 with the rest of record production.
"""
