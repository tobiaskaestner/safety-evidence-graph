"""Shared internal — the severity model of the error-handling contract.

Not a component and never a requirement subject. Error, warning and info, and
the diagnostic record they travel in: an error blocks both committing and
generating an evidence package, a warning blocks the package only, and info is
reported without blocking anything. The components that decide *which*
condition earns which severity own those requirements; this module owns only
the vocabulary they share.
"""
