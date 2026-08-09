from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace

from PIL import Image

from catlabel.vendors.phomemo.client import PhomemoClient


M02_PRO = {
    "vendor": "phomemo",
    "model_id": "M02_PRO",
    "width_px": 624,
    "width_mm": 53,
    "dpi": 300,
    "media_type": "continuous",
    "protocol_family": "phomemo_m02",
    "default_energy": 6,
    "default_feed": 32,
}


def _black(width: int, height: int = 4) -> Image.Image:
    return Image.new("RGB", (width, height), "black")


class CenterOnPrintWidthTests(unittest.TestCase):
    def test_narrow_image_is_padded_to_the_head_width(self) -> None:
        result = PhomemoClient._center_on_print_width(_black(568), 624)
        self.assertEqual(result.width, 624)
        self.assertEqual(result.height, 4)

    def test_content_is_centered_with_white_padding(self) -> None:
        result = PhomemoClient._center_on_print_width(_black(568), 624).convert("RGB")
        left_pad = (624 - 568) // 2

        self.assertEqual(result.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((left_pad - 1, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((left_pad, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((left_pad + 568 - 1, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((left_pad + 568, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((623, 0)), (255, 255, 255))

    def test_odd_difference_puts_the_extra_dot_on_the_right(self) -> None:
        result = PhomemoClient._center_on_print_width(_black(567), 624).convert("RGB")

        self.assertEqual(result.getpixel((27, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((28, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((594, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((595, 0)), (255, 255, 255))

    def test_image_at_head_width_is_returned_unchanged(self) -> None:
        source = _black(624)
        self.assertIs(PhomemoClient._center_on_print_width(source, 624), source)

    def test_wider_image_is_left_to_the_caller(self) -> None:
        source = _black(700)
        self.assertIs(PhomemoClient._center_on_print_width(source, 624), source)

    def test_grayscale_images_keep_working(self) -> None:
        result = PhomemoClient._center_on_print_width(Image.new("L", (568, 4), 0), 624)
        self.assertEqual(result.width, 624)
        self.assertEqual(result.convert("RGB").getpixel((0, 0)), (255, 255, 255))


class PrintImageAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = PhomemoClient(
            SimpleNamespace(address="C4:B8:04:17:B8:97", name="M02 Pro"),
            dict(M02_PRO),
            None,
            SimpleNamespace(energy=0, feed_lines=0),
        )
        self.printed: list[Image.Image] = []

        async def capture(img, width_bytes, density, dither=True):
            self.printed.append(img)

        self.client._print_m02 = capture

    def test_label_narrower_than_the_head_is_centered_before_printing(self) -> None:
        # A 48 mm design is rendered at 203 dpi, so 384 px, and upscaled to 300 dpi.
        asyncio.run(self.client.print_images([_black(384, 10)]))

        self.assertEqual(len(self.printed), 1)
        self.assertEqual(self.printed[0].width, 624)

        printed = self.printed[0].convert("RGB")
        self.assertEqual(printed.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(printed.getpixel((623, 0)), (255, 255, 255))
        self.assertEqual(printed.getpixel((312, 0)), (0, 0, 0))

    def test_full_width_label_is_not_padded(self) -> None:
        asyncio.run(self.client.print_images([_black(422, 10)]))

        self.assertEqual(self.printed[0].width, 624)
        printed = self.printed[0].convert("RGB")
        self.assertEqual(printed.getpixel((0, 0)), (0, 0, 0))
        self.assertEqual(printed.getpixel((623, 0)), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
