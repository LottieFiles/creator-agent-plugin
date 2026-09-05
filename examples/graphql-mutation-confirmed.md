# Explicit mutation flow

This flow changes data. Do not call `lf_graphql` until the user explicitly confirms the target and effect and the host asks for confirmation.

1. Read `<resource>(id: $id)` and show the relevant current values.
2. State: “Update resource `resource_demo_001` with the requested name. Continue?”
3. After explicit confirmation, send a minimum mutation:

```json
{
  "operationName": "UpdateResource",
  "query": "mutation UpdateResource($id: ID!, $input: <ResourceInput>!) { <updateResource>(id: $id, input: $input) { id name } }",
  "variables": {
    "id": "resource_demo_001",
    "input": { "name": "Demo animation" }
  }
}
```

4. Inspect the returned resource. If the response includes `errors`, treat the change as uncertain until the target is read again.

All angle-bracket names are schema placeholders, not published LottieFiles fields.
