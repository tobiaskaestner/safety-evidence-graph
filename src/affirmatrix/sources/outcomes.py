"""The outcome extractor — TestOutcome records from test artifacts.

Reads the run's artifacts, maps each result's nodeid back to the stable
``SEG-TS-nnn`` identity (so moving or renaming a test changes neither identity
nor hashes), records the commit SHA the run executed against, and derives the
``confirms`` and ``witnesses`` edges.

The recorded SHA is the freshness mechanism: compared against current HEAD at
proof time, a mismatch makes the outcome stale, and a stale outcome is
*discarded* from the proof rather than failed — it blocks only if its removal
opens a coverage gap. The current SHA is supplied explicitly, never inferred
from the outcomes themselves.

pytest is v1's artifact format, not this component's identity.

Deferred past iteration 0 with the rest of record production.
"""
