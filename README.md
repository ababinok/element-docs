# Element Docs Marketplace

Codex marketplace repository with a plugin for working with 1C:Enterprise Element documentation and code.

## Contents

- `.agents/plugins/marketplace.json` - marketplace manifest for Codex.
- `plugins/element-docs/` - Codex plugin root.
- `plugins/element-docs/skills/element-console-api/` - Codex skill for the 1C:Enterprise Element control panel Console API.
- `plugins/element-docs/skills/element-console-api/references/` - generated endpoint, schema, auth, safety, and workflow references.
- `plugins/element-docs/skills/element-console-api/scripts/` - helper scripts for searching references, generating references, and making Console API requests without printing secrets.
- `plugins/element-docs/skills/element-language-code/` - Codex skill for writing and reviewing 1C:Element language code.
- `plugins/element-docs/skills/element-language-code/references/element_language_spec.md` - complete language specification loaded as one file.

## Installation

Add this repository as a Codex plugin marketplace:

```text
Source: https://github.com/ababinok/element-docs.git
Git ref: main
Sparse paths: leave empty
```

If sparse paths are required, include both marketplace metadata and the plugin directory:

```text
.agents/plugins/marketplace.json
plugins/element-docs
```

After adding the marketplace, install the `element-docs` plugin from it and start a new Codex thread.

## Security Notes

Do not commit real Console API credentials or tokens.

The Console API helper reads credentials from environment variables or from a local file outside the repository:

```sh
~/.config/element-console-api/credentials.env
```

Local `.env` files are intentionally ignored.
