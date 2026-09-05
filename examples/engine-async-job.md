# Async job handling

Use `engine_job_status` with the returned job identifier, for example `job_demo_001`. Check at bounded intervals. Do not submit the export again while the job is pending.

1. If the job is pending or running, report progress and check again.
2. If the job succeeds, call `engine_job_result` and report the output location or artifact identifier.
3. If the job fails, report its stable error code and safe remediation. Do not expose private payloads.
4. If the user asks to stop it, explain the effect and then call `engine_cancel_job` after host confirmation.

Use `engine_docs` to confirm job states and arguments before calling a tool.
