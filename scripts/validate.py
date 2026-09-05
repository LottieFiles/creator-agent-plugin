#!/usr/bin/env python3
"""Validate source metadata and generated plugin distribution files without a network."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "plugin.json"
EXPECTED = (
    ROOT / ".mcp.json",
    ROOT / "gemini-extension.json",
    ROOT / "server.json",
    ROOT / ".agents" / "plugins" / "marketplace.json",
    ROOT / ".claude-plugin" / "marketplace.json",
    ROOT / ".grok-plugin" / "marketplace.json",
    ROOT / "plugins" / "lottiefiles-creator" / ".mcp.json",
    ROOT / "plugins" / "lottiefiles-creator" / ".codex-plugin" / "plugin.json",
    ROOT / "plugins" / "lottiefiles-creator" / ".grok-plugin" / "plugin.json",
    ROOT / "plugins" / "lottiefiles-creator" / ".claude-plugin" / "plugin.json"
)
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SECRET_KEY = re.compile(r"(api[-_]?key|secret|password|token|authorization|credential)", re.I)
SECRET_VALUE = re.compile(r"(sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,})")
PATH_KEY = re.compile(r"^(path|source|skills|assets)$", re.I)


def no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate JSON key: {key}")
        payload[key] = value
    return payload


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_object)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"JSON object required: {path.relative_to(ROOT)}")
        return None
    return value


def validate_tree(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if ".git" in path.relative_to(ROOT).parts:
            continue
        if path.is_symlink():
            errors.append(f"symlinks are not allowed: {path.relative_to(ROOT)}")


def validate_secrets(value: Any, location: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if SECRET_KEY.search(key):
                errors.append(f"secret-looking key is not allowed: {location}.{key}")
            validate_secrets(child, f"{location}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_secrets(child, f"{location}[{index}]", errors)
    elif isinstance(value, str) and SECRET_VALUE.search(value):
        errors.append(f"secret-looking value is not allowed: {location}")


def validate_paths(value: Any, location: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if PATH_KEY.fullmatch(key) and isinstance(child, str) and not child.startswith("https://"):
                parts = Path(child).parts
                if Path(child).is_absolute() or ".." in parts:
                    errors.append(f"path traversal is not allowed: {child_location}")
            validate_paths(child, child_location, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_paths(child, f"{location}[{index}]", errors)


def validate_https(value: Any, location: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f"HTTPS URL required: {location}")
        return
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append(f"HTTPS URL required: {location}")


def value_at(payload: dict[str, Any], *keys: str) -> Any:
    value: Any = payload
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def run_generator_check(errors: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        errors.append(f"generated outputs are stale: {detail}")


def main() -> int:
    errors: list[str] = []
    validate_tree(errors)
    catalog = load_json(CATALOG, errors)
    payloads = {path: load_json(path, errors) for path in EXPECTED}
    for path, payload in payloads.items():
        if payload is not None:
            validate_secrets(payload, path.relative_to(ROOT).as_posix(), errors)
            validate_paths(payload, path.relative_to(ROOT).as_posix(), errors)
    if catalog is not None:
        plugin_id = catalog.get("id")
        version = catalog.get("version")
        remote = value_at(catalog, "remote", "productionUrl")
        if plugin_id != "lottiefiles-creator":
            errors.append("catalog id must be lottiefiles-creator")
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            errors.append("catalog version must be strict semver")
        validate_https(remote, "catalog.remote.productionUrl", errors)
        if set(catalog.get("remote", {})) != {"productionUrl"}:
            errors.append("catalog remote metadata must publish only productionUrl")
        links = catalog.get("links")
        if not isinstance(links, dict):
            errors.append("catalog links must be an object")
        else:
            for key in ("homepage", "repository", "website", "privacyPolicy", "termsOfService"):
                validate_https(links.get(key), f"catalog.links.{key}", errors)
        if catalog.get("category") != "Creativity":
            errors.append("catalog category must be Creativity")
        for path, payload in payloads.items():
            if payload is None:
                continue
            candidate_id = payload.get("name")
            if path.name == "server.json":
                if candidate_id != "com.lottiefiles/creator":
                    errors.append("server.json name must be com.lottiefiles/creator")
            elif candidate_id is not None and candidate_id not in {plugin_id, catalog.get("marketplaceId")}:
                errors.append(f"name drift in {path.relative_to(ROOT)}")
            candidate_version = payload.get("version")
            if candidate_version is not None and candidate_version != version:
                errors.append(f"version drift in {path.relative_to(ROOT)}")
        for path, payload in payloads.items():
            if payload is None:
                continue
            for server in value_at(payload, "mcpServers").values() if isinstance(value_at(payload, "mcpServers"), dict) else []:
                validate_https(server.get("url", server.get("httpUrl")), f"{path.relative_to(ROOT)} MCP URL", errors)
        server = payloads.get(ROOT / "server.json")
        if server is not None:
            server_description = server.get("description")
            if not isinstance(server_description, str) or len(server_description) > 100:
                errors.append("server.json description must be at most 100 characters")
            remotes = server.get("remotes")
            if not isinstance(remotes, list) or len(remotes) != 1 or remotes[0].get("type") != "streamable-http":
                errors.append("server.json must define one streamable-http remote")
            else:
                validate_https(remotes[0].get("url"), "server.json remotes[0].url", errors)
        if "allowedTools" in catalog or "toolAllowlist" in catalog:
            errors.append("catalog must not narrow the LottieFiles GraphQL surface")
    run_generator_check(errors)
    if errors:
        print("validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
