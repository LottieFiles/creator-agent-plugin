# Install and use

This repository supports source installation. It does not prove that a universal public directory listing or production remote endpoint is approved and live. The release manager must complete publication checks before a directory listing or manual remote connection is announced.

## Client matrix

| Client | Native package support | Manual MCP connection | Use after connection |
| --- | --- | --- | --- |
| ChatGPT desktop and Codex | Confirmed repository marketplace support. The universal public directory listing is not approved yet. | Wait for the verified production endpoint and OAuth setup. | Install from source, then discover tools before use. |
| Claude Code | Confirmed repository marketplace support. Claude Code also supports plugin-provided and manual MCP servers. | Add the verified endpoint with Claude Code MCP settings only after publication. | Approve the server, authenticate if required, then verify tools. |
| Grok Build | Adapter support uses the official xAI marketplace format and CLI validation. No directory listing claim. | Use the official Grok marketplace or MCP guidance. Do not use an unpublished endpoint. | Run `grok inspect`, then use the discovered tools. |
| ZCode | ZCode consumes the Claude-compatible manifest. No duplicate ZCode manifest exists. | Add the repository as a marketplace in ZCode, or add a verified MCP server in Settings -> MCP Servers. | Confirm enabled server and inspect its tools. |
| Gemini CLI | Confirmed source extension shape: root `gemini-extension.json` and root `skills` are present. | Add a verified MCP server only when the production endpoint and OAuth are approved. | Run `/mcp list` and inspect available tools. |
| Generic MCP client | No native package claim. | Use the client’s streamable HTTP or stdio configuration after the server is published. | Discover capabilities before a tool call. |
| MCP Registry | Not listed at publication time. | Registry registration is an administrator action after release validation. | Install only from the registry entry after it exists. |

## Source installation

Codex:

```sh
codex plugin marketplace add LottieFiles/creator-agent-plugin
codex plugin add lottiefiles-creator@lottiefiles
```

Claude Code:

```sh
claude plugin marketplace add LottieFiles/creator-agent-plugin
claude plugin install lottiefiles-creator@lottiefiles
```

Gemini CLI:

```sh
gemini extensions install https://github.com/LottieFiles/creator-agent-plugin
```

For Grok Build, follow the official plugin marketplace documentation and validate the adapter with the official CLI. For ZCode, use **Create -> Add marketplace** and select this repository. ZCode documents its fallback to a Claude-compatible plugin manifest, so this package does not include a second ZCode manifest.

`.app.json` is intentionally absent. Do not add it until the OpenAI portal issues a real connector app ID. A placeholder app ID would create an invalid connector claim.

## Safe connection procedure

1. Get the endpoint or command from a signed release. Do not use a staging or private address.
2. Add only the required environment variables or OAuth connection. Keep tokens in the client secret store or environment.
3. Connect and inspect the tool list. Confirm that only expected tools appear.
4. Run a read-only example first.
5. For writes or deletes, require explicit user intent and the host confirmation prompt.

If a connection fails, check the release notes and support documentation. Do not disable client security controls to make it work.
