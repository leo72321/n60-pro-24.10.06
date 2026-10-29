import json
from pathlib import Path
import shlex
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from render_router_config import parse_config, render_script


SAMPLE = {
    "wlan_name": "My WiFi",
    "wlan_password": "abc$(id)'123",
    "root_password": "root'$(id)",
    "lan_ip_address": "192.168.100.1",
    "pppoe_username": "",
    "pppoe_password": "",
}


class RouterConfigTests(unittest.TestCase):
    def test_valid_config_and_shell_quoting(self):
        values = parse_config(json.dumps(SAMPLE))
        rendered = render_script("#!/bin/sh\n__ROUTER_CONFIG_ASSIGNMENTS__\n", values)
        self.assertIn("wlan_password=" + shlex.quote(SAMPLE["wlan_password"]), rendered)
        self.assertIn("root_password=" + shlex.quote(SAMPLE["root_password"]), rendered)
        result = subprocess.run(["sh", "-n"], input=rendered, text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_full_template_syntax(self):
        template = (Path(__file__).resolve().parents[1] / "templates/uci-defaults/99-router-config.tmpl").read_text()
        rendered = render_script(template, parse_config(json.dumps(SAMPLE)))
        result = subprocess.run(["sh", "-n"], input=rendered, text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_missing_secret(self):
        with self.assertRaisesRegex(ValueError, "Missing ROUTER_CONFIG"):
            parse_config("")

    def test_invalid_json(self):
        with self.assertRaisesRegex(ValueError, "valid JSON"):
            parse_config("{oops}")

    def test_missing_field(self):
        value = dict(SAMPLE)
        del value["root_password"]
        with self.assertRaises(ValueError):
            parse_config(json.dumps(value))

    def test_invalid_wifi_password(self):
        with self.assertRaisesRegex(ValueError, "wlan_password"):
            parse_config(json.dumps({**SAMPLE, "wlan_password": "short"}))

    def test_invalid_lan_ip(self):
        with self.assertRaisesRegex(ValueError, "IPv4"):
            parse_config(json.dumps({**SAMPLE, "lan_ip_address": "192.168.999.1"}))

    def test_half_pppoe(self):
        with self.assertRaisesRegex(ValueError, "PPPoE"):
            parse_config(json.dumps({**SAMPLE, "pppoe_username": "account"}))

    def test_control_character(self):
        with self.assertRaisesRegex(ValueError, "Control characters"):
            parse_config(json.dumps({**SAMPLE, "root_password": "one\ntwo"}))


if __name__ == "__main__":
    unittest.main()
