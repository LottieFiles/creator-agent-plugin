# Create and export an animation

Use `engine_docs` first. It defines the valid arguments for `engine_exec`, `engine_document`, and `engine_export`.

1. Ask for the document purpose, output format, and destination.
2. Call `engine_exec` with the published create action and minimum document content.
3. Call `engine_document` to confirm the created document and capture its returned identifier.
4. State the export target and request confirmation if the export writes or replaces a file.
5. Call `engine_export` with the published export arguments.
6. If it returns a job identifier, follow [the async job example](engine-async-job.md).

Synthetic identifiers, such as `document_demo_001`, show flow only. The published fixture must supply argument names and result fields.
