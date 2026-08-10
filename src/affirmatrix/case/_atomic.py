"""Replacing one file's contents, all at once or not at all.

ADR-0008 requires that an interrupted run never leave a half-written record
behind. With a per-kind collection document as the unit of atomicity, that is
one operation: write the new contents beside the target, then rename over it.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def replace_file(path: Path, payload: bytes) -> None:
    """Give ``path`` these bytes, atomically.

    :implements: SEG-SREQ-022

    The temporary file is created in the target's **own directory**, which is
    what makes the rename a same-filesystem operation and therefore atomic; a
    temporary file elsewhere would degrade into a copy and reintroduce exactly
    the half-written document this exists to prevent.

    The contents are flushed to the device before the rename, so a power loss
    between the two cannot leave a file that has been renamed into place but is
    still empty. On any failure the temporary file is removed, so an
    interrupted run leaves neither a partial document nor a stray file for the
    next reader to wonder about.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


__all__ = ["replace_file"]
