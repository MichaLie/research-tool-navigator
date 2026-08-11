#!/usr/bin/env python3
"""Fetch the three published catalogue JSONs for standalone use.

The navigator normally reads the catalogues from sibling checkouts
(`../Foundation_models/`, `../Autonomous_Agents/`, `../Coding_Agents/`).
A standalone clone can instead download the published FAIR distributions
into `catalogues/` and pass explicit paths to `navigator.py search`.

Uses only the Python standard library. Downloads are read-only public
files; SHA-256 hashes are printed so provenance stays visible.
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

PUBLISHED = {
    "models_final.json": "https://michalie.github.io/bio-foundation-models-wiki/models_final.json",
    "agents_final.json": "https://michalie.github.io/autonomous-stem-agents-wiki/agents_final.json",
    "tools.json": "https://michalie.github.io/research-coding-agents-wiki/tools.json",
}

TARGET = Path(__file__).resolve().parents[1] / "catalogues"


def main() -> int:
    TARGET.mkdir(exist_ok=True)
    for name, url in PUBLISHED.items():
        dest = TARGET / name
        print(f"fetching {url}")
        with urllib.request.urlopen(url, timeout=60) as response:
            payload = response.read()
        dest.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        print(f"  -> {dest.relative_to(TARGET.parent)}  {len(payload):,} bytes  sha256={digest}")
    print(
        "\nSearch with explicit catalogue paths:\n"
        "  python3 scripts/navigator.py search \\\n"
        "    --profile <query-profile.json> \\\n"
        "    --foundation-catalogue catalogues/models_final.json \\\n"
        "    --autonomous-catalogue catalogues/agents_final.json \\\n"
        "    --coding-catalogue catalogues/tools.json \\\n"
        "    --output runs/<request-id>/retrieval-results.json\n"
        "\nNote: published distributions may be newer or older than any local\n"
        "sibling checkout; the recorded hashes identify exactly what was searched."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
