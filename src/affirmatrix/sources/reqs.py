"""The requirements reader — a thin reader over the built ``needs.json``.

Turns the requirement specification's reproducible export into Requirement
records: the need ID verbatim as the case-local identifier (ADR-0007), the
canonical content form as the hash input (DEC-031), and the ``refines``
declarations as edges.

Two disciplines it must carry:

* **Forward links only.** Back-link fields (``*_back``) are derived by
  sphinx-needs and can go stale in an incremental build; this reader consumes
  the forward ``refines`` and derives the reverse itself.
* **Clean build.** ``needs.json`` is consumed from a clean build; a stale
  export is a wrong input, not a tolerable one.

Deferred past iteration 0 with the rest of record production.
"""
