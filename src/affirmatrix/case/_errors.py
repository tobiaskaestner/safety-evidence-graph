"""The affirmation store's refusal type.

Its own module so that layout, atomicity, serialization and validation can all
raise it without any of them importing the component's public face.
"""

from __future__ import annotations


class AffirmationStoreError(Exception):
    """The affirmation store refuses to write, or cannot read what is there.

    Named in full rather than ``StoreError``, which the would-be store already
    uses. The two stores hold opposite things — one content, one hashes and
    references — and a shared word for their failures would be the first step
    towards a shared word for them (ADR-0004).
    """


__all__ = ["AffirmationStoreError"]
