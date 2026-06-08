#!/usr/bin/env python3
"""Make safe Element Console API calls using local credentials."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any
from urllib.parse import urlencode


DEFAULT_BASE_URL = "https://1cmycloud.com"
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "element-console-api" / "credentials.env"
READ_ONLY_METHODS = {"GET", "HEAD", "OPTIONS"}


class ApiError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call the Element Console API without printing secrets or tokens."
    )
    subparsers = parser.add_subparsers(dest="command")

    request = subparsers.add_parser("request", help="Run a read-only Console API request.")
    request.add_argument("path", help="API path, for example /console/api/v2/me")
    request.add_argument("--method", default="GET", help="HTTP method. Default: GET")
    request.add_argument("--query", action="append", default=[], help="Query pair as name=value")
    request.add_argument("--json-body", help="JSON body for explicitly allowed write calls")
    request.add_argument("--allow-write", action="store_true", help="Allow non-read-only methods")

    list_apps = subparsers.add_parser(
        "list-applications", help="List non-deleted applications as a compact table."
    )
    list_apps.add_argument("--page", type=int, default=0)
    list_apps.add_argument("--size", type=int, default=100)
    list_apps.add_argument(
        "--deleted",
        choices=["false", "true"],
        default="false",
        help="Default: false. Use true only when deleted applications are requested.",
    )
    list_apps.add_argument("--json", action="store_true", help="Print raw JSON response.")

    parser.add_argument("--base-url", help=f"Default: env/config or {DEFAULT_BASE_URL}")
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument(
        "--transport",
        choices=["auto", "requests", "curl"],
        default="auto",
        help="Default: auto. Auto uses requests+certifi when available and falls back to curl on TLS errors.",
    )
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    if not args.command:
        parser.error("choose a command: request or list-applications")
    return args


def unquote_env_value(raw_value: str) -> str:
    parts = shlex.split(raw_value, posix=True)
    return parts[0] if parts else ""


def load_credentials(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    expanded = path.expanduser()
    if expanded.exists():
        for raw_line in expanded.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, raw_value = line.split("=", 1)
            values[key.strip()] = unquote_env_value(raw_value.strip())

    for key in (
        "ELEMENT_CONSOLE_BASE_URL",
        "ELEMENT_CONSOLE_CLIENT_ID",
        "ELEMENT_CONSOLE_CLIENT_SECRET",
    ):
        if os.environ.get(key):
            values[key] = os.environ[key]
    return values


def require_credentials(values: dict[str, str]) -> tuple[str, str, str]:
    base_url = values.get("ELEMENT_CONSOLE_BASE_URL") or DEFAULT_BASE_URL
    client_id = values.get("ELEMENT_CONSOLE_CLIENT_ID")
    client_secret = values.get("ELEMENT_CONSOLE_CLIENT_SECRET")
    missing = [
        name
        for name, value in (
            ("ELEMENT_CONSOLE_CLIENT_ID", client_id),
            ("ELEMENT_CONSOLE_CLIENT_SECRET", client_secret),
        )
        if not value
    ]
    if missing:
        raise ApiError(
            "Missing credentials: "
            + ", ".join(missing)
            + ". Run: python3 scripts/setup_console_credentials.py"
        )
    return base_url.rstrip("/"), client_id, client_secret


def is_tls_error(error: BaseException) -> bool:
    text = str(error).lower()
    return "certificate_verify_failed" in text or "ssl" in text or "tls" in text


def request_with_requests(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: Any = None,
    json_body: Any = None,
    auth: tuple[str, str] | None = None,
    timeout: int,
) -> dict[str, Any]:
    import requests

    verify = True
    try:
        import certifi

        verify = certifi.where()
    except Exception:
        verify = True

    response = requests.request(
        method,
        url,
        headers=headers,
        data=data,
        json=json_body,
        auth=auth,
        timeout=timeout,
        verify=verify,
    )
    if response.status_code >= 400:
        raise ApiError(f"HTTP {response.status_code}: {response.text[:800]}")
    return response.json()


def request_with_curl(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: str | None = None,
    auth: tuple[str, str] | None = None,
    timeout: int,
) -> dict[str, Any]:
    command = [
        "curl",
        "-sS",
        "--max-time",
        str(timeout),
        "-X",
        method,
        "-w",
        "\n%{http_code}",
        url,
    ]
    if auth:
        command.extend(["-u", f"{auth[0]}:{auth[1]}"])
    for name, value in (headers or {}).items():
        command.extend(["-H", f"{name}: {value}"])
    if data is not None:
        command.extend(["--data", data])

    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"curl exited {result.returncode}"
        raise ApiError(message[:1000])
    body, _, status_text = result.stdout.rpartition("\n")
    try:
        status_code = int(status_text)
    except ValueError as error:
        raise ApiError(f"curl response did not include HTTP status: {result.stdout[:800]}") from error
    if status_code >= 400:
        raise ApiError(f"HTTP {status_code}: {body[:800]}")
    try:
        return json.loads(body)
    except json.JSONDecodeError as error:
        raise ApiError(f"Response is not JSON: {result.stdout[:800]}") from error


def http_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: Any = None,
    json_body: Any = None,
    auth: tuple[str, str] | None = None,
    timeout: int,
    transport: str,
) -> dict[str, Any]:
    if transport == "curl":
        curl_data = data if isinstance(data, str) else None
        if json_body is not None:
            curl_data = json.dumps(json_body, ensure_ascii=False)
            headers = {**(headers or {}), "Content-Type": "application/json"}
        return request_with_curl(method, url, headers=headers, data=curl_data, auth=auth, timeout=timeout)

    try:
        return request_with_requests(
            method,
            url,
            headers=headers,
            data=data,
            json_body=json_body,
            auth=auth,
            timeout=timeout,
        )
    except ImportError:
        if transport == "requests":
            raise ApiError("Python package 'requests' is not installed.")
        return http_json(
            method,
            url,
            headers=headers,
            data=data,
            json_body=json_body,
            auth=auth,
            timeout=timeout,
            transport="curl",
        )
    except Exception as error:
        if transport == "auto" and is_tls_error(error):
            print("Python TLS verification failed; retrying with curl.", file=sys.stderr)
            return http_json(
                method,
                url,
                headers=headers,
                data=data,
                json_body=json_body,
                auth=auth,
                timeout=timeout,
                transport="curl",
            )
        raise


def get_token(base_url: str, client_id: str, client_secret: str, args: argparse.Namespace) -> str:
    payload = "grant_type=client_credentials"
    response = http_json(
        "POST",
        f"{base_url}/console/sys/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=payload,
        auth=(client_id, client_secret),
        timeout=args.timeout,
        transport=args.transport,
    )
    token = response.get("id_token")
    if not token:
        raise ApiError("Token response does not contain id_token.")
    return token


def parse_query(pairs: list[str]) -> dict[str, str]:
    query: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ApiError(f"Invalid --query value {pair!r}; expected name=value.")
        key, value = pair.split("=", 1)
        query[key] = value
    return query


def build_url(base_url: str, path: str, query: dict[str, Any] | None = None) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        url = path
    else:
        url = f"{base_url}/{path.lstrip('/')}"
    if query:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{urlencode(query)}"
    return url


def call_api(
    method: str,
    url: str,
    token: str,
    *,
    json_body: Any,
    args: argparse.Namespace,
) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    return http_json(
        method,
        url,
        headers=headers,
        json_body=json_body,
        timeout=args.timeout,
        transport=args.transport,
    )


def extract_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("content", "items", "data", "result"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = extract_items(value)
            if nested:
                return nested
    return []


def first_value(item: dict[str, Any], names: tuple[str, ...]) -> str:
    for name in names:
        value = item.get(name)
        if value is not None:
            return str(value)
    return ""


def print_applications_table(payload: dict[str, Any]) -> None:
    rows = []
    for item in extract_items(payload):
        rows.append(
            [
                first_value(item, ("name", "Name")),
                first_value(item, ("status", "Status", "state", "State")),
                first_value(item, ("uri", "Uri", "url", "Url")),
                first_value(item, ("id", "Id", "applicationId", "ApplicationId")),
            ]
        )
    headers = ["name", "status", "uri", "id"]
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows)) if rows else len(headers[index])
        for index in range(len(headers))
    ]
    print("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(row[index].ljust(widths[index]) for index in range(len(headers))))
    if not rows:
        print("(no applications found)")


def main() -> int:
    args = parse_args()
    values = load_credentials(args.credentials)
    if args.base_url:
        values["ELEMENT_CONSOLE_BASE_URL"] = args.base_url
    base_url, client_id, client_secret = require_credentials(values)
    token = get_token(base_url, client_id, client_secret, args)

    if args.command == "list-applications":
        query = {
            "deleted": args.deleted,
            "result": "page",
            "page": args.page,
            "size": args.size,
        }
        payload = call_api(
            "GET",
            build_url(base_url, "/console/api/v2/applications", query),
            token,
            json_body=None,
            args=args,
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_applications_table(payload)
        return 0

    method = args.method.upper()
    if method not in READ_ONLY_METHODS and not args.allow_write:
        raise ApiError(f"{method} is not read-only. Add --allow-write only after explicit confirmation.")
    json_body = json.loads(args.json_body) if args.json_body else None
    payload = call_api(
        method,
        build_url(base_url, args.path, parse_query(args.query)),
        token,
        json_body=json_body,
        args=args,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ApiError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
