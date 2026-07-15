from __future__ import annotations

from ..raster import PixelFormat, RasterBuffer, RasterSet


def apply_paper_layout_to_raster_set(
    raster_set: RasterSet,
    *,
    paper_width_pixels: int | None,
    left_padding_pixels: int = 0,
) -> RasterSet:
    """Center narrow rasters unless the protocol applies explicit left padding."""

    if (
        paper_width_pixels is None
        or paper_width_pixels <= raster_set.width
        or left_padding_pixels > 0
    ):
        return raster_set

    left = (paper_width_pixels - raster_set.width) // 2
    right = paper_width_pixels - raster_set.width - left
    return RasterSet(
        rasters={
            pixel_format: _pad_raster(raster, left, right)
            for pixel_format, raster in raster_set.rasters.items()
        }
    )


def _pad_raster(raster: RasterBuffer, left: int, right: int) -> RasterBuffer:
    white = 255 if raster.pixel_format is PixelFormat.GRAY8 else 0
    pixels: list[int] = []
    for row in range(raster.height):
        start = row * raster.width
        pixels.extend([white] * left)
        pixels.extend(raster.pixels[start : start + raster.width])
        pixels.extend([white] * right)
    return RasterBuffer(
        pixels=pixels,
        width=raster.width + left + right,
        pixel_format=raster.pixel_format,
    )


__all__ = ["apply_paper_layout_to_raster_set"]
