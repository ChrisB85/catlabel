from __future__ import annotations

import os

DEFAULT_DATA_DIR = "data"


def data_dir() -> str:
    """Directory holding the database, fonts and imported assets."""
    return os.environ.get("CATLABEL_DATA_DIR") or DEFAULT_DATA_DIR


def fonts_dir() -> str:
    """Directory holding font files served under /fonts."""
    return os.path.join(data_dir(), "fonts")
