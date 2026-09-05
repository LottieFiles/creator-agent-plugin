#!/usr/bin/env python3
"""Check Markdown and Agent Skills frontmatter without a YAML dependency."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from check_common import CheckError, ROOT, require_text


FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.+?)\s*$")


def skill_files() -> list[Path]:
    return (
        sorted(ROOT.glob("content/skills/**/SKILL.md"))
        + sorted(ROOT.glob("skills/**/SKILL.md"))
        + sorted(ROOT.glob("plugins/**/skills/**/SKILL.md"))
    )


def parse_frontmatter(path: Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(source)
    if not match:
        raise CheckError(f"skill has no YAML frontmatter: {path.relative_to(ROOT)}")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        field = FIELD.match(line)
        if not field:
            raise CheckError(
                f"skill frontmatter must use simple key/value fields: {path.relative_to(ROOT)}"
            )
        key, value = field.groups()
        if key in fields:
            raise CheckError(f"duplicate skill frontmatter key {key}: {path.relative_to(ROOT)}")
        fields[key] = value.strip().strip("\"'")
    require_text(fields.get("name"), f"{path.relative_to(ROOT)} frontmatter.name")
    require_text(fields.get("description"), f"{path.relative_to(ROOT)} frontmatter.description")
    if not source[match.end() :].strip():
        raise CheckError(f"skill body is empty: {path.relative_to(ROOT)}")
    return fields


def main() -> None:
    markdown = sorted(ROOT.rglob("*.md"))
    if not markdown:
        raise CheckError("no Markdown files found")
    for path in markdown:
        if ".git" in path.parts:
            continue
        if path.name == "SKILL.md":
            parse_frontmatter(path)
        elif not path.read_text(encoding="utf-8").strip():
            raise CheckError(f"empty Markdown file: {path.relative_to(ROOT)}")
    print("Markdown and skill frontmatter checks passed.")


if __name__ == "__main__":
    try:
        main()
    except (CheckError, UnicodeDecodeError) as error:
        print(f"Content check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
