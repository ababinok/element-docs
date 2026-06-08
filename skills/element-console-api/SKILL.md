---
name: element-console-api
description: "Work with the 1C:Enterprise Element control panel Console API: find endpoints, inspect request/response schemas, prepare authenticated curl/HTTP calls, plan workflows for applications, projects, spaces, users, services, tasks, branches, DBMS types, and handle auth, pagination, errors, and destructive operations using bundled Element 9.2 API references."
---

# Element Console API

Use this skill when the user asks how to work with the API of the 1C:Enterprise Element control panel, asks for a Console API method, wants to build an HTTP/curl request, automate applications/projects/users/spaces/services/tasks, or interpret API request/response schemas.

The bundled reference was generated from the local HTML Docusaurus archive for Element `9.2`. Static HTML endpoint pages contain OpenAPI skeleton blocks; the accurate method data is decoded from `frontMatter.api` payloads in JS chunks.

## Bundled Resource Paths

Treat the directory containing this `SKILL.md` as `SKILL_DIR`. Resolve every bundled script and reference file relative to `SKILL_DIR`, not relative to the user's current project.

Before running bundled scripts, change into the skill directory:

```bash
cd "$SKILL_DIR"
```

If `SKILL_DIR` is not already set, derive it from the loaded skill path shown in Codex context, for example the directory that contains `skills/element-console-api/SKILL.md`.

## Required Workflow

1. Identify the user task and the likely API group.
2. Search the compact endpoint index instead of guessing paths:

```bash
cd "$SKILL_DIR"
python3 scripts/search_console_api.py "создать приложение"
python3 scripts/search_console_api.py --group "Приложения" --method POST
```

3. For the selected method, load exact request/response details:

```bash
cd "$SKILL_DIR"
python3 scripts/search_console_api.py --slug post-console-api-v-2-applications --full
```

4. Read only the relevant reference files:
   - `references/auth.md` for authentication, token use, and environment variables.
   - `references/workflows.md` for common multi-step tasks.
   - `references/errors-and-safety.md` before destructive or state-changing calls.
   - `references/api-index.md` for a human-readable list of all methods by group.
   - `references/api-index.json` for compact structured summaries.
   - `references/openapi-full.json` for exact decoded OpenAPI payloads.
   - `references/schemas-index.json` for schema page summaries.

5. When producing code or curl examples, include the full method, path, required path/query parameters, request content type, and expected success/error responses from the selected OpenAPI entry.

6. For live read-only API calls from Codex, prefer the bundled helper or `curl`; avoid ad hoc Python `urllib` snippets because local macOS Python can fail TLS verification even when the API and credentials are valid.

```bash
cd "$SKILL_DIR"
python3 scripts/element_console_request.py request /console/api/v2/me
python3 scripts/element_console_request.py list-applications
```

## Application Listing Defaults

For `GET /console/api/v2/applications`, add `deleted=false` by default when building or executing requests, examples, scripts, or workflows for listing applications.

Interpret generic requests such as "show my applications", "list applications", or "show all applications" as "all non-deleted applications". Include deleted applications only when the user explicitly asks for deleted/removed applications or asks to include deleted records; in that case use `deleted=true` for only deleted applications, or explain/use the requested broader behavior explicitly.

When executing an application listing, prefer:

```bash
cd "$SKILL_DIR"
python3 scripts/element_console_request.py list-applications
```

The helper uses `deleted=false`, `result=page`, `page=0`, and `size=100` by default and prints `name/status/uri/id`.

## Authentication Rules

Console API calls use two auth modes:

- `POST /console/sys/token` uses Basic auth where username is `ClientId` and password is `ClientSecret`, with form body `grant_type=client_credentials`.
- Other Console API calls use `Authorization: Bearer <id_token>`.

Never store or print secrets. Prefer these environment variables in examples:

```bash
ELEMENT_CONSOLE_BASE_URL="https://1cmycloud.com"
ELEMENT_CONSOLE_CLIENT_ID="..."
ELEMENT_CONSOLE_CLIENT_SECRET="..."
ELEMENT_CONSOLE_TOKEN="..."
```

Default to `https://1cmycloud.com` when the user has not provided another base URL; this is the shared 1C cloud. If the user needs a private/self-hosted Element server, let them override `ELEMENT_CONSOLE_BASE_URL` with their server URL.

If `ELEMENT_CONSOLE_CLIENT_ID` or `ELEMENT_CONSOLE_CLIENT_SECRET` are missing, check for the persistent local credentials file `~/.config/element-console-api/credentials.env` before asking the user to export variables again. Load it only for the current command with:

```bash
set -a; source "$HOME/.config/element-console-api/credentials.env"; set +a
```

If neither environment variables nor the credentials file exist, use the simple setup flow from `references/auth.md`: run `cd "$SKILL_DIR" && python3 scripts/setup_console_credentials.py` yourself when possible. If you cannot run it, tell the user to run that one setup command with the resolved skill path, enter `ClientId`, enter `ClientSecret`, and then retry the API request. Do not show a long multi-line shell script to non-technical users. Do not ask the user to paste secrets into chat unless they explicitly choose that less safe path.

If a token is expired and the API returns `401`, request a new token. Documentation says the token is valid for about one hour.

For live API execution, use `scripts/element_console_request.py` or `curl` first. The helper loads `~/.config/element-console-api/credentials.env`, obtains a token without printing it, uses `requests` with `certifi` when available, and automatically retries through `curl` if Python TLS certificate verification fails.

## Safety Rules

Treat these as sensitive operations:

- Any `DELETE`.
- Application status changes: suspend, restore, start, stop, convert.
- Project/application updates, project export/reapply/update, dumps, certificates, user access, token access, password reset, 2FA changes, rights recomputation.

Before executing a real state-changing request, verify the target base URL, identifiers, method, and body. If the user has not explicitly authorized the specific destructive action, ask for confirmation. For read-only requests, proceed when credentials/base URL are available.

## API Groups

The Console API index contains 13 groups and 166 methods:

- Авторизация и аутентификация
- Профиль пользователя
- Приложения
- Проекты
- Пространства
- Пользователи
- Веб-адреса приложения
- СУБД
- Сервисы
- Задачи
- Групповая разработка. Задачи
- Групповая разработка. Ветки
- Команды API

Deprecated methods are marked in the index. Prefer non-deprecated methods unless the user specifically needs a legacy route.

## Regenerating References

If the local documentation archive changes, regenerate references from the HTML source:

```bash
cd "$SKILL_DIR"
python3 scripts/build_console_api_refs.py \
  --source-root /path/to/data/docs/element/9.2
```

After regeneration, inspect `references/coverage.json`. A complete 9.2 reference currently has:

- `consoleApiMethods`: 166
- `schemas`: 87
- `methodsLinkedToGroups`: 166
- `methodsWithResponses`: 166
- `methodsWithSecurity`: 166
