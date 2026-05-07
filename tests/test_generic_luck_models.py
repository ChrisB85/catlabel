from __future__ import annotations

import unittest

from catlabel.protocol import ProtocolFamily
from catlabel.vendors import VendorRegistry
from catlabel.vendors.generic.manifest import GenericManifest
from catlabel.vendors.generic.models import PrinterModelRegistry
from catlabel.vendors.utils import extract_raw_hardware_info


class GenericLuckModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = PrinterModelRegistry.load()

    def assertDetected(self, name: str, model_no: str, family: ProtocolFamily, variant: str | None) -> None:
        match = self.registry.detect_with_origin(name)
        self.assertIsNotNone(match, name)
        self.assertEqual(match.model.model_no, model_no)
        self.assertEqual(match.protocol_family, family)
        self.assertEqual(match.protocol_variant, variant)

    def test_luck_exact_names_do_not_shadow_more_specific_models(self) -> None:
        self.assertDetected("A2", "luck_a2", ProtocolFamily.LUCK_NORMAL, None)
        self.assertDetected("A2H", "luck_a2h", ProtocolFamily.LUCK_NORMAL, None)
        self.assertDetected("PPA2_1234", "luck_a2", ProtocolFamily.LUCK_NORMAL, None)
        self.assertDetected("PPA2H_1234", "luck_a2h", ProtocolFamily.LUCK_NORMAL, None)

    def test_luck_a4_aliases_resolve_to_protocol_variants(self) -> None:
        expected = {
            "APA49H_1234": ("luck_a49h", "a49h"),
            "DP_ITP05_1234": ("luck_a4_compressed_tattoo", "a4_tattoo_64"),
            "TPA46Pro_1234": ("luck_a4_compressed_tattoo_96_dense", "a4_tattoo_64_endline96"),
            "APL86H_1234": ("luck_apl86h", "apl86"),
            "DP_D80_1234": ("luck_d80", "d80"),
            "DYD80H": ("luck_d80h", "d80h"),
            "A80H-HD": ("luck_a80h_way1", "a80h_way1"),
            "LuckP_A41_1234": ("luck_a41_luckp", "luckp_a41"),
        }
        for name, (model_no, variant) in expected.items():
            with self.subTest(name=name):
                self.assertDetected(name, model_no, ProtocolFamily.LUCK_NORMAL_A4, variant)

    def test_qirui_hardware_info_exposes_only_supported_paper_modes(self) -> None:
        match = self.registry.detect_with_origin("QIRUI_Q2_1234")
        self.assertIsNotNone(match)
        raw = extract_raw_hardware_info(match.model)

        self.assertEqual(raw["protocol_family"], "luck_normal")
        self.assertEqual(raw["protocol_variant"], "qirui_q2")
        self.assertEqual([mode["value"] for mode in raw["supported_paper_modes"]], ["plain", "tag"])

    def test_unimplemented_luck_names_are_not_claimed(self) -> None:
        for name in ("A49H", "D80H", "PPA2L_1234", "ITP05N"):
            with self.subTest(name=name):
                self.assertIsNone(self.registry.detect_with_origin(name))

    def test_generic_manifest_reports_paper_modes_for_luck_models(self) -> None:
        manifest = GenericManifest()
        info = manifest.identify_device("APA49H_1234")

        self.assertIsNotNone(info)
        self.assertEqual(info["protocol_family"], "luck_normal_a4")
        self.assertEqual(info["protocol_variant"], "a49h")
        self.assertIn({"value": "tag", "label": "Tag"}, info["supported_paper_modes"])


if __name__ == "__main__":
    unittest.main()
