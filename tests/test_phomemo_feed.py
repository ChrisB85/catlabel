from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace

from PIL import Image

from catlabel.vendors.phomemo.client import PhomemoClient


M02_PRO = {
    "vendor": "phomemo",
    "model_id": "M02_PRO",
    "width_px": 576,
    "width_mm": 48,
    "dpi": 300,
    "media_type": "continuous",
    "protocol_family": "phomemo_m02",
    "default_energy": 6,
}


def _feed_amounts(sent: list[bytes]) -> list[int]:
    return [packet[2] for packet in sent if len(packet) == 3 and packet[:2] == b"\x1b\x4a"]


class PhomemoFeedTests(unittest.TestCase):
    def _client(self, hardware_info: dict, feed_lines) -> PhomemoClient:
        client = PhomemoClient(
            SimpleNamespace(address="C4:B8:04:17:B8:97", name="M02 Pro"),
            hardware_info,
            None,
            SimpleNamespace(energy=0, feed_lines=feed_lines),
        )
        self.sent: list[bytes] = []

        async def capture(data: bytes) -> None:
            self.sent.append(bytes(data))

        client._send = capture
        return client

    def test_m02_feeds_the_configured_amount_instead_of_a_fixed_eight(self) -> None:
        client = self._client(dict(M02_PRO), 200)
        asyncio.run(client.print_images([Image.new("RGB", (576, 8), "white")]))

        self.assertEqual(_feed_amounts(self.sent), [200])

    def test_long_feeds_are_split_across_commands(self) -> None:
        client = self._client(dict(M02_PRO), 600)
        asyncio.run(client.print_images([Image.new("RGB", (576, 8), "white")]))

        amounts = _feed_amounts(self.sent)
        self.assertEqual(amounts, [255, 255, 90])
        self.assertEqual(sum(amounts), 600)

    def test_m_series_also_splits_long_feeds(self) -> None:
        hardware_info = dict(M02_PRO, model_id="M220", protocol_family="phomemo_m", dpi=203, width_px=576)
        client = self._client(hardware_info, 300)
        asyncio.run(client.print_images([Image.new("RGB", (576, 8), "white")]))

        self.assertEqual(_feed_amounts(self.sent), [255, 45])

    def test_zero_feed_falls_back_to_the_hardware_default(self) -> None:
        # Zero means "not configured" here, the same convention the energy setting uses.
        client = self._client(dict(M02_PRO), 0)
        asyncio.run(client.print_images([Image.new("RGB", (576, 8), "white")]))

        self.assertEqual(_feed_amounts(self.sent), [32])

    def test_model_specific_default_feed_is_honoured(self) -> None:
        client = self._client(dict(M02_PRO, default_feed=180), 0)
        asyncio.run(client.print_images([Image.new("RGB", (576, 8), "white")]))

        self.assertEqual(_feed_amounts(self.sent), [180])


if __name__ == "__main__":
    unittest.main()
