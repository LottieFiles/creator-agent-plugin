# Research and support status

Reviewed 2026-09-06. This document records official sources used for packaging decisions. It does not claim that this package is listed in a universal public directory or that its remote endpoint is live.

## Client support

| Product | Official source | Confirmed capability | Package status |
| --- | --- | --- | --- |
| OpenAI | [OpenAI Plugins](https://developers.openai.com/plugins) | Codex and ChatGPT desktop support repository marketplaces. | This repository supports source installation. Universal public directory approval is pending. `.app.json` stays absent until the OpenAI portal issues a real connector app ID. |
| Claude Code | [MCP documentation](https://code.claude.com/docs/en/mcp) | Supports remote HTTP, local stdio, and plugin-provided MCP servers. | Repository marketplace install is supported. Manual MCP connection needs a verified production endpoint. |
| Grok Build | [Plugins and marketplaces](https://docs.x.ai/build/features/skills-plugins-marketplaces), [CLI reference](https://docs.x.ai/build/cli/reference), and [official marketplace source](https://github.com/xai-org/plugin-marketplace) | Supports plugin marketplaces and MCP configuration. | The Grok adapter uses the current xAI format and official CLI validation. It has no directory listing claim. |
| ZCode | [Plugin documentation](https://zcode.z.ai/en/docs/plugin) and [MCP documentation](https://zcode.z.ai/en/docs/mcp-services) | Supports plugins and manual MCP servers. The documented manifest lookup falls back to a Claude-compatible manifest. | The package uses that fallback. It intentionally has no duplicate ZCode manifest. |
| Gemini CLI | [Extension reference](https://geminicli.com/docs/extensions/reference/) and [source repository](https://github.com/google-gemini/gemini-cli) | Supports extension installation from a Git source and MCP configuration. | The root extension manifest and root skills support source installation. Manual MCP connection needs a verified production endpoint. |
| MCP Registry | [MCP Registry](https://registry.modelcontextprotocol.io/) and [MCP specification](https://modelcontextprotocol.io/specification/) | Provides an official registry and protocol reference. | Registration is not complete until an administrator publishes an entry. |

## Integration precedents

Cloudflare is the broad API precedent. Its official MCP uses compact `search` and `execute` Code Mode tools to expose the full Cloudflare API and can execute GraphQL: [Cloudflare MCP source](https://github.com/cloudflare/mcp). Linear is the curated-object precedent. Its official MCP exposes object tools and a [read-only endpoint](https://linear.app/docs/mcp); Linear’s separate [public API is GraphQL](https://linear.app/developers/graphql). Do not describe Linear MCP as raw GraphQL.

These precedents support a mixed-operation GraphQL tool only when the implementation enforces bounded requests, scopes, server time and size limits, read-before-write checks, confirmation for writes and deletes, pagination, and partial-error handling. Prompt text is guidance; authorization and host controls enforce access.

## LottieFiles sources

- Website: [lottiefiles.com](https://lottiefiles.com)
- Support: [help.lottiefiles.com](https://help.lottiefiles.com)
- Privacy: [Privacy Policy](https://lottiefiles.com/page/privacy-policy)
- Terms: [Terms and Conditions](https://lottiefiles.com/page/terms-and-conditions)
- Brand assets: [LottieFiles brand assets](https://lottiefiles.com/brand-assets)

The brand-assets endpoint could not be reliably retrieved during package preparation. No logo binary is included. A brand owner must verify provenance and approve any asset before publication.

The creator MCP production and staging DNS endpoints did not resolve during package preparation. This is an external publication blocker. Do not claim live endpoint availability until an external test verifies it.
