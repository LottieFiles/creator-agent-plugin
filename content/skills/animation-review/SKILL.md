---
name: lottiefiles-animation-review
description: Inspect, review, compare, or diagnose an animation result with installed Engine tools. Use when the user asks why an animation differs, fails, renders poorly, or needs a quality review.
---

# Animation review and diagnosis

Use `engine_docs` to discover the installed Engine contract. Use `engine_document` to inspect, `engine_exec` to render or inspect when the contract requires it, and `engine_job_status` or `engine_job_result` for async work. Read [the contract reference](references/tool-contract.md) before a tool call.

1. Inspect the source, result, and reported symptom before you diagnose.
2. Compare the smallest relevant artifact, frame range, or property set.
3. Separate confirmed facts from hypotheses. State the evidence for each finding.
4. Do not change the animation during a review unless the user asks for a fix.
5. If a tool returns an async job, inspect the job result before you report a render or export failure.
6. Recommend the smallest safe next action and identify any missing input.

Do not claim visual correctness from metadata alone. Do not expose private document content in diagnostics.
