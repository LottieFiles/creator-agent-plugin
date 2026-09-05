#!/usr/bin/env python3
"""Check license and ownership claims for this metadata-only public package."""

from __future__ import annotations

import sys

from check_common import CheckError, ROOT, load_json, require_object, require_text


def main() -> None:
    for name in ("LICENSE", "CHANGELOG.md", "SECURITY.md", "SUPPORT.md"):
        path = ROOT / name
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            raise CheckError(f"missing {name}; add required public legal or support guidance before release")
    catalog = require_object(load_json(ROOT / "catalog/plugin.json"), "catalog/plugin.json")
    publisher = require_object(catalog.get("publisher"), "catalog.publisher")
    publisher_name = require_text(publisher.get("name"), "catalog.publisher.name")
    for path in (
        ROOT / "plugins/lottiefiles-creator/.codex-plugin/plugin.json",
        ROOT / "plugins/lottiefiles-creator/.claude-plugin/plugin.json",
        ROOT / ".claude-plugin/marketplace.json",
        ROOT / ".grok-plugin/marketplace.json",
    ):
        manifest = require_object(load_json(path), path.relative_to(ROOT).as_posix())
        owner = manifest.get("author", manifest.get("owner"))
        owner = require_object(owner, f"{path.relative_to(ROOT)} owner")
        if require_text(owner.get("name"), f"{path.relative_to(ROOT)} owner.name") != publisher_name:
            raise CheckError(f"publisher ownership drift in {path.relative_to(ROOT)}")
    print("License and publisher provenance checks passed.")


if __name__ == "__main__":
    try:
        main()
    except CheckError as error:
        print(f"Provenance check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
