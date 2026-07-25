"""The command-line interface — a thin layer over the library (AC-014).

``affirmatrix <noun> <verb>``, configuration from ``affirmatrix.yaml``. The
engine is a library with a clean programmatic core and no logic buried in
command handlers, so a later interface — REST, a review UI, a TUI (DEC-008) —
is another thin adapter over the same core rather than a second implementation.

Iteration 0 ships the minimum needed to drive the three workflows for the
definition of done: consistency, proof generation, suspect detection.

Iteration 0, backlog item B19.
"""
