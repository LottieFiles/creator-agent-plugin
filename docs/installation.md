# Install and use

This repository is a source package. It does not prove that a public directory listing or remote MCP endpoint is live. The release manager must publish and validate the package before users can install it from a directory.

## Client matrix

| Client | Native package support | Manual MCP connection | Use after connection |
| --- | --- | --- | --- |
| ChatGPT and Codex | Not confirmed for this package. Use only a released host install path. | Pending a published public MCP endpoint and host support. | Discover the tools, then follow the included skills. |
| Claude Code | Not confirmed for this package. Claude Code supports plugin-provided and manually configured MCP servers. | Confirmed client capability; add the released endpoint or command with Claude Code MCP settings. | Approve the server, authenticate if required, then verify tools. |
| Grok Build | Not confirmed for this package. Grok Build supports plugins and MCP configuration. | Confirmed client capability; add the released endpoint or command with `grok mcp add`. | Run `grok inspect`, then use the discovered tools. |
| ZCode | Not confirmed for this package. ZCode supports plugins that bundle MCP servers. | Confirmed client capability; add the released endpoint or command in Settings -> MCP Servers. | Confirm enabled server and inspect its tools. |
| Gemini CLI | Not confirmed for this package. Gemini CLI supports MCP servers. | Confirmed client capability; add the released endpoint or command with `gemini mcp add` or `settings.json`. | Run `/mcp list` and inspect available tools. |
| Generic MCP client | No native package claim. | Use the client’s streamable HTTP or stdio configuration after the server is published. | Discover capabilities before a tool call. |
| MCP Registry | Not listed at publication time. | Registry registration is an administrator action after release validation. | Install only from the registry entry after it exists. |

## Safe connection procedure

1. Get the endpoint or command from a signed release. Do not use a staging or private address.
2. Add only the required environment variables or OAuth connection. Keep tokens in the client secret store or environment.
3. Connect and inspect the tool list. Confirm that only expected tools appear.
4. Run a read-only example first.
5. For writes or deletes, require explicit user intent and the host confirmation prompt.

If a connection fails, check the release notes and support documentation. Do not disable client security controls to make it work.
