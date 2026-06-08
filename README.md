# Element Docs

Codex plugin with skills and generated references for working with 1C:Enterprise Element documentation.

## Contents

- `skills/element-console-api/` - Codex skill for the 1C:Enterprise Element control panel Console API.
- `skills/element-console-api/references/` - generated endpoint, schema, auth, safety, and workflow references.
- `skills/element-console-api/scripts/` - helper scripts for searching references, generating references, and making Console API requests without printing secrets.

## Security Notes

Do not commit real Console API credentials or tokens.

The Console API helper reads credentials from environment variables or from a local file outside the repository:

```sh
~/.config/element-console-api/credentials.env
```

Local `.env` files are intentionally ignored.
