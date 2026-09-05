#!/usr/bin/env python3
"""Reject symlinks and unsafe archive paths from distributable content."""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path

from check_common import CheckError, ROOT


INCLUDE_FILE = ROOT / "release-include.txt"


def included_roots() -> list[Path]:
    if not INCLUDE_FILE.is_file():
        raise CheckError("missing release archive configuration: release-include.txt")
    roots: list[Path] = []
    for line in INCLUDE_FILE.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        candidate = Path(item)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise CheckError(f"unsafe release include path: {item}")
        path = ROOT / candidate
        if not path.exists() and not path.is_symlink():
            raise CheckError(f"release include path does not exist: {item}")
        roots.append(path)
    if not roots:
        raise CheckError("release archive configuration has no paths")
    return roots


def main() -> None:
    tracked = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    ).stdout.decode("utf-8").split("\0")
    for name in tracked:
        parts = Path(name).parts
        if "__pycache__" in parts or name.endswith((".pyc", ".pyo", ".pyd")):
            raise CheckError(f"tracked cache or temporary artifact is not allowed: {name}")
    checked = 0
    for root in included_roots():
        for path in [root, *root.rglob("*")] if root.is_dir() else [root]:
            relative = path.relative_to(ROOT)
            if path.is_symlink():
                raise CheckError(f"symlinks are not allowed in release content: {relative}")
            if ".." in relative.parts or relative.is_absolute():
                raise CheckError(f"release path escapes its archive: {relative}")
            checked += 1
    print(f"Release path check passed for {checked} path(s).")


if __name__ == "__main__":
    try:
        main()
    except CheckError as error:
        print(f"Path check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
