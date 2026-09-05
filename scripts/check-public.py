#!/usr/bin/env python3
"""Reject private paths and secret-shaped text in public distribution inputs."""

from __future__ import annotations

import sys
from pathlib import Path

from check_common import CheckError, ROOT, assert_public_text


EXCLUDED = {".git", "dist", "__pycache__"}


def main() -> None:
    checked = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or EXCLUDED.intersection(path.relative_to(ROOT).parts):
            continue
        assert_public_text(path)
        checked += 1
    print(f"Public-reference check passed for {checked} file(s).")


if __name__ == "__main__":
    try:
        main()
    except CheckError as error:
        print(f"Public-reference check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
