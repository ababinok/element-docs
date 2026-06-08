---
name: element-console-api
description: "Work with the 1C:Enterprise Element control panel Console API: find endpoints, inspect request/response schemas, prepare authenticated curl/HTTP calls, plan workflows for applications, projects, spaces, users, services, tasks, branches, DBMS types, and handle auth, pagination, errors, and destructive operations using bundled Element 9.2 API references."
---

# Element Console API

Use this skill when the user asks how to work with the API of the 1C:Enterprise Element control panel, asks for a Console API method, wants to build an HTTP/curl request, automate applications/projects/users/spaces/services/tasks, or interpret API request/response schemas.

The bundled reference was generated from the local HTML Docusaurus archive for Element `9.2`. Static HTML endpoint pages contain OpenAPI skeleton blocks; the accurate method data is decoded from `frontMatter.api` payloads in JS chunks.

## Required Workflow

1. Identify the user task and the likely API group.
2. Search the compact endpoint index instead of guessing paths:

```bash
python3 scripts/search_console_api.py "создать приложение"
python3 scripts/search_console_api.py --group "Приложения" --method POST
```

3. For the selected method, load exact request/response details:

```bash
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

## Authentication Rules

Console API calls use two auth modes:

- `POST /console/sys/token` uses Basic auth where username is `ClientId` and password is `ClientSecret`, with form body `grant_type=client_credentials`.
- Other Console API calls use `Authorization: Bearer <id_token>`.

Never store or print secrets. Prefer these environment variables in examples:

```bash
ELEMENT_CONSOLE_BASE_URL="https://example.com"
ELEMENT_CONSOLE_CLIENT_ID="..."
ELEMENT_CONSOLE_CLIENT_SECRET="..."
ELEMENT_CONSOLE_TOKEN="..."
```

If a token is expired and the API returns `401`, request a new token. Documentation says the token is valid for about one hour.

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
python3 scripts/build_console_api_refs.py \
  --source-root /path/to/data/docs/element/9.2
```

After regeneration, inspect `references/coverage.json`. A complete 9.2 reference currently has:

- `consoleApiMethods`: 166
- `schemas`: 87
- `methodsLinkedToGroups`: 166
- `methodsWithResponses`: 166
- `methodsWithSecurity`: 166
