#!/usr/bin/env python3
"""Verify every generated manifest version equals the release tag version."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from check_common import CheckError, ROOT, load_json


MANIFESTS = (
    ROOT / "catalog/plugin.json",
    ROOT / "gemini-extension.json",
    ROOT / "server.json",
    ROOT / ".claude-plugin/marketplace.json",
    ROOT / ".grok-plugin/marketplace.json",
    ROOT / "plugins/lottiefiles-creator/.codex-plugin/plugin.json",
    ROOT / "plugins/lottiefiles-creator/.claude-plugin/plugin.json",
)


def versions(value: Any, location: str) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "version":
                if not isinstance(child, str):
                    raise CheckError(f"{location}.version must be a string")
                found.append(child)
            found.extend(versions(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(versions(child, f"{location}[{index}]"))
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="release tag in vMAJOR.MINOR.PATCH form")
    args = parser.parse_args()
    if not args.tag.startswith("v") or len(args.tag) == 1:
        raise CheckError("release tag must start with v")
    expected = args.tag[1:]
    for path in MANIFESTS:
        payload = load_json(path)
        found = versions(payload, path.relative_to(ROOT).as_posix())
        if not found:
            raise CheckError(f"manifest has no version fields: {path.relative_to(ROOT)}")
        if any(version != expected for version in found):
            raise CheckError(f"manifest version differs from release tag: {path.relative_to(ROOT)}")
    print(f"All manifest versions equal {expected}.")


if __name__ == "__main__":
    try:
        main()
    except CheckError as error:
        print(f"Version check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
