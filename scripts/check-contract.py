#!/usr/bin/env python3
"""Validate the public Engine MCP tool snapshot used by skills and examples."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from check_common import (
    CheckError,
    ROOT,
    assert_public_text,
    load_json,
    require_array,
    require_object,
    require_text,
    sha256,
)


CONTRACT = ROOT / "contracts" / "public-mcp-v1.json"
DIGEST = ROOT / "contracts" / "public-mcp-v1.sha256"
TOOL_TOKEN = re.compile(r"\b(?:engine_[a-z0-9_]+|request_upload|lf_graphql)\b")
DIGEST_LINE = re.compile(
    r"^([a-f0-9]{64})(?:\s+contracts/public-mcp-v1\.json)?\s*$"
)
EXPECTED_TOOLS = {
    "engine_cancel_job",
    "engine_docs",
    "engine_document",
    "engine_exec",
    "engine_export",
    "engine_job_result",
    "engine_job_status",
    "lf_graphql",
    "request_upload",
}
OAUTH_SECURITY = [{"type": "oauth2", "scopes": ["mcp:full"]}]


def adapt_tools(payload: Any) -> list[Any]:
    """Accept the two stable tools/list JSON envelopes and reject all others."""
    root = require_object(payload, "contract root")
    if "tools" in root:
        return require_array(root["tools"], "contract.tools")
    result = root.get("result")
    if isinstance(result, dict) and "tools" in result:
        return require_array(result["tools"], "contract.result.tools")
    raise CheckError(
        "unsupported contract envelope: expected tools or result.tools; update adapt_tools once the public snapshot format is pinned"
    )


def check_digest() -> None:
    if not CONTRACT.is_file():
        raise CheckError(
            "missing contracts/public-mcp-v1.json; add the reviewed public tools/list snapshot before running distribution checks"
        )
    if not DIGEST.is_file():
        raise CheckError(
            "missing contracts/public-mcp-v1.sha256; add the SHA-256 digest for the public tools/list snapshot"
        )
    lines = [line for line in DIGEST.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 1:
        raise CheckError("contract digest must contain exactly one SHA-256 line")
    match = DIGEST_LINE.fullmatch(lines[0])
    if not match:
        raise CheckError("contract digest must be the reviewed public snapshot SHA-256 and source label")
    actual = sha256(CONTRACT)
    if match.group(1) != actual:
        raise CheckError(f"contract digest mismatch: expected {match.group(1)}, got {actual}")


def check_schema(tool: Any, index: int) -> str:
    label = f"tool[{index}]"
    value = require_object(tool, label)
    name = require_text(value.get("name"), f"{label}.name")
    require_text(value.get("description"), f"{label}.description")
    input_schema = require_object(value.get("inputSchema"), f"{label}.inputSchema")
    output_schema = require_object(value.get("outputSchema"), f"{label}.outputSchema")
    if input_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise CheckError(f"{label}.inputSchema must use JSON Schema draft 2020-12")
    if output_schema.get("type") != "object":
        raise CheckError(f"{label}.outputSchema.type must be object")
    annotations = require_object(value.get("annotations"), f"{label}.annotations")
    require_text(annotations.get("title"), f"{label}.annotations.title")
    for key in ("readOnlyHint", "destructiveHint", "openWorldHint", "idempotentHint"):
        if not isinstance(annotations.get(key), bool):
            raise CheckError(f"{label}.annotations.{key} must be a boolean")
    if annotations["readOnlyHint"] and annotations["destructiveHint"]:
        raise CheckError(f"{label} cannot be both read-only and destructive")
    security = value.get("securitySchemes")
    if security != OAUTH_SECURITY:
        raise CheckError(f"{label}.securitySchemes must require mcp:full OAuth2")
    meta = require_object(value.get("_meta"), f"{label}._meta")
    if meta.get("securitySchemes") != OAUTH_SECURITY:
        raise CheckError(f"{label}._meta.securitySchemes must mirror securitySchemes")
    return name


def check_references(tool_names: set[str]) -> None:
    files = (
        sorted(ROOT.glob("content/skills/**/*.md"))
        + sorted(ROOT.glob("skills/**/*.md"))
        + sorted(ROOT.glob("examples/**/*.md"))
    )
    if not files:
        raise CheckError("no skill or example files found for tool-reference validation")
    for path in files:
        for name in TOOL_TOKEN.findall(path.read_text(encoding="utf-8")):
            if name not in tool_names:
                raise CheckError(f"unknown tool reference {name} in {path.relative_to(ROOT)}")


def main() -> None:
    check_digest()
    assert_public_text(CONTRACT)
    payload = load_json(CONTRACT)
    root = require_object(payload, "contract root")
    if root.get("schemaVersion") != "1.0.0":
        raise CheckError("contract schemaVersion must be 1.0.0")
    authorization = require_object(root.get("authorization"), "contract.authorization")
    if authorization != {"type": "oauth2", "scopes": ["mcp:full"]}:
        raise CheckError("contract.authorization must require mcp:full OAuth2")
    server = require_object(root.get("server"), "contract.server")
    if server.get("name") != "creator-mcp":
        raise CheckError("contract.server.name must be creator-mcp")
    require_text(server.get("version"), "contract.server.version")
    protocol_versions = require_array(root.get("protocolVersions"), "contract.protocolVersions")
    if not protocol_versions or any(not isinstance(version, str) or not version for version in protocol_versions):
        raise CheckError("contract.protocolVersions must be a non-empty string array")
    if len(protocol_versions) != len(set(protocol_versions)):
        raise CheckError("contract.protocolVersions must not contain duplicates")
    transport = require_object(root.get("transport"), "contract.transport")
    if transport.get("type") != "streamable-http" or transport.get("path") != "/mcp":
        raise CheckError("contract.transport must use streamable-http at /mcp")
    catalog = require_object(load_json(ROOT / "catalog" / "plugin.json"), "catalog/plugin.json")
    remote = require_object(catalog.get("remote"), "catalog.remote")
    production_url = require_text(remote.get("productionUrl"), "catalog.remote.productionUrl")
    if transport.get("productionResourceUri") != production_url:
        raise CheckError("contract.transport.productionResourceUri must equal catalog.remote.productionUrl")
    for key, value in transport.items():
        if "staging" in key.lower() or (isinstance(value, str) and "staging" in value.lower()):
            raise CheckError("contract.transport must not contain staging data")
    tools = adapt_tools(payload)
    if not tools:
        raise CheckError("contract must contain at least one tool")
    names = [check_schema(tool, index) for index, tool in enumerate(tools)]
    if len(names) != len(set(names)):
        raise CheckError("contract tool names must be unique")
    if set(names) != EXPECTED_TOOLS:
        missing = sorted(EXPECTED_TOOLS - set(names))
        unknown = sorted(set(names) - EXPECTED_TOOLS)
        raise CheckError(f"contract tool set differs: missing={missing} unknown={unknown}")
    graphql = next((tool for tool in tools if isinstance(tool, dict) and tool.get("name") == "lf_graphql"), None)
    if graphql is None:
        raise CheckError("contract must include lf_graphql")
    annotations = require_object(graphql.get("annotations"), "lf_graphql.annotations")
    if (
        annotations.get("readOnlyHint") is not False
        or annotations.get("destructiveHint") is not True
        or annotations.get("openWorldHint") is not True
    ):
        raise CheckError("lf_graphql annotations must be explicit: readOnlyHint=false, destructiveHint=true, openWorldHint=true")
    check_references(set(names))
    print(f"Contract check passed for {len(names)} tool(s).")


if __name__ == "__main__":
    try:
        main()
    except CheckError as error:
        print(f"Contract check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
