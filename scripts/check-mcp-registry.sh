#!/usr/bin/env bash
# Validate server.json with the pinned official MCP Registry publisher CLI.
set -euo pipefail

publisher_version="1.8.1"
system_name="$(uname -s)"
machine_name="$(uname -m)"
case "$system_name/$machine_name" in
  Linux/x86_64)
    publisher_asset="mcp-publisher_linux_amd64.tar.gz"
    publisher_sha256="a06c9096dcb9727c13555b6be26c7effa707b01f06a4c561ba7a3635443cf2cc"
    ;;
  Darwin/arm64)
    publisher_asset="mcp-publisher_darwin_arm64.tar.gz"
    publisher_sha256="e45e520892460732a4bdf37255576415d4a53ec171f8b913faf15bb1aef7cb77"
    ;;
  *)
    echo "Unsupported mcp-publisher platform: $system_name/$machine_name" >&2
    exit 1
    ;;
esac

temporary_dir="$(mktemp -d)"
trap 'rm -rf "$temporary_dir"' EXIT
archive_path="$temporary_dir/$publisher_asset"
archive_url="https://github.com/modelcontextprotocol/registry/releases/download/v${publisher_version}/${publisher_asset}"

curl --fail --location --proto '=https' --tlsv1.2 --retry 3 --output "$archive_path" "$archive_url"
if command -v sha256sum >/dev/null 2>&1; then
  printf '%s  %s\n' "$publisher_sha256" "$archive_path" | sha256sum -c -
else
  printf '%s  %s\n' "$publisher_sha256" "$archive_path" | shasum -a 256 -c -
fi
tar -xzf "$archive_path" -C "$temporary_dir" mcp-publisher
"$temporary_dir/mcp-publisher" validate server.json
