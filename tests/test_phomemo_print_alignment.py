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
    "default_feed": 32,
}


def _black(width: int, height: int = 4) -> Image.Image:
    return Image.new("RGB", (width, height), "black")


class CenterOnPrintWidthTests(unittest.TestCase):
    def test_narrow_image_is_padded_to_the_head_width(self) -> None:
        result = PhomemoClient._center_on_print_width(_black(568), 576)
        self.assertEqual(result.width, 576)
        self.assertEqual(result.height, 4)

    def test_content_is_centered_with_white_padding(self) -> None:
        result = PhomemoClient._center_on_print_width(_black(568), 576).convert("RGB")
        left_pad = (576 - 568) // 2

        self.assertEqual(result.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((left_pad - 1, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((left_pad, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((left_pad + 568 - 1, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((left_pad + 568, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((575, 0)), (255, 255, 255))

    def test_odd_difference_puts_the_extra_dot_on_the_right(self) -> None:
        result = PhomemoClient._center_on_print_width(_black(567), 576).convert("RGB")

        self.assertEqual(result.getpixel((3, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((4, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((570, 0)), (0, 0, 0))
        self.assertEqual(result.getpixel((571, 0)), (255, 255, 255))

    def test_image_at_head_width_is_returned_unchanged(self) -> None:
        source = _black(576)
        self.assertIs(PhomemoClient._center_on_print_width(source, 576), source)

    def test_wider_image_is_left_to_the_caller(self) -> None:
        source = _black(700)
        self.assertIs(PhomemoClient._center_on_print_width(source, 576), source)

    def test_grayscale_images_keep_working(self) -> None:
        result = PhomemoClient._center_on_print_width(Image.new("L", (568, 4), 0), 576)
        self.assertEqual(result.width, 576)
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

        async def capture(img, width_bytes, density, feed, dither=True):
            self.printed.append(img)

        self.client._print_m02 = capture

    def test_label_narrower_than_the_head_is_centered_before_printing(self) -> None:
        # The canvas is rendered at the printer's own dpi, so a 48 mm design on a
        # 300 dpi head arrives as 567 px and must keep that size.
        asyncio.run(self.client.print_images([_black(567, 10)]))

        self.assertEqual(len(self.printed), 1)
        self.assertEqual(self.printed[0].width, 576)

        printed = self.printed[0].convert("RGB")
        left_pad = (576 - 567) // 2
        self.assertEqual(printed.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(printed.getpixel((575, 0)), (255, 255, 255))
        self.assertEqual(printed.getpixel((left_pad, 0)), (0, 0, 0))
        self.assertEqual(printed.getpixel((left_pad + 566, 0)), (0, 0, 0))

    def test_a_300_dpi_head_does_not_rescale_the_rendered_canvas(self) -> None:
        asyncio.run(self.client.print_images([_black(567, 10)]))

        printed = self.printed[0].convert("RGB")
        black_columns = [x for x in range(576) if printed.getpixel((x, 0)) == (0, 0, 0)]
        self.assertEqual(len(black_columns), 567)
        self.assertEqual(self.printed[0].height, 10)

    def test_full_width_label_is_not_padded(self) -> None:
        asyncio.run(self.client.print_images([_black(576, 10)]))

        self.assertEqual(self.printed[0].width, 576)
        printed = self.printed[0].convert("RGB")
        self.assertEqual(printed.getpixel((0, 0)), (0, 0, 0))
        self.assertEqual(printed.getpixel((575, 0)), (0, 0, 0))

    def test_label_wider_than_the_head_is_still_scaled_down(self) -> None:
        asyncio.run(self.client.print_images([_black(800, 10)]))

        self.assertEqual(self.printed[0].width, 576)


if __name__ == "__main__":
    unittest.main()
