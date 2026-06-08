# Console API Authentication

## Environment

Use environment variables in generated examples:

```bash
ELEMENT_CONSOLE_BASE_URL="https://example.com"
ELEMENT_CONSOLE_CLIENT_ID="client-id"
ELEMENT_CONSOLE_CLIENT_SECRET="client-secret"
ELEMENT_CONSOLE_TOKEN="id-token"
```

Do not hardcode, print, commit, or echo real secrets.

## Getting A Token

Endpoint: `POST /console/sys/token`

Auth: HTTP Basic. Username is `ClientId`; password is `ClientSecret`.

Body: `application/x-www-form-urlencoded`

```text
grant_type=client_credentials
```

Curl pattern:

```bash
curl -sS -X POST "$ELEMENT_CONSOLE_BASE_URL/console/sys/token" \
  -u "$ELEMENT_CONSOLE_CLIENT_ID:$ELEMENT_CONSOLE_CLIENT_SECRET" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "grant_type=client_credentials"
```

The success response includes `id_token` and token metadata. Use `id_token` as the bearer token for API calls.

## Calling Console API Methods

Use:

```bash
Authorization: Bearer $ELEMENT_CONSOLE_TOKEN
```

Example:

```bash
curl -sS "$ELEMENT_CONSOLE_BASE_URL/console/api/v2/applications" \
  -H "Authorization: Bearer $ELEMENT_CONSOLE_TOKEN"
```

Token lifetime is documented as about one hour. On `401`, get a fresh token and retry only when retrying is safe for the method.

## Auth Failure Interpretation

- `401`: missing/expired/invalid authentication.
- `403`: authenticated user lacks permission for the requested resource or operation.

For `401`, refresh token. For `403`, do not retry blindly; explain the missing authorization condition.
