#!/usr/bin/env python3
"""Prove release archives are reproducible and safe to unpack."""

from __future__ import annotations

import shutil
import sys
import tempfile
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

from check_common import CheckError, ROOT, load_json, require_text, sha256
from package import archive_path, included_files, package


def safe_member(name: str) -> None:
    value = PurePosixPath(name)
    if value.is_absolute() or ".." in value.parts or not value.parts:
        raise CheckError(f"unsafe archive member: {name}")


def smoke_tar(path: Path, expected: set[str]) -> None:
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        if not members:
            raise CheckError(f"empty tar archive: {path.name}")
        names = {member.name for member in members}
        if names != expected:
            raise CheckError("tar archive members differ from release-include.txt")
        for member in members:
            safe_member(member.name)
            if not member.isfile() or member.issym() or member.islnk():
                raise CheckError(f"tar archive has a non-regular member: {member.name}")


def smoke_zip(path: Path, expected: set[str]) -> None:
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if not members:
            raise CheckError(f"empty ZIP archive: {path.name}")
        names = {member.filename for member in members}
        if names != expected:
            raise CheckError("ZIP archive members differ from release-include.txt")
        for member in members:
            safe_member(member.filename)
            if member.is_dir():
                raise CheckError(f"ZIP archive member is invalid: {member.filename}")


def main() -> None:
    catalog = load_json(ROOT / "catalog" / "plugin.json")
    if not isinstance(catalog, dict):
        raise CheckError("catalog/plugin.json must be a JSON object")
    version = require_text(catalog.get("version"), "catalog.version")
    expected = {archive_path(version, path.relative_to(ROOT)) for path in included_files()}
    with tempfile.TemporaryDirectory(prefix="creator-agent-plugin-") as temporary:
        first = Path(temporary) / "first"
        second = Path(temporary) / "second"
        one = package(first, version)
        two = package(second, version)
        for before, after in zip(one, two, strict=True):
            if sha256(before) != sha256(after):
                raise CheckError(f"archive is not reproducible: {before.name}")
        smoke_tar(one[0], expected)
        smoke_zip(one[1], expected)
    print("Reproducible archive smoke test passed.")


if __name__ == "__main__":
    try:
        main()
    except CheckError as error:
        print(f"Package smoke test failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
