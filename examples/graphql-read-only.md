# Read-only GraphQL

Use `lf_graphql` only after the current schema confirms `<Resource>` and `<resource>`.

```json
{
  "operationName": "GetResource",
  "query": "query GetResource($id: ID!) { <resource>(id: $id) { id name } }",
  "variables": { "id": "resource_demo_001" }
}
```

Request only the fields needed for the answer. If `errors` appears with `data`, report the available data as partial and state the failed path.
