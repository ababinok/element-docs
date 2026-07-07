---
name: element-language-code
description: "Write, edit, review, and explain code in the 1C:Enterprise Element language (1C:Элемент, XBSL). Use when Codex needs to create modules, methods, structures, enumerations, exceptions, expressions, control flow, typed declarations, outgoing HTTP clients via Стд::Http, or JSON serialization/deserialization via Стд::Json, or when converting/reviewing code to avoid 1C:Enterprise 8 syntax and follow the bundled full language and standard-library references."
---

# Element Language Code

Use this skill to produce correct 1C:Enterprise Element language code from the bundled specification.

## Required Workflow

1. Read `references/element_language_spec.md` before writing, editing, converting, or reviewing 1C:Element code.
2. Load the specification as one whole file. Do not split, summarize instead of reading, or rely on partial snippets when generating code.
3. Follow the specification over habits from 1C:Enterprise 8 or other languages.
4. Keep generated code focused on the requested module, method, type, or snippet. Do not invent platform APIs or standard-library behavior not present in the user context or other relevant Element references.
5. When the task uses outgoing HTTP requests, REST APIs, URLs, query parameters, headers, request/response bodies, authentication, proxy, timeouts, TLS, or `Стд::Http`, read `references/spec_http_client.md`.
6. When the task uses JSON reading/writing, object serialization, streaming JSON, JSON annotations, settings, or `Стд::Json`, read `references/spec_json_serialization.md`.
7. When the task builds a JSON API client or service that combines HTTP and JSON, read both `references/spec_http_client.md` and `references/spec_json_serialization.md`.
8. When the task depends on Console API behavior, use the `element-console-api` skill separately for API contracts, then write the 1C:Element code here.
9. After creating or editing `.XBSL`/`.xbsl` files, run the bundled analyzer against the changed files or their containing project:

   ```bash
   python3 scripts/xbsl_lint.py PATH...
   ```

10. If the analyzer reports diagnostics, inspect them, fix the code, and run the analyzer again. Repeat this lint-fix loop until the analyzer exits with code `0`, or until the remaining issue is clearly outside the analyzer's supported model and must be reported to the user.
11. For complete generated code snippets that are returned in chat instead of written to a file, validate through stdin before presenting the snippet as ready:

   ```bash
   python3 scripts/xbsl_lint.py - --stdin-name sample.XBSL
   ```

12. If the user asks for an intentionally partial fragment that cannot be linted as valid standalone XBSL without changing its meaning, do not invent a wrapper only to satisfy the analyzer. State that the fragment was not linted because no complete module/source file was available.
13. Treat a clean analyzer run as static validity under `scripts/xbsl_lint.py`, not as proof that platform APIs, runtime behavior, or business logic are correct.

## Reference

- `references/element_language_spec.md` - complete 1C:Element language specification for AI agents. Read the entire file whenever this skill is used.
- `references/xbsl_lint.md` - CLI analyzer usage, exit codes, project-mode behavior, and known validation scope.
- `references/spec_http_client.md` - Element 9.2 outgoing HTTP client reference for `Стд::Http`, `КлиентHttp`, `ЗапросHttp`, `ОтветHttp`, URL/query/header/body handling, auth, proxy, timeouts, TLS, and practical HTTP patterns.
- `references/spec_json_serialization.md` - Element 9.2 JSON reference for `Стд::Json`, object serialization/deserialization, streaming readers/writers, annotations, settings, formats, exceptions, and practical JSON patterns.

## Coding Rules

- Use `.XBSL` module conventions and 1C:Element syntax from the specification.
- Use lowercase language keywords such as `метод`, `статический`, `пер`, `знч`, `если`, `иначе`, `для`, `пока`, `возврат`, `новый`, `структура`, `перечисление`, `исключение`, and `область`.
- Close blocks with a single `;` according to the specification.
- Do not use 1C:Enterprise 8 constructs such as `Процедура`, `Функция`, `КонецЕсли`, `КонецЦикла`, `Тогда`, `ИначеЕсли`, or constructor syntax like `Новый Тип(...)`; use lowercase `новый` for object construction. `Новый` may be a regular identifier when valid by context, such as a method name.
- Use explicit typing and type syntax from the specification, including `?` for `Неопределено` unions.
- Prefer clear, idiomatic examples over pseudo-code when the user asks for implementation.
