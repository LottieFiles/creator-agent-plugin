# GraphQL contract reference

Use `lf_graphql` for LottieFiles GraphQL operations. The public schema fixture is required before publication of schema-specific examples or field names.

Safe request shape:

- Use one operation with an `operationName`.
- Put user and resource values in `variables`.
- Request only required fields.
- Preserve `data` when GraphQL returns both `data` and `errors`.
- Treat `errors` as an incomplete result until the response identifies the failed path.

Schema placeholder notation in this repository uses `<Type>`, `<field>`, and `<mutation>`. It is not an API claim.
