#!/usr/bin/env python3
"""Create deterministic source distribution archives from release-include.txt."""

from __future__ import annotations

import argparse
import gzip
import io
import shutil
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from check_common import CheckError, ROOT, assert_public_text, load_json, require_text, sha256


INCLUDE = ROOT / "release-include.txt"
EPOCH = 315532800  # 1980-01-01T00:00:00Z; valid for both tar and ZIP.


def included_files() -> list[Path]:
    if not INCLUDE.is_file():
        raise CheckError("missing release archive configuration: release-include.txt")
    files: set[Path] = set()
    for raw in INCLUDE.read_text(encoding="utf-8").splitlines():
        value = raw.strip()
        if not value or value.startswith("#"):
            continue
        relative = PurePosixPath(value)
        if relative.is_absolute() or ".." in relative.parts:
            raise CheckError(f"unsafe release include path: {value}")
        source = ROOT / relative
        if source.is_symlink() or not source.exists():
            raise CheckError(f"release include path is missing or a symlink: {value}")
        candidates = source.rglob("*") if source.is_dir() else [source]
        for path in candidates:
            if path.is_symlink():
                raise CheckError(f"symlinks are not allowed in release content: {path.relative_to(ROOT)}")
            if path.is_file():
                assert_public_text(path)
                files.add(path)
    if not files:
        raise CheckError("release archive has no files")
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


def archive_path(version: str, relative: Path) -> str:
    path = PurePosixPath("lottiefiles-creator") / version / PurePosixPath(relative.as_posix())
    if path.is_absolute() or ".." in path.parts:
        raise CheckError(f"unsafe archive member: {path}")
    return path.as_posix()


def build_tar(path: Path, version: str, files: list[Path]) -> None:
    with path.open("wb") as target, gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=EPOCH) as zipped:
        with tarfile.open(fileobj=zipped, mode="w") as archive:
            for source in files:
                data = source.read_bytes()
                member = tarfile.TarInfo(archive_path(version, source.relative_to(ROOT)))
                member.size = len(data)
                member.mode = 0o644
                member.mtime = EPOCH
                member.uid = 0
                member.gid = 0
                member.uname = ""
                member.gname = ""
                archive.addfile(member, io.BytesIO(data))


def build_zip(path: Path, version: str, files: list[Path]) -> None:
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in files:
            member = zipfile.ZipInfo(archive_path(version, source.relative_to(ROOT)), date_time=(1980, 1, 1, 0, 0, 0))
            member.compress_type = zipfile.ZIP_DEFLATED
            member.external_attr = 0o100644 << 16
            archive.writestr(member, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def package(output: Path, version: str) -> tuple[Path, Path]:
    output.mkdir(parents=True, exist_ok=True)
    files = included_files()
    stem = f"lottiefiles-creator-{version}"
    tar_path = output / f"{stem}.tar.gz"
    zip_path = output / f"{stem}.zip"
    build_tar(tar_path, version, files)
    build_zip(zip_path, version, files)
    return tar_path, zip_path


def write_checksums(paths: tuple[Path, Path]) -> Path:
    checksum_path = paths[0].with_suffix("").with_suffix(".sha256")
    lines = [f"{sha256(path)}  {path.name}" for path in paths]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksum_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="directory for release archives")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog = load_json(ROOT / "catalog" / "plugin.json")
    if not isinstance(catalog, dict):
        raise CheckError("catalog/plugin.json must be a JSON object")
    version = require_text(catalog.get("version"), "catalog.version")
    tar_path, zip_path = package(args.output, version)
    checksum_path = write_checksums((tar_path, zip_path))
    print(f"created {tar_path} ({sha256(tar_path)})")
    print(f"created {zip_path} ({sha256(zip_path)})")
    print(f"created {checksum_path}")


if __name__ == "__main__":
    try:
        main()
    except CheckError as error:
        print(f"Package failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
