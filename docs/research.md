# Research and support status

Reviewed 2026-09-05. This document records official sources used for packaging decisions. It does not claim that this package is listed or available in any directory.

## Client support

| Product | Official source | Confirmed capability | Package status |
| --- | --- | --- | --- |
| OpenAI | [OpenAI Apps SDK](https://developers.openai.com/apps-sdk/) | Official OpenAI documentation is the source for ChatGPT app and MCP integration requirements. | Native package support and directory listing require release validation. |
| Claude Code | [MCP documentation](https://code.claude.com/docs/en/mcp) | Supports remote HTTP and local stdio MCP servers. It also supports plugin-provided servers. | Manual MCP connection is supported by the client; this package needs host validation. |
| Grok Build | [MCP servers](https://docs.x.ai/build/features/mcp-servers) | Supports configured MCP servers. | Manual MCP connection is supported by the client; this package needs host validation. |
| ZCode | [Plugin documentation](https://zcode.z.ai/en/docs/plugin) and [MCP documentation](https://zcode.z.ai/en/docs/mcp-services) | Supports plugins and manual MCP servers. | Manual MCP connection is supported by the client; this package needs host validation. |
| Gemini CLI | [MCP server documentation](https://geminicli.com/docs/tools/mcp-server/) and [source repository](https://github.com/google-gemini/gemini-cli) | Supports MCP server configuration. | Manual MCP connection is supported by the client; this package needs host validation. |
| MCP Registry | [MCP Registry](https://registry.modelcontextprotocol.io/) and [MCP specification](https://modelcontextprotocol.io/specification/) | Provides an official registry and protocol reference. | Registration is not complete until an administrator publishes an entry. |

## Integration precedents

Cloudflare documents a broad MCP server that exposes platform capabilities. This is the raw or broad API precedent: [Cloudflare MCP server source](https://github.com/cloudflare/mcp-server-cloudflare) and [Cloudflare MCP documentation](https://developers.cloudflare.com/agents/model-context-protocol/). Linear documents an official curated, read-only MCP integration: [Linear MCP documentation](https://linear.app/docs/mcp). These precedents support a broad GraphQL tool only with strict schema discovery, scope, confirmation, and result-handling controls.

## LottieFiles sources

- Website: [lottiefiles.com](https://lottiefiles.com)
- Support: [help.lottiefiles.com](https://help.lottiefiles.com)
- Privacy: [Privacy Policy](https://lottiefiles.com/page/privacy-policy)
- Terms: [Terms and Conditions](https://lottiefiles.com/page/terms-and-conditions)
- Brand assets: [LottieFiles brand assets](https://lottiefiles.com/brand-assets)

The brand-assets endpoint could not be reliably retrieved during package preparation. No logo binary is included. A brand owner must verify provenance and approve any asset before publication.

The creator MCP production and staging DNS endpoints did not resolve during package preparation. This is an external publication blocker. Do not claim live endpoint availability until an external test verifies it.
