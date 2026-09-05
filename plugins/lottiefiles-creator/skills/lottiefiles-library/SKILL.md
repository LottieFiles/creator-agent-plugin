---
name: lottiefiles-library-account
description: Search or inspect LottieFiles library or account data with lf_graphql. Use when the user asks to find, list, inspect, upload, update, delete, or organize LottieFiles resources.
---

# LottieFiles library and account workflows

Full LottieFiles GraphQL access is intentional. It supports the capabilities that the connected account has. It does not grant extra scopes. Read [the contract reference](../../references/tool-contract.md) before a tool call.

1. Discover the needed schema and capability first. Use only fields that the current public schema confirms.
2. Read before a change. Inspect the target resource and its ownership or current state.
3. Request the minimum fields. Send values as variables. Do not put secrets in a query.
4. Paginate lists. Use the returned cursor and a user-approved limit.
5. Before a mutation or delete, state the target and effect. Require explicit user intent and host confirmation.
6. Inspect the response after a mutation. Handle GraphQL partial errors and report which data is reliable.

Never bypass scopes. Never log tokens or query variables. Do not infer a field or mutation name from a human label.
