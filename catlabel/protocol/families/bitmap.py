from __future__ import annotations

from ...raster import PixelFormat, RasterBuffer
from ..encoding import pack_line


def packed_row_width_bytes(width: int) -> int:
    if width <= 0:
        raise ValueError("Raster width must be greater than zero")
    return (width + 7) // 8


def pack_bw1_rows(raster: RasterBuffer, *, lsb_first: bool) -> bytes:
    raster.validate()
    if raster.pixel_format != PixelFormat.BW1:
        raise ValueError("BW1 raster packing requires a bw1 raster")
    body = bytearray()
    for row in range(raster.height):
        line = raster.pixels[row * raster.width : (row + 1) * raster.width]
        body += pack_line(list(line), lsb_first=lsb_first)
    return bytes(body)


def build_gs_v0_blocks(
    raster: RasterBuffer,
    *,
    max_lines_per_block: int,
    lsb_first: bool,
    mode: int,
) -> bytes:
    raster.validate()
    if max_lines_per_block <= 0:
        raise ValueError("GS v 0 block height must be positive")
    width_bytes = packed_row_width_bytes(raster.width)
    payload = bytearray()
    line = 0
    while line < raster.height:
        height = min(max_lines_per_block, raster.height - line)
        block = raster.slice_rows(line, height)
        payload += bytes(
            [
                0x1D,
                0x76,
                0x30,
                mode & 0xFF,
                width_bytes & 0xFF,
                (width_bytes >> 8) & 0xFF,
                height & 0xFF,
                (height >> 8) & 0xFF,
            ]
        )
        payload += pack_bw1_rows(block, lsb_first=lsb_first)
        line += height
    return bytes(payload)
