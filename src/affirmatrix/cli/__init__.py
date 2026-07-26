"""The command-line interface — a thin layer over the library.

``affirmatrix <noun> <verb>`` (SEG-SYS-010), configuration from
``affirmatrix.yaml``. The engine is a library with a clean programmatic core
and no logic buried in command handlers, so a later interface — a web API, a
review UI, a terminal UI — is another thin adapter over the same core rather
than a second implementation of the same rules.

Iteration 0 ships the minimum needed to drive the three workflows the
definition of done names: consistency, evidence-package generation, and
suspect detection.

Iteration-0 backlog item B19.
"""
