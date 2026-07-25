"""Shared internal — the severity model of the error-handling contract.

Not a component and never a requirement subject. Error / Warning / Info and the
diagnostic record they travel in (design summary §5): Error blocks commit and
proof, Warning blocks proof only, Info is reported. The components that decide
*which* condition earns which severity own those requirements; this module owns
only the vocabulary they share.
"""
