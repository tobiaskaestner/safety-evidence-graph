"""Package smoke tests."""

import affirmatrix


def test_version() -> None:
    assert affirmatrix.__version__.startswith("0.0.1")
