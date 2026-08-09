from __future__ import annotations

import unittest

from catlabel.vendors.phomemo.manifest import PhomemoManifest


class PhomemoModelDetectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = PhomemoManifest()

    def _identify(self, advertised_name: str):
        return self.manifest.identify_device(advertised_name)

    def test_m02_pro_is_not_mistaken_for_the_shorter_m02(self) -> None:
        model = self._identify("M02 Pro")
        self.assertEqual(model["model_id"], "M02_PRO")
        self.assertEqual(model["width_px"], 576)
        self.assertEqual(model["dpi"], 300)

    def test_m02_pro_head_width_matches_the_measured_hardware(self) -> None:
        # Measured with a calibration raster: dots past 575 are never printed, so
        # the head is 576 dots wide. 53 mm is the paper width, not the print width.
        model = self._identify("M02 Pro")
        self.assertEqual(model["width_px"], 576)
        self.assertEqual(model["width_mm"], 48)

    def test_m02_pro_without_a_space(self) -> None:
        self.assertEqual(self._identify("M02PRO")["model_id"], "M02_PRO")

    def test_m02_pro_behind_a_vendor_prefix(self) -> None:
        self.assertEqual(self._identify("Phomemo M02 Pro")["model_id"], "M02_PRO")

    def test_plain_m02_variants_still_resolve_to_m02(self) -> None:
        for advertised_name in ("M02", "M02S", "M02X"):
            with self.subTest(advertised_name=advertised_name):
                model = self._identify(advertised_name)
                self.assertEqual(model["model_id"], "M02")
                self.assertEqual(model["width_px"], 384)

    def test_other_models_are_unaffected(self) -> None:
        expected = {
            "P12": "P12",
            "P12 Pro": "P12",
            "A30": "A30",
            "M03": "M03",
            "M04S": "M04S",
            "M110": "M110",
            "M120": "M110",
            "M200": "M200",
            "M250": "M200",
            "M220": "M220",
            "T02": "T02",
            "D30": "D30",
            "Q30": "Q30",
            "PM-241-BT": "PM241",
            "Phomemo M200": "M200",
            "Mr.in_M02S": "M02",
        }
        for advertised_name, model_id in expected.items():
            with self.subTest(advertised_name=advertised_name):
                self.assertEqual(self._identify(advertised_name)["model_id"], model_id)

    def test_unknown_names_are_not_claimed(self) -> None:
        self.assertIsNone(self._identify("Brother QL-800"))
        self.assertIsNone(self._identify(""))


if __name__ == "__main__":
    unittest.main()
