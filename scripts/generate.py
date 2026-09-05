#!/usr/bin/env python3
"""Generate deterministic platform manifests from the canonical plugin catalog."""

from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import sys
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog" / "plugin.json"
PLUGIN_ROOT = ROOT / "plugins" / "lottiefiles-creator"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated files differ from their canonical output.",
    )
    return parser.parse_args()


def load_catalog() -> dict[str, Any]:
    with CATALOG_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("catalog/plugin.json must contain a JSON object")
    return payload


def remote_server(catalog: dict[str, Any], *, gemini: bool = False) -> dict[str, str]:
    url = catalog["remote"]["productionUrl"]
    if gemini:
        return {"httpUrl": url}
    return {"type": "http", "url": url}


def plugin_manifest(catalog: dict[str, Any]) -> dict[str, Any]:
    links = catalog["links"]
    return {
        "name": catalog["id"],
        "version": catalog["version"],
        "description": catalog["description"],
        "author": {"name": catalog["publisher"]["name"], "url": links["website"]},
        "homepage": links["homepage"],
        "repository": links["repository"],
        "license": "MIT",
        "keywords": catalog["keywords"],
        "skills": "./skills/",
        "mcpServers": "./.mcp.json",
        "interface": {
            "displayName": catalog["displayName"],
            "shortDescription": catalog["description"],
            "longDescription": catalog["longDescription"],
            "developerName": catalog["publisher"]["name"],
            "category": catalog["category"],
            "capabilities": ["Read", "Write"],
            "websiteURL": links["website"],
            "privacyPolicyURL": links["privacyPolicy"],
            "termsOfServiceURL": links["termsOfService"],
            "brandColor": "#00DDB3",
            "defaultPrompt": [
                "Create or edit an authenticated LottieFiles animation.",
                "Export an animation or inspect an export job.",
                "Use the LottieFiles API for an animation workflow."
            ]
        }
    }


def claude_manifest(catalog: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": catalog["id"],
        "version": catalog["version"],
        "description": catalog["description"],
        "author": {"name": catalog["publisher"]["name"]},
        "mcpServers": "./.mcp.json"
    }


def marketplace_entry(catalog: dict[str, Any], source: Any) -> dict[str, Any]:
    return {
        "name": catalog["id"],
        "description": catalog["description"],
        "version": catalog["version"],
        "source": source,
        "category": "creativity",
        "keywords": catalog["keywords"]
    }


def generated_json(catalog: dict[str, Any]) -> dict[Path, dict[str, Any]]:
    server_name = catalog["mcpServerName"]
    description = catalog["description"]
    return {
        ROOT / ".mcp.json": {
            "mcpServers": {server_name: remote_server(catalog)}
        },
        ROOT / "gemini-extension.json": {
            "name": catalog["id"],
            "version": catalog["version"],
            "description": catalog["longDescription"],
            "mcpServers": {server_name: remote_server(catalog, gemini=True)}
        },
        ROOT / "server.json": {
            "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
            "name": "com.lottiefiles/creator",
            "title": catalog["displayName"],
            "description": catalog["longDescription"],
            "version": catalog["version"],
            "remotes": [{"type": "streamable-http", "url": catalog["remote"]["productionUrl"]}]
        },
        ROOT / ".agents" / "plugins" / "marketplace.json": {
            "name": catalog["marketplaceId"],
            "interface": {"displayName": catalog["publisher"]["name"]},
            "plugins": [{
                "name": catalog["id"],
                "source": {"source": "local", "path": f"./plugins/{catalog['id']}"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": catalog["category"]
            }]
        },
        ROOT / ".claude-plugin" / "marketplace.json": {
            "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
            "name": catalog["marketplaceId"],
            "version": catalog["version"],
            "description": description,
            "owner": {"name": catalog["publisher"]["name"]},
            "plugins": [marketplace_entry(catalog, f"./plugins/{catalog['id']}")]
        },
        ROOT / ".grok-plugin" / "marketplace.json": {
            "name": catalog["marketplaceId"],
            "description": description,
            "owner": {"name": catalog["publisher"]["name"]},
            "plugins": [marketplace_entry(catalog, {
                "type": "local", "path": f"./plugins/{catalog['id']}"
            })]
        },
        PLUGIN_ROOT / ".mcp.json": {
            "mcpServers": {server_name: remote_server(catalog)}
        },
        PLUGIN_ROOT / ".codex-plugin" / "plugin.json": plugin_manifest(catalog),
        PLUGIN_ROOT / ".grok-plugin" / "plugin.json": claude_manifest(catalog),
        PLUGIN_ROOT / ".claude-plugin" / "plugin.json": claude_manifest(catalog)
    }


def json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_safe_relative(relative: Path) -> None:
    posix = PurePosixPath(relative.as_posix())
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError(f"unsafe generated path: {relative}")


def sync_tree(source: Path, destination: Path, *, check: bool) -> bool:
    if source.is_symlink() or any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError(f"canonical content must not contain symlinks: {source}")
    if destination.is_symlink() or (
        destination.exists() and any(path.is_symlink() for path in destination.rglob("*"))
    ):
        raise ValueError(f"generated content must not contain symlinks: {destination}")
    source_files = {path.relative_to(source) for path in source.rglob("*") if path.is_file()}
    destination_files = (
        {path.relative_to(destination) for path in destination.rglob("*") if path.is_file()}
        if destination.exists() else set()
    )
    stale = destination_files - source_files
    changed = stale != set()
    for relative in source_files:
        require_safe_relative(relative)
        target = destination / relative
        if not target.is_file() or not filecmp.cmp(source / relative, target, shallow=False):
            changed = True
    if check:
        return changed
    for relative in stale:
        (destination / relative).unlink()
    for relative in sorted(source_files):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, target)
    for directory in sorted((path for path in destination.rglob("*") if path.is_dir()), reverse=True):
        if not any(directory.iterdir()):
            directory.rmdir()
    return changed


def sync_content(*, check: bool) -> list[Path]:
    stale: list[Path] = []
    source_skills = ROOT / "content" / "skills"
    for destination in (PLUGIN_ROOT / "skills", ROOT / "skills"):
        if source_skills.exists():
            if sync_tree(source_skills, destination, check=check):
                stale.append(destination.relative_to(ROOT))
        elif destination.exists():
            if check:
                stale.append(destination.relative_to(ROOT))
            else:
                shutil.rmtree(destination)

    source_assets = ROOT / "content" / "assets"
    destination_assets = PLUGIN_ROOT / "assets"
    if source_assets.exists():
        if sync_tree(source_assets, destination_assets, check=check):
            stale.append(destination_assets.relative_to(ROOT))
    elif destination_assets.exists():
        if check:
            stale.append(destination_assets.relative_to(ROOT))
        else:
            shutil.rmtree(destination_assets)
    return stale


def main() -> int:
    args = parse_args()
    catalog = load_catalog()
    stale: list[Path] = []
    for path, payload in generated_json(catalog).items():
        expected = json_bytes(payload)
        if not path.is_file() or path.read_bytes() != expected:
            stale.append(path.relative_to(ROOT))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(expected)
    stale.extend(sync_content(check=args.check))
    if args.check and stale:
        print("stale generated outputs:", file=sys.stderr)
        for path in stale:
            print(f"- {path.as_posix()}", file=sys.stderr)
        return 1
    if not args.check:
        print("generated platform manifests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
