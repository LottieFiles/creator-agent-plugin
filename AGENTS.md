# Public package guidance

Use the canonical public content under `content/skills` and `content/assets`. The generator creates platform copies. Do not edit generated copies by hand.

Keep the package public. Do not add internal paths, hostnames, private source, secrets, user data, debug payloads, or proprietary schema.

For GraphQL, discover the published schema first, request minimum fields, use variables, paginate lists, inspect before mutation, and require explicit user intent and host confirmation for writes or deletes. Never bypass scopes or log tokens or variables. Handle partial errors.

Use exact names from the released public tool contract. Verify links and content generation before publishing.
