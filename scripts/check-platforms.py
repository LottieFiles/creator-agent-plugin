#!/usr/bin/env python3
"""Check the generated shapes required by each supported public platform."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from check_common import (
    CheckError,
    ROOT,
    load_json,
    require_array,
    require_object,
    require_relative_path,
    require_text,
)


PLUGIN = ROOT / "plugins" / "lottiefiles-creator"


def member(value: Any, key: str, label: str) -> Any:
    return require_object(value, label).get(key)


def mcp_http(payload: dict[str, Any], name: str, label: str, *, gemini: bool = False) -> None:
    server = require_object(member(payload, "mcpServers", label), f"{label}.mcpServers").get(name)
    server = require_object(server, f"{label}.mcpServers.{name}")
    url_key = "httpUrl" if gemini else "url"
    url = require_text(server.get(url_key), f"{label}.mcpServers.{name}.{url_key}")
    if not url.startswith("https://"):
        raise CheckError(f"{label}.mcpServers.{name}.{url_key} must use HTTPS")
    if not gemini and server.get("type") != "http":
        raise CheckError(f"{label}.mcpServers.{name}.type must be http")


def local_path(value: Any, label: str) -> None:
    path = require_relative_path(value, label)
    if not path.is_dir():
        raise CheckError(f"{label} must resolve to a directory")


def marketplace_entry(payload: dict[str, Any], label: str) -> dict[str, Any]:
    entries = require_array(payload.get("plugins"), f"{label}.plugins")
    if len(entries) != 1:
        raise CheckError(f"{label}.plugins must contain exactly one plugin")
    return require_object(entries[0], f"{label}.plugins[0]")


def main() -> None:
    catalog = require_object(load_json(ROOT / "catalog" / "plugin.json"), "catalog/plugin.json")
    plugin_id = require_text(catalog.get("id"), "catalog.id")
    marketplace_id = require_text(catalog.get("marketplaceId"), "catalog.marketplaceId")
    server_name = require_text(catalog.get("mcpServerName"), "catalog.mcpServerName")
    version = require_text(catalog.get("version"), "catalog.version")

    # Codex marketplace and plugin manifest.
    codex_market = require_object(load_json(ROOT / ".agents/plugins/marketplace.json"), "Codex marketplace")
    if codex_market.get("name") != marketplace_id:
        raise CheckError("Codex marketplace name differs from catalog.marketplaceId")
    codex_entry = marketplace_entry(codex_market, "Codex marketplace")
    if codex_entry.get("name") != plugin_id:
        raise CheckError("Codex marketplace plugin name differs from catalog.id")
    source = require_object(codex_entry.get("source"), "Codex marketplace plugin source")
    if source.get("source") != "local":
        raise CheckError("Codex marketplace plugin source must be local")
    local_path(source.get("path"), "Codex marketplace plugin source.path")
    policy = require_object(codex_entry.get("policy"), "Codex marketplace plugin policy")
    if policy.get("installation") != "AVAILABLE" or policy.get("authentication") != "ON_INSTALL":
        raise CheckError("Codex marketplace plugin policy must request install authentication")
    codex = require_object(load_json(PLUGIN / ".codex-plugin/plugin.json"), "Codex plugin manifest")
    if codex.get("name") != plugin_id or codex.get("version") != version:
        raise CheckError("Codex plugin manifest name or version differs from catalog")
    local_path((PLUGIN.relative_to(ROOT) / str(codex.get("skills", ""))).as_posix(), "Codex plugin skills")
    mcp_reference = require_relative_path(
        (PLUGIN.relative_to(ROOT) / str(codex.get("mcpServers", ""))).as_posix(),
        "Codex plugin mcpServers",
    )
    if not mcp_reference.is_file():
        raise CheckError("Codex plugin mcpServers must resolve to a file")

    # Claude marketplace and plugin manifest. This manifest is also the ZCode
    # Claude fallback; it must retain a local MCP configuration.
    claude_market = require_object(load_json(ROOT / ".claude-plugin/marketplace.json"), "Claude marketplace")
    if claude_market.get("name") != marketplace_id or claude_market.get("version") != version:
        raise CheckError("Claude marketplace name or version differs from catalog")
    claude_entry = marketplace_entry(claude_market, "Claude marketplace")
    if claude_entry.get("name") != plugin_id or claude_entry.get("version") != version:
        raise CheckError("Claude marketplace plugin name or version differs from catalog")
    local_path(claude_entry.get("source"), "Claude marketplace plugin source")
    claude = require_object(load_json(PLUGIN / ".claude-plugin/plugin.json"), "Claude plugin manifest")
    if claude.get("name") != plugin_id or claude.get("version") != version:
        raise CheckError("Claude plugin manifest name or version differs from catalog")
    fallback = require_relative_path(
        (PLUGIN.relative_to(ROOT) / str(claude.get("mcpServers", ""))).as_posix(),
        "ZCode Claude fallback mcpServers",
    )
    if not fallback.is_file():
        raise CheckError("ZCode Claude fallback mcpServers must resolve to a file")
    for path in (
        PLUGIN / "contracts/public-mcp-v1.json",
        PLUGIN / "contracts/public-mcp-v1.sha256",
    ):
        if not path.is_file():
            raise CheckError(f"plugin-local public contract is missing: {path.relative_to(ROOT)}")

    # Grok marketplace.
    grok = require_object(load_json(ROOT / ".grok-plugin/marketplace.json"), "Grok marketplace")
    if grok.get("name") != marketplace_id:
        raise CheckError("Grok marketplace name differs from catalog.marketplaceId")
    grok_entry = marketplace_entry(grok, "Grok marketplace")
    if grok_entry.get("name") != plugin_id or grok_entry.get("version") != version:
        raise CheckError("Grok marketplace plugin name or version differs from catalog")
    grok_source = require_object(grok_entry.get("source"), "Grok marketplace plugin source")
    if grok_source.get("type") != "local":
        raise CheckError("Grok marketplace plugin source.type must be local")
    local_path(grok_source.get("path"), "Grok marketplace plugin source.path")

    # Gemini, standard MCP, and the official MCP Registry server.json.
    gemini = require_object(load_json(ROOT / "gemini-extension.json"), "Gemini root manifest")
    if gemini.get("name") != plugin_id or gemini.get("version") != version:
        raise CheckError("Gemini root manifest name or version differs from catalog")
    mcp_http(gemini, server_name, "Gemini root manifest", gemini=True)
    root_mcp = require_object(load_json(ROOT / ".mcp.json"), "root MCP manifest")
    plugin_mcp = require_object(load_json(PLUGIN / ".mcp.json"), "plugin MCP manifest")
    mcp_http(root_mcp, server_name, "root MCP manifest")
    mcp_http(plugin_mcp, server_name, "plugin MCP manifest")
    registry = require_object(load_json(ROOT / "server.json"), "MCP Registry server.json")
    if registry.get("version") != version:
        raise CheckError("MCP Registry server.json version differs from catalog")
    remotes = require_array(registry.get("remotes"), "MCP Registry server.json remotes")
    if len(remotes) != 1:
        raise CheckError("MCP Registry server.json must define exactly one remote")
    remote = require_object(remotes[0], "MCP Registry server.json remotes[0]")
    if remote.get("type") != "streamable-http":
        raise CheckError("MCP Registry server.json remote must use streamable-http")
    if not require_text(remote.get("url"), "MCP Registry server.json remote URL").startswith("https://"):
        raise CheckError("MCP Registry server.json remote URL must use HTTPS")

    print("Platform conformance checks passed.")


if __name__ == "__main__":
    try:
        main()
    except CheckError as error:
        print(f"Platform conformance failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
