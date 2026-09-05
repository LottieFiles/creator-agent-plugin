"""Small, dependency-free helpers for distribution checks."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


class CheckError(Exception):
    """An input does not meet a public distribution contract."""


def fail(message: str) -> None:
    raise CheckError(message)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as source:
            return json.load(source, object_pairs_hook=_reject_duplicate_keys)
    except FileNotFoundError:
        fail(f"missing required file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as error:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {error}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(64 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be a JSON object")
    return value


def require_array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be a JSON array")
    return value


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    return value


def require_relative_path(value: Any, label: str, *, base: Path = ROOT) -> Path:
    raw = require_text(value, label)
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        fail(f"{label} must stay inside the repository: {raw}")
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        fail(f"{label} escapes the repository: {raw}")
    return resolved


PRIVATE_PATTERNS = (
    re.compile(r"(?:github\.com|gitlab\.com)[:/]LottieFiles/(?:engine|thorvg-rs)(?:[/.#]|$)", re.I),
    re.compile(r"(?:^|[/:])(?:Users|home)/(?:jaw|runner)/(?:Projects|\.codex)(?:/|$)", re.I),
)

SECRET_PATTERNS = (
    re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"),
)


def assert_public_text(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    for pattern in (*PRIVATE_PATTERNS, *SECRET_PATTERNS):
        if pattern.search(text):
            fail(f"private reference or secret-like value in {path.relative_to(ROOT)}")
