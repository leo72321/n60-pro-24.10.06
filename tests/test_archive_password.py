import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from archive_password import get_archive_password


SAMPLE = {
    "wlan_name": "Test WiFi",
    "wlan_password": "example-wifi-password",
    "root_password": "my-router-root-password",
    "lan_ip_address": "192.168.100.1",
    "pppoe_username": "",
    "pppoe_password": "",
}


class ArchivePasswordTests(unittest.TestCase):
    def test_uses_exact_root_password(self):
        self.assertEqual(
            get_archive_password(json.dumps(SAMPLE)),
            SAMPLE["root_password"],
        )

    def test_does_not_depend_on_other_settings(self):
        altered = {**SAMPLE, "wlan_name": "Different WiFi"}
        self.assertEqual(
            get_archive_password(json.dumps(altered)),
            SAMPLE["root_password"],
        )

    def test_new_root_password_changes_archive_password(self):
        altered = {**SAMPLE, "root_password": "different-root-password"}
        self.assertEqual(
            get_archive_password(json.dumps(altered)),
            altered["root_password"],
        )

    def test_missing_secret_fails(self):
        with self.assertRaisesRegex(ValueError, "Missing ROUTER_CONFIG"):
            get_archive_password("")

    def test_missing_root_password_fails(self):
        altered = {**SAMPLE, "root_password": ""}
        with self.assertRaisesRegex(ValueError, "root_password"):
            get_archive_password(json.dumps(altered))


if __name__ == "__main__":
    unittest.main()
