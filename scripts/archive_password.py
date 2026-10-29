#!/usr/bin/env python3
"""Read the archive password from ROUTER_CONFIG (same as router root_password).

This command is for CI use. Capture its stdout into a shell variable;
never print the password in CI logs.
"""
import os
import sys
from render_router_config import parse_config


def get_archive_password(raw: str) -> str:
    return parse_config(raw)["root_password"]


def main() -> int:
    try:
        password = get_archive_password(os.environ.get("ROUTER_CONFIG", ""))
    except ValueError as exc:
        print(f"Invalid ROUTER_CONFIG: {exc}", file=sys.stderr)
        return 1
    sys.stdout.write(password)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
