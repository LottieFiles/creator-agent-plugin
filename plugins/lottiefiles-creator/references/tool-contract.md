# Pinned public tool contract

Release evidence: `contracts/public-mcp-v1.json` at the distribution or plugin root, schema `1.0.0`, SHA-256 `1effca56b6481b2890d0359845e50e99664004e6b3bf2bcb25d1597a589037e7`. The snapshot records the reviewed release contract. Call `engine_docs` at execution to discover the live contract; live discovery is authoritative.

Every tool requires OAuth 2.0 scope `mcp:full`. A stable tool error has `error.code`, `error.message`, and `error.retryable`.

| Tool | Required input keys | Optional input keys | Success result fields |
| --- | --- | --- | --- |
| `engine_docs` | None | `topic` | `topic`, `bytes` |
| `engine_document` | `action` (`list`, `reset`, or `delete`) | `engineId` | List: `documents[]` with `engineId`, `revision`, `tombstone`. Reset/delete: `ok`, `action`, `engineId`, `revision`, `tombstone`, `durability`; cancelled work returns `ok: false`, `action`, `engineId`, `cancelled: true`. |
| `engine_exec` | `code` | `engineId`, `params`, `timeoutMs` | `result`, `logs`, `engineId`, `revision`, `durability`; may include `warnings`. |
| `engine_export` | None | `durationSec`, `engineId`, `format`, `fps`, `frameTimeSec`, `height`, `tiles`, `width` | `jobId` |
| `engine_job_status` | `jobId` | None | `jobId`, `engineId`, `state`, `progress`, `logs`, `error`, `artifact` |
| `engine_job_result` | `jobId` | None | Success: `jobId`, `state: "succeeded"`, `artifact` with `uri`, `filename`, `mime`, `bytes`, `width`, `height`; other states use the job status fields. |
| `engine_cancel_job` | `jobId` | None | `ok: true`, `jobId`, `state` |
| `request_upload` | `filename`, `mime`, `bytes` | None | `uploadId`, `maxBytes`, `filename`, `mime`, `bytes`, `expiresAtMs` |

## LottieFiles GraphQL

`lf_graphql` requires `query`. It accepts optional `operationName` and `variables`. A GraphQL response preserves `data` and `errors`; a tool failure returns the stable `error` object. When both `data` and `errors` exist, treat the data as partial and report the failed path before any follow-up action.

The pinned annotations are `readOnlyHint: false`, `destructiveHint: true`, `openWorldHint: true`, and `idempotentHint: false`. These describe a mixed-operation tool. They do not grant scopes or bypass host confirmation.
