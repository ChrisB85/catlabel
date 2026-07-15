"""Synchronize the public TiMini-Print catalog snapshot used by CatLabel.

This is a maintainer tool, not an installation/runtime dependency.  It reads a
Git revision that is already available locally and writes normalized JSON data
under ``catlabel/vendors/generic/data``.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "catlabel" / "vendors" / "generic" / "data"
UPSTREAM_REPOSITORY = "https://github.com/Dejniel/TiMini-Print"
DEFAULT_REVISION = "v0.7.3"

SOURCES = {
    "catalog_models.json": "timiniprint/data/printer_models.json",
    "catalog_unsupported.json": "timiniprint/data/printer_models_unsupported.json",
    "catalog_profiles.json": "timiniprint/data/printer_profiles.json",
    "catalog_paper_presets.json": "timiniprint/data/printer_paper_presets.json",
    "catalog_origin_apps.json": "timiniprint/data/origin_apps.json",
}


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def sync(revision: str) -> str:
    commit = _git("rev-parse", f"{revision}^{{commit}}").strip()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for destination, source in SOURCES.items():
        raw = _git("show", f"{commit}:{source}")
        parsed = json.loads(raw)
        (DATA_DIR / destination).write_text(
            json.dumps(parsed, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    metadata = {
        "repository": UPSTREAM_REPOSITORY,
        "revision": revision,
        "commit": commit,
        "license": "Apache-2.0",
        "files": SOURCES,
    }
    (DATA_DIR / "catalog_source.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return commit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "revision",
        nargs="?",
        default=DEFAULT_REVISION,
        help=f"TiMini-Print Git revision (default: {DEFAULT_REVISION})",
    )
    args = parser.parse_args()
    commit = sync(args.revision)
    print(f"Synchronized TiMini-Print catalog from {commit}")


if __name__ == "__main__":
    main()
