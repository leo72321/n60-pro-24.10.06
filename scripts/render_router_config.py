#!/usr/bin/env python3
"""Render an OpenWrt first-boot script from one JSON configuration."""

import ipaddress
import json
import os
from pathlib import Path
import shlex
import sys

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates/uci-defaults/99-router-config.tmpl"
OUTPUT = ROOT / "files/etc/uci-defaults/99-router-config"
MARKER = "__ROUTER_CONFIG_ASSIGNMENTS__"
KEYS = (
    "wlan_name",
    "wlan_password",
    "root_password",
    "lan_ip_address",
    "pppoe_username",
    "pppoe_password",
)


def parse_config(raw: str) -> dict[str, str]:
    if not raw or not raw.strip():
        raise ValueError("Missing ROUTER_CONFIG repository secret.")
    try:
        values = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("ROUTER_CONFIG must be valid JSON.") from exc

    if not isinstance(values, dict) or set(values) != set(KEYS):
        raise ValueError("ROUTER_CONFIG must contain exactly six expected fields.")

    for key in KEYS:
        value = values[key]
        if not isinstance(value, str):
            raise ValueError(f"Invalid field type: {key}.")
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError(f"Control characters are not allowed in: {key}.")
        if len(value.encode("utf-8")) > 1024:
            raise ValueError(f"Field too long: {key}.")

    if not values["root_password"]:
        raise ValueError("root_password must not be empty.")
    if not values["wlan_name"]:
        raise ValueError("wlan_name must not be empty.")
    password_bytes = len(values["wlan_password"].encode("utf-8"))
    if not (8 <= password_bytes <= 63):
        raise ValueError("wlan_password must be 8 to 63 UTF-8 bytes.")
    try:
        ipaddress.IPv4Address(values["lan_ip_address"])
    except ipaddress.AddressValueError as exc:
        raise ValueError("Invalid LAN IPv4 address.") from exc
    if bool(values["pppoe_username"]) != bool(values["pppoe_password"]):
        raise ValueError("PPPoE username and password must be both set or both empty.")
    return values


def render_script(template: str, values: dict[str, str]) -> str:
    if template.count(MARKER) != 1:
        raise ValueError("Template must have one assignment marker.")
    assignments = "\n".join(f"{key}={shlex.quote(values[key])}" for key in KEYS)
    return template.replace(MARKER, assignments)


def main() -> int:
    try:
        values = parse_config(os.environ.get("ROUTER_CONFIG", ""))
        rendered = render_script(TEMPLATE.read_text(encoding="utf-8"), values)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered, encoding="utf-8")
        OUTPUT.chmod(0o700)
    except (ValueError, OSError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    print("Private router settings generated without printing content.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
