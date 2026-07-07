# System Map

## Project

This repository contains the `element-docs` Codex plugin. Plugin-delivered skills live under `plugins/element-docs/skills/`.

## Skills

- `element-language-code`: writes, edits, reviews, and explains 1C:Enterprise Element/XBSL code. It always uses `references/element_language_spec.md` for language syntax and `scripts/xbsl_lint.py` for static checks. It conditionally loads `references/spec_http_client.md` for `Std::Http`/outgoing HTTP work and `references/spec_json_serialization.md` for `Std::Json`/JSON serialization work.
- `element-console-api`: works with the Element control panel Console API using generated endpoint references and helper scripts.

## Invariants

- Keep plugin changes scoped under `plugins/element-docs/` unless repository-level docs such as this map need updates.
- Keep detailed API/library documentation in `references/` and load it conditionally from `SKILL.md`.
- Do not merge Console API contracts into the language code skill; use `element-console-api` for Console API behavior and `element-language-code` for XBSL code generation.
