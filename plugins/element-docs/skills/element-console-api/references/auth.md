# Console API Authentication

## Environment

Use environment variables in generated examples:

```bash
ELEMENT_CONSOLE_BASE_URL="https://1cmycloud.com"
ELEMENT_CONSOLE_CLIENT_ID="client-id"
ELEMENT_CONSOLE_CLIENT_SECRET="client-secret"
ELEMENT_CONSOLE_TOKEN="id-token"
```

`https://1cmycloud.com` is the default Console API base URL for the shared 1C cloud. Users can override `ELEMENT_CONSOLE_BASE_URL` when they need to connect to their own Element server.

Do not hardcode, print, commit, or echo real secrets.

## Persistent Local Credentials

Plain `export ELEMENT_CONSOLE_CLIENT_ID=...` works only in the current terminal session. To avoid repeating it in every project or every new Codex request, store Console API credentials once in a local file outside repositories:

```text
~/.config/element-console-api/credentials.env
```

Recommended user-facing setup:

```bash
cd "$SKILL_DIR"
python3 scripts/setup_console_credentials.py
```

The script asks for `ClientId` and `ClientSecret`, hides the secret while typing, writes the credentials file, and restricts it to the current OS user.

When working as an agent, run this script yourself from the skill directory. Resolve `SKILL_DIR` to the directory containing `SKILL.md`; do not run bundled scripts from the user's current project. If you cannot run commands and must give a manual instruction, show only one command with the resolved path to `setup_console_credentials.py`.

For a private/self-hosted Element server, pass its base URL:

```bash
cd "$SKILL_DIR"
python3 scripts/setup_console_credentials.py --base-url https://element.example.com
```

For non-technical users, do not show the raw file-writing shell commands by default. Tell them:

1. Run the one setup command above.
2. Enter `ClientId`.
3. Enter `ClientSecret`.
4. Ask Codex to connect to the Element Console API again.

Agents can load the file in future commands without printing secrets:

```bash
set -a
source "$HOME/.config/element-console-api/credentials.env"
set +a
```

Agents should prefer this order:

1. Use already-defined `ELEMENT_CONSOLE_*` environment variables.
2. If missing, source `~/.config/element-console-api/credentials.env` for the current command.
3. If still missing, give the user only the one-line setup command above, not a multi-line bash script.

Never commit this file or copy real values into plugin files.

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

## Live Calls From Codex

Prefer the bundled helper for read-only live API calls:

```bash
cd "$SKILL_DIR"
python3 scripts/element_console_request.py request /console/api/v2/me
python3 scripts/element_console_request.py list-applications
```

The helper:

- loads `~/.config/element-console-api/credentials.env` and current `ELEMENT_CONSOLE_*` variables;
- obtains a token without printing secrets or the token;
- uses `requests` with `certifi` when available;
- falls back to `curl` automatically when Python TLS certificate verification fails;
- blocks non-read-only methods unless `--allow-write` is passed after explicit confirmation.

For direct shell calls, prefer `curl` over Python `urllib` on macOS.

## macOS Python TLS Failure

If Python fails with `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate` while `curl` succeeds, treat it as a local Python certificate-store issue, not as an Element API or credential failure.

Use one of these fixes:

```bash
cd "$SKILL_DIR"
python3 scripts/element_console_request.py list-applications
```

or force curl transport:

```bash
cd "$SKILL_DIR"
python3 scripts/element_console_request.py --transport curl list-applications
```

Do not ask the user to resend credentials for this TLS error.

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
