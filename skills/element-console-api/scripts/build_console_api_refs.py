#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import re
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from bs4 import BeautifulSoup


DOCUSAURUS_METADATA_RE = re.compile(r"JSON\.parse\('((?:\\.|[^\\'])*)'\)")
API_LINK_RE = re.compile(r"/docs/console/([^/#?]+)/?")
METHOD_SLUG_RE = re.compile(r"^(get|post|put|patch|delete)-", re.IGNORECASE)


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = value.replace("\x00", "").replace("\u200b", "")
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_title(value: str | None) -> str:
    return clean_text((value or "").replace("\U0001f4c4", "").replace("\ufe0f", ""))


def parse_json_parse_payload(raw: str) -> dict[str, Any] | None:
    for candidate in (raw, raw.replace("\\'", "'")):
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def load_docusaurus_metadata(source_root: Path) -> dict[str, dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = {}
    js_root = source_root / "assets" / "js"
    for path in sorted(js_root.glob("*.js")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in DOCUSAURUS_METADATA_RE.finditer(text):
            obj = parse_json_parse_payload(match.group(1))
            if not obj or "id" not in obj or "frontMatter" not in obj:
                continue
            obj["_chunk"] = path.name
            metadata[clean_text(str(obj["id"]))] = obj
    return metadata


def decode_openapi_payload(metadata: dict[str, Any]) -> dict[str, Any] | None:
    front_matter = metadata.get("frontMatter")
    if not isinstance(front_matter, dict):
        return None
    payload = front_matter.get("api")
    if not isinstance(payload, str) or not payload:
        return None
    decoded = zlib.decompress(base64.b64decode(payload)).decode("utf-8")
    api = json.loads(decoded)
    return api if isinstance(api, dict) else None


def schema_type(schema: Any) -> str:
    if not isinstance(schema, dict):
        return ""
    if "$ref" in schema:
        return str(schema["$ref"]).rsplit("/", 1)[-1]
    for key, sep in (("oneOf", " | "), ("anyOf", " | "), ("allOf", " & ")):
        if key in schema and isinstance(schema[key], list):
            return sep.join(filter(None, (schema_type(item) for item in schema[key])))
    current = str(schema.get("type") or schema.get("title") or "object")
    if current == "array":
        current = f"array[{schema_type(schema.get('items')) or 'object'}]"
    if schema.get("format"):
        current += f"({schema['format']})"
    if schema.get("enum"):
        current += ": " + ", ".join(str(item) for item in schema["enum"])
    return current


def has_example(value: Any) -> bool:
    if isinstance(value, dict):
        if any(key in value for key in ("example", "examples", "x-examples")):
            return True
        return any(has_example(item) for item in value.values())
    if isinstance(value, list):
        return any(has_example(item) for item in value)
    return False


def media_summary(content: Any) -> list[str]:
    if not isinstance(content, dict):
        return []
    return sorted(str(key) for key in content)


def first_response_schema(api: dict[str, Any]) -> str:
    responses = api.get("responses")
    if not isinstance(responses, dict):
        return ""
    for code in sorted(responses):
        if not str(code).startswith("2"):
            continue
        response = responses[code]
        if not isinstance(response, dict):
            continue
        content = response.get("content")
        if not isinstance(content, dict):
            continue
        for media in content.values():
            if isinstance(media, dict):
                current = schema_type(media.get("schema"))
                if current:
                    return current
    return ""


def endpoint_summary(slug: str, api: dict[str, Any], group_slug: str | None, group_title: str | None) -> dict[str, Any]:
    parameters = api.get("parameters") if isinstance(api.get("parameters"), list) else []
    request_body = api.get("requestBody") if isinstance(api.get("requestBody"), dict) else {}
    responses = api.get("responses") if isinstance(api.get("responses"), dict) else {}
    return {
        "slug": slug,
        "group": group_slug,
        "groupTitle": group_title,
        "title": clean_text(str(api.get("title") or api.get("summary") or "")),
        "description": clean_text(str(api.get("description") or "")),
        "method": clean_text(str(api.get("method") or "")).upper(),
        "path": clean_text(str(api.get("path") or "")),
        "deprecated": bool(api.get("deprecated")),
        "security": api.get("security") if isinstance(api.get("security"), list) else [],
        "parameters": [
            {
                "name": clean_text(str(param.get("name") or "")),
                "in": clean_text(str(param.get("in") or "")),
                "required": bool(param.get("required")),
                "type": schema_type(param.get("schema")),
                "description": clean_text(str(param.get("description") or "")),
            }
            for param in parameters
            if isinstance(param, dict)
        ],
        "requestBody": {
            "required": bool(request_body.get("required")),
            "contentTypes": media_summary(request_body.get("content")),
        },
        "responses": [
            {
                "code": str(code),
                "description": clean_text(str(response.get("description") or "")) if isinstance(response, dict) else "",
                "contentTypes": media_summary(response.get("content")) if isinstance(response, dict) else [],
            }
            for code, response in responses.items()
        ],
        "successResponseSchema": first_response_schema(api),
        "hasExamples": has_example(api),
    }


def extract_groups(console_root: Path, api_by_slug: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    linked: set[str] = set()
    for page in sorted(console_root.glob("*/index.html")):
        slug = page.parent.name
        if slug == "schemas" or METHOD_SLUG_RE.match(slug):
            continue
        soup = BeautifulSoup(page.read_text(encoding="utf-8", errors="replace"), "html.parser")
        article = soup.find("article") or soup
        h1 = article.find("h1")
        title = clean_text(h1.get_text(" ", strip=True) if h1 else slug)
        methods: list[dict[str, str]] = []
        seen: set[str] = set()
        if slug == "команды-api":
            groups.append({"slug": slug, "title": title, "methods": methods})
            continue
        for link in article.find_all("a", href=True):
            match = API_LINK_RE.search(link["href"])
            if not match:
                continue
            target = unquote(match.group(1))
            if target in seen or target == slug or target.startswith("schemas/") or target not in api_by_slug:
                continue
            seen.add(target)
            linked.add(target)
            h2 = link.find("h2")
            link_title = clean_title(h2.get_text(" ", strip=True) if h2 else link.get_text(" ", strip=True))
            methods.append({"slug": target, "title": link_title})
        groups.append({"slug": slug, "title": title, "methods": methods})

    orphan_slugs = sorted(set(api_by_slug) - linked)
    if orphan_slugs:
        groups.append({"slug": "_unlinked", "title": "Unlinked endpoints", "methods": [{"slug": slug, "title": slug} for slug in orphan_slugs]})
    return groups


def extract_schemas(console_root: Path) -> list[dict[str, Any]]:
    schemas: list[dict[str, Any]] = []
    schema_root = console_root / "schemas"
    for page in sorted(schema_root.glob("*/index.html")):
        soup = BeautifulSoup(page.read_text(encoding="utf-8", errors="replace"), "html.parser")
        article = soup.find("article") or soup
        h1 = article.find("h1")
        paragraphs = [clean_text(p.get_text(" ", strip=True)) for p in article.find_all("p")]
        examples = [clean_text(pre.get_text(" ", strip=True)) for pre in article.find_all("pre")]
        schemas.append(
            {
                "slug": page.parent.name,
                "title": clean_text(h1.get_text(" ", strip=True) if h1 else page.parent.name),
                "description": next((p for p in paragraphs if p and not p.startswith("Possible values:")), ""),
                "fields": [p for p in paragraphs if p and not p.startswith("Possible values:")][1:],
                "examples": examples[:2],
            }
        )
    return schemas


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_method_refs(path: Path, api_by_slug: dict[str, dict[str, Any]]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for old in path.glob("*.json"):
        old.unlink()
    for slug, api in sorted(api_by_slug.items()):
        write_json(path / f"{slug}.json", {"slug": slug, "api": api})


def write_api_index_md(path: Path, groups: list[dict[str, Any]], summaries: dict[str, dict[str, Any]]) -> None:
    lines = [
        "# Console API Index",
        "",
        "Generated from the local Docusaurus HTML archive and decoded `frontMatter.api` payloads.",
        "",
    ]
    for group in groups:
        lines.append(f"## {group['title']}")
        lines.append("")
        for item in group["methods"]:
            summary = summaries[item["slug"]]
            deprecated = " DEPRECATED" if summary["deprecated"] else ""
            lines.append(f"- `{summary['method']} {summary['path']}`{deprecated} - {item['title']} (`{item['slug']}`)")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path("data/docs/element/9.2"))
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "references")
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    console_root = source_root / "pages" / "console"
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    metadata = load_docusaurus_metadata(source_root)
    api_by_slug: dict[str, dict[str, Any]] = {}
    for doc_id, item in metadata.items():
        if not doc_id.startswith("console/"):
            continue
        api = decode_openapi_payload(item)
        if api:
            api_by_slug[doc_id.split("/", 1)[1]] = api

    groups = extract_groups(console_root, api_by_slug)
    group_lookup: dict[str, tuple[str, str]] = {}
    for group in groups:
        for method in group["methods"]:
            group_lookup[method["slug"]] = (group["slug"], group["title"])

    summaries = {
        slug: endpoint_summary(slug, api, *(group_lookup.get(slug, (None, None))))
        for slug, api in sorted(api_by_slug.items())
    }
    schemas = extract_schemas(console_root)
    coverage = {
        "sourceRoot": source_root.as_posix(),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "consoleApiMethods": len(api_by_slug),
        "methodReferenceFiles": len(api_by_slug),
        "groups": len(groups),
        "schemas": len(schemas),
        "methodsLinkedToGroups": len(group_lookup),
        "methodsWithParameters": sum(1 for item in summaries.values() if item["parameters"]),
        "methodsWithRequestBody": sum(1 for item in summaries.values() if item["requestBody"]["contentTypes"]),
        "methodsWithResponses": sum(1 for item in summaries.values() if item["responses"]),
        "methodsWithSecurity": sum(1 for item in summaries.values() if item["security"]),
        "methodsWithExamples": sum(1 for item in summaries.values() if item["hasExamples"]),
    }

    write_json(out / "api-index.json", {"coverage": coverage, "groups": groups, "methods": summaries})
    write_method_refs(out / "openapi-methods", api_by_slug)
    write_json(out / "schemas-index.json", {"coverage": coverage, "schemas": schemas})
    write_json(out / "coverage.json", coverage)
    write_api_index_md(out / "api-index.md", groups, summaries)
    print(json.dumps(coverage, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
