# Errors And Safety

## Common Error Payload

Many error responses use an object like:

```json
{
  "code": 3,
  "status": "INVALID_ARGUMENT",
  "message": "1111 is not a valid UUID.",
  "details": "details"
}
```

Use each selected endpoint's `responses` entry from `python3 scripts/search_console_api.py --slug <slug> --full`; error code meanings are endpoint-specific.

## Common HTTP Handling

- `400`: invalid parameter, malformed body, unsupported state, or validation failure.
- `401`: absent/expired authentication. Refresh token.
- `403`: missing authorization. Do not retry without changing user permissions.
- `404`: unknown identifier or unavailable target.
- `409`: conflict. Inspect endpoint-specific message before retrying.
- `500`: server-side error. Preserve request id/log context if available.

## Destructive Or Sensitive Operations

Require explicit user confirmation before executing a real request for:

- `DELETE` methods.
- Application start/stop/suspend/restore/convert.
- Rights recomputation.
- Project update/reapply/export and assembly upload/delete.
- Dumps, certificates, endpoint changes.
- User deletion, password reset, access-token changes, 2FA changes, account-service settings.
- Space/service/subscriber membership changes.

Before execution, restate method, URL path, target IDs, and request body. Use dry-run output when the user only asks for a command.

## Deprecated Methods

The index marks deprecated methods. Prefer non-deprecated alternatives when available, especially project assembly routes:

- Prefer `/console/api/v2/projects/{ProjectId}/assemblies`.
- Avoid legacy `/versions` routes unless requested.

## Pagination

Some list endpoints use `page`, `size`, and `result`. Check the selected method's parameters before assuming pagination. If the task requires complete retrieval, plan a loop and stop when the returned page is exhausted or page metadata says there are no more results.
