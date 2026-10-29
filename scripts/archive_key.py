#!/usr/bin/env python3
"""Derive firmware archive password from the one ROUTER_CONFIG JSON secret.

Do not print this password in public CI logs. Keep your own exact config
values for decrypting older firmware after changing the GitHub secret.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

SALT = b"netcore-n60-pro-immortalwrt-24.10.6-firmware-archive-v1"
ITERATIONS = 400_000


def derive_archive_password(raw: str) -> str:
    config = json.loads(raw)
    if not isinstance(config, dict):
        raise ValueError("Config must be a JSON object")
    normalized = json.dumps(
        config, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", normalized, SALT, ITERATIONS).hex()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path,
        help="Local private JSON file (instead of ROUTER_CONFIG env)",
    )
    args = parser.parse_args()
    raw = (
        args.config.read_text(encoding="utf-8-sig")
        if args.config else os.environ.get("ROUTER_CONFIG", "")
    )
    if not raw.strip():
        print("Missing ROUTER_CONFIG or --config JSON", file=sys.stderr)
        return 1
    try:
        print(derive_archive_password(raw))
    except (ValueError, OSError):
        print("Invalid router configuration JSON", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
