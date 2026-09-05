# Paginated GraphQL

Use `lf_graphql` only after the schema confirms `<resources>`, `<cursor>`, and the page type.

```json
{
  "operationName": "ListResources",
  "query": "query ListResources($first: Int!, $after: String) { <resources>(first: $first, after: $after) { nodes { id name } pageInfo { hasNextPage endCursor } } }",
  "variables": { "first": 20, "after": null }
}
```

Use `endCursor` only when `hasNextPage` is true. Stop at the user-approved limit. Do not request all pages by default.
