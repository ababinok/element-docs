#!/usr/bin/env python3
"""Store Element Console API credentials in a local user config file."""

from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path
import shlex
import stat
import sys


DEFAULT_BASE_URL = "https://1cmycloud.com"
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "element-console-api" / "credentials.env"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Save Element Console API ClientId and ClientSecret locally."
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Credentials file path. Default: {DEFAULT_CONFIG_PATH}",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Element Console base URL. Default: {DEFAULT_BASE_URL}",
    )
    return parser.parse_args()


def prompt_value(label: str, *, secret: bool = False) -> str:
    while True:
        value = getpass.getpass(f"{label}: ") if secret else input(f"{label}: ")
        value = value.strip()
        if value:
            return value
        print("Значение не может быть пустым.")


def write_credentials(path: Path, base_url: str, client_id: str, client_secret: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        [
            f"ELEMENT_CONSOLE_BASE_URL={shlex.quote(base_url.strip())}",
            f"ELEMENT_CONSOLE_CLIENT_ID={shlex.quote(client_id)}",
            f"ELEMENT_CONSOLE_CLIENT_SECRET={shlex.quote(client_secret)}",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def main() -> int:
    args = parse_args()
    base_url = args.base_url.strip() or DEFAULT_BASE_URL

    print("Настройка доступа к Element Console API")
    print(f"URL консоли: {base_url}")
    print("Введите ClientId и ClientSecret. Secret не будет отображаться на экране.")

    client_id = prompt_value("ClientId")
    client_secret = prompt_value("ClientSecret", secret=True)
    write_credentials(args.path.expanduser(), base_url, client_id, client_secret)

    print(f"Готово. Доступы сохранены локально: {args.path.expanduser()}")
    print("В следующих запросах Codex сможет использовать их без повторного ввода.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
