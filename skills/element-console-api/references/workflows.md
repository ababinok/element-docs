# Console API Workflows

Use `scripts/search_console_api.py --full --slug <slug>` before implementing any workflow step. This file gives route selection only; exact body fields come from the OpenAPI payload.

## Find Current User

1. Get token with `POST /console/sys/token`.
2. Call `GET /console/api/v2/me`.

## List Applications

Method: `GET /console/api/v2/applications`

Notes:

- Supports pagination parameters such as `page`, `size`, and `result`.
- Can filter deleted applications with `deleted`.

## Create Application

Typical method: `POST /console/api/v2/applications`

Before creating:

1. Identify project/assembly source.
2. Identify default user list and optional connected user lists.
3. Identify space, technology version, DBMS type, locale, timezone, and publication context.
4. Load full method schema and build body from `CreateApplicationRequest`.

Related methods:

- `GET /console/api/v2/projects`
- `GET /console/api/v2/projects/{ProjectId}/assemblies`
- `GET /console/api/v2/user-lists`
- `GET /console/api/v2/spaces`
- `GET /console/api/v2/dbms/types`

## Update Or Deploy Application Project

Related methods:

- `POST /console/api/v2/applications/{ApplicationId}/project/update`
- `POST /console/api/v2/applications/{ApplicationId}/project/reapply`
- `POST /console/api/v2/applications/{ApplicationId}/project/export`
- `GET /console/api/v2/applications/{ApplicationId}/project`

These change application state or export artifacts; verify target IDs before execution.

## Application Status

Related methods:

- `GET /console/api/v2/applications/{ApplicationId}/status`
- `PUT /console/api/v2/applications/{ApplicationId}/status/start`
- `PUT /console/api/v2/applications/{ApplicationId}/status/stop`
- `PUT /console/api/v2/applications/{ApplicationId}/status/suspend`
- `PUT /console/api/v2/applications/{ApplicationId}/status/restore`
- `POST /console/api/v2/applications/{ApplicationId}/status/convert`

Status-changing calls are sensitive. Ask for confirmation before real execution.

## Projects And Assemblies

Preferred methods:

- `GET /console/api/v2/projects`
- `POST /console/api/v2/projects`
- `GET /console/api/v2/projects/{ProjectId}`
- `DELETE /console/api/v2/projects/{ProjectId}`
- `GET /console/api/v2/projects/{ProjectId}/assemblies`
- `POST /console/api/v2/projects/{ProjectId}/assemblies`
- `GET /console/api/v2/projects/{ProjectId}/assemblies/{Version}`
- `DELETE /console/api/v2/projects/{ProjectId}/assemblies/{Version}`

Avoid deprecated `/versions` routes unless the user explicitly needs them.

## Users And User Lists

Common discovery:

- `GET /console/api/v2/user-lists`
- `GET /console/api/v2/user-lists/{UserListId}/users`
- `GET /console/api/v2/applications/{ApplicationId}/users`

Common changes:

- `POST /console/api/v2/user-lists/{UserListId}/users`
- `PUT /console/api/v2/user-lists/{UserListId}/users/{UserId}`
- `DELETE /console/api/v2/user-lists/{UserListId}/users/{UserId}`
- `POST /console/api/v2/applications/{ApplicationId}/users`
- `DELETE /console/api/v2/applications/{ApplicationId}/users/{UserListId}/{UserId}`

User deletion, password reset, token changes, 2FA changes, and app connection changes are sensitive.

## Web Addresses And Certificates

Related methods live in group `Веб-адреса приложения`.

Common sequence:

1. `GET /console/api/v2/applications/{ApplicationId}/endpoints`
2. `GET /console/api/v2/applications/{ApplicationId}/endpoint-validation`
3. `POST /console/api/v2/applications/{ApplicationId}/endpoints`
4. Certificate methods if a certificate is required.

## Spaces

Common methods:

- `GET /console/api/v2/spaces`
- `POST /console/api/v2/spaces`
- `GET /console/api/v2/spaces/{SpaceId}`
- `GET /console/api/v2/spaces/{SpaceId}/applications`
- `GET /console/api/v2/spaces/{SpaceId}/projects`
- `GET /console/api/v2/spaces/{SpaceId}/user-lists`
- `GET /console/api/v2/spaces/{SpaceId}/participants`

## Tasks

There are two task groups:

- `Задачи`: operational group/application/deployment-instance tasks.
- `Групповая разработка. Задачи`: issue-like development tasks.

Search by group before choosing a method.
