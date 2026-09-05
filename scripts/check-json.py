#!/usr/bin/env python3
"""Parse every public JSON file and reject duplicate JSON object keys."""

from __future__ import annotations

import sys

from check_common import CheckError, ROOT, load_json


EXCLUDED_PARTS = {".git", "dist", "__pycache__"}


def main() -> None:
    files = sorted(
        path
        for path in ROOT.rglob("*.json")
        if not EXCLUDED_PARTS.intersection(path.relative_to(ROOT).parts)
    )
    if not files:
        raise CheckError("no JSON files found")
    for path in files:
        load_json(path)
    print(f"JSON check passed for {len(files)} file(s).")


if __name__ == "__main__":
    try:
        main()
    except CheckError as error:
        print(f"JSON check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
