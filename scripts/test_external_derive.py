#!/usr/bin/env python3
"""Test derive expansion across a genuine external package visibility boundary."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--nargo", default=os.environ.get("NARGO_BIN", "nargo"))
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="bigcurve-external-derive-") as directory:
    consumer = Path(directory)
    shutil.copytree(root / "tests/external_derive/src", consumer / "src")
    manifest = (root / "tests/external_derive/Nargo.toml").read_text()
    manifest = manifest.replace('path="../.."', "path=" + json.dumps(str(root)))
    (consumer / "Nargo.toml").write_text(manifest)
    # Move outside the library's workspace so Nargo selects the external package.
    subprocess.run(
        [args.nargo, "check", "--deny-warnings", "--program-dir", str(consumer)],
        check=True,
        timeout=120,
    )
    subprocess.run(
        [
            args.nargo,
            "test",
            "--inliner-aggressiveness",
            "0",
            "--deny-warnings",
            "--program-dir",
            str(consumer),
        ],
        check=True,
        timeout=120,
    )
