import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from archive_key import derive_archive_password


class ArchiveKeyTests(unittest.TestCase):
    def test_order_and_whitespace_do_not_change_key(self):
        a = '{"b":"secret value","a":"wifi"}'
        b = json.dumps({"a": "wifi", "b": "secret value"}, indent=3)
        self.assertEqual(derive_archive_password(a), derive_archive_password(b))

    def test_changing_secret_changes_key(self):
        a = '{"wlan_password":"password-A"}'
        b = '{"wlan_password":"password-B"}'
        self.assertNotEqual(derive_archive_password(a), derive_archive_password(b))

    def test_reject_non_object(self):
        with self.assertRaises(ValueError):
            derive_archive_password("[]")


if __name__ == "__main__":
    unittest.main()
