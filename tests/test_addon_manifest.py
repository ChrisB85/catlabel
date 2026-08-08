from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "catlabel_addon"


def _config_value(key: str) -> str:
    text = (ADDON / "config.yaml").read_text(encoding="utf-8")
    match = re.search(rf"^{key}:\s*\"?([^\"\n]+)\"?\s*$", text, re.MULTILINE)
    assert match, f"{key} missing from config.yaml"
    return match.group(1).strip()


class AddonManifestTests(unittest.TestCase):
    def test_ingress_port_matches_the_port_the_server_listens_on(self) -> None:
        dockerfile = (ADDON / "Dockerfile").read_text(encoding="utf-8")
        match = re.search(r"CATLABEL_PORT=(\d+)", dockerfile)
        self.assertIsNotNone(match, "CATLABEL_PORT missing from Dockerfile")
        self.assertEqual(_config_value("ingress_port"), match.group(1))

    def test_ingress_is_enabled_and_no_port_is_published(self) -> None:
        text = (ADDON / "config.yaml").read_text(encoding="utf-8")
        self.assertEqual(_config_value("ingress"), "true")
        self.assertNotRegex(text, r"(?m)^ports:")

    def test_bluetooth_access_is_declared(self) -> None:
        self.assertEqual(_config_value("host_dbus"), "true")

    def test_container_writes_to_the_persistent_volume(self) -> None:
        dockerfile = (ADDON / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("CATLABEL_DATA_DIR=/data", dockerfile)
        self.assertIn("CATLABEL_NO_BROWSER=1", dockerfile)
        self.assertIn("CATLABEL_INGRESS_ONLY=1", dockerfile)


if __name__ == "__main__":
    unittest.main()
