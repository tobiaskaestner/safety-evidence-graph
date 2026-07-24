# affirmatrix — test specification (Sphinx + sphinx-needs)
# Thin per-document shim; all shared configuration lives in doc/conf_common.py.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from conf_common import configure

configure(globals(), doc_dir=Path(__file__).resolve().parent)
