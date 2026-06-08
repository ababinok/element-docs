#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def score_method(method: dict, query: str) -> int:
    if not query:
        return 1
    haystack = " ".join(
        str(method.get(key, ""))
        for key in ("slug", "group", "groupTitle", "title", "description", "method", "path")
    ).lower()
    score = 0
    for part in query.lower().split():
        if part in haystack:
            score += 1
    return score


def main() -> int:
    parser = argparse.ArgumentParser(description="Search 1C:Element Console API reference.")
    parser.add_argument("query", nargs="*", help="Search words, method slug, or path fragment.")
    parser.add_argument("--group", help="Filter by group slug or title fragment.")
    parser.add_argument("--method", help="Filter by HTTP method.")
    parser.add_argument("--slug", help="Print one exact method by slug.")
    parser.add_argument("--full", action="store_true", help="Print full decoded OpenAPI payload for matched methods.")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    index = load_json(REFERENCES / "api-index.json")
    methods = list(index["methods"].values())

    if args.slug:
        methods = [index["methods"][args.slug]] if args.slug in index["methods"] else []
    if args.method:
        methods = [item for item in methods if item["method"].lower() == args.method.lower()]
    if args.group:
        needle = args.group.lower()
        methods = [
            item for item in methods
            if needle in str(item.get("group", "")).lower() or needle in str(item.get("groupTitle", "")).lower()
        ]

    query = " ".join(args.query)
    ranked = [(score_method(item, query), item) for item in methods]
    ranked = [(score, item) for score, item in ranked if score > 0]
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["groupTitle"] or "", pair[1]["path"]))
    selected = [item for _, item in ranked[: args.limit]]

    if args.full:
        full = load_json(REFERENCES / "openapi-full.json")["methods"]
        print(json.dumps({item["slug"]: full[item["slug"]] for item in selected}, ensure_ascii=False, indent=2))
        return 0

    for item in selected:
        deprecated = " DEPRECATED" if item["deprecated"] else ""
        print(f"{item['slug']}")
        print(f"  {item['groupTitle']} | {item['method']} {item['path']}{deprecated}")
        print(f"  {item['description']}")
        if item["parameters"]:
            params = ", ".join(
                f"{p['name']}:{p['in']}{'*' if p['required'] else ''}" for p in item["parameters"]
            )
            print(f"  params: {params}")
        if item["requestBody"]["contentTypes"]:
            print(f"  body: {', '.join(item['requestBody']['contentTypes'])}")
        print(f"  responses: {', '.join(response['code'] for response in item['responses'])}")
        if item["successResponseSchema"]:
            print(f"  success schema: {item['successResponseSchema']}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
