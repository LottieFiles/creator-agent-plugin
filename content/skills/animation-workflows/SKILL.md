---
name: lottiefiles-animation-workflows
description: Create, edit, save, export, or manage an animation document with installed Engine tools. Use when the user asks to build or change an animation, export a file, or check an async Engine job.
---

# Animation workflows

Use `engine_docs` to discover the installed Engine contract. Use `engine_document` to inspect a document, `engine_exec` to make a document change, `engine_export` to export, and `engine_job_status` or `engine_job_result` to inspect async work. Read [the contract reference](../../references/tool-contract.md) before a tool call.

1. Ask for the target document, change, output format, and destination when they are not clear.
2. Inspect the document before you change it. Report the current state that affects the request.
3. Make the smallest requested change. Do not replace unrelated content.
4. Save or export only after the user confirms the destination when the action writes a file or replaces an asset.
5. For an async operation, keep its job identifier. Check its state until it succeeds, fails, or needs user action.
6. Report the document or job identifier, result location, and any warning. Do not expose credentials or private data.

Do not invent tool arguments. Do not assume that an export completed until the job result confirms it.
