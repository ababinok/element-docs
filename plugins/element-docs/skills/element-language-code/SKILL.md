---
name: element-language-code
description: "Write, edit, review, and explain code in the 1C:Enterprise Element language (1C:Элемент, XBSL). Use when Codex needs to create modules, methods, structures, enumerations, exceptions, expressions, control flow, or typed declarations in 1C:Element, or when converting/reviewing code to avoid 1C:Enterprise 8 syntax and follow the bundled full language specification."
---

# Element Language Code

Use this skill to produce correct 1C:Enterprise Element language code from the bundled specification.

## Required Workflow

1. Read `references/element_language_spec.md` before writing, editing, converting, or reviewing 1C:Element code.
2. Load the specification as one whole file. Do not split, summarize instead of reading, or rely on partial snippets when generating code.
3. Follow the specification over habits from 1C:Enterprise 8 or other languages.
4. Keep generated code focused on the requested module, method, type, or snippet. Do not invent platform APIs or standard-library behavior not present in the user context or other relevant Element references.
5. When the task depends on Console API behavior, use the `element-console-api` skill separately for API contracts, then write the 1C:Element code here.

## Reference

- `references/element_language_spec.md` - complete 1C:Element language specification for AI agents. Read the entire file whenever this skill is used.

## Coding Rules

- Use `.XBSL` module conventions and 1C:Element syntax from the specification.
- Use lowercase language keywords such as `метод`, `статический`, `пер`, `знч`, `если`, `иначе`, `для`, `пока`, `возврат`, `новый`, `структура`, `перечисление`, `исключение`, and `область`.
- Close blocks with a single `;` according to the specification.
- Do not use 1C:Enterprise 8 constructs such as `Процедура`, `Функция`, `КонецЕсли`, `КонецЦикла`, `Тогда`, `ИначеЕсли`, or `Новый` with an uppercase first letter.
- Use explicit typing and type syntax from the specification, including `?` for `Неопределено` unions.
- Prefer clear, idiomatic examples over pseudo-code when the user asks for implementation.
