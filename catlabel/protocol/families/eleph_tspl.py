"""Eleph/ToPrint P1 TSPL-shaped command dialect."""

from __future__ import annotations

from dataclasses import dataclass

from ...raster import PixelFormat, RasterBuffer
from ..plan import ProtocolPlan
from ..types import ImageEncoding, ImagePipelineConfig, PaperMode
from .base import PrintJobRequest, ProtocolBehavior
from .bitmap import pack_bw1_rows, packed_row_width_bytes

_LINE_END = b"\r\n"
_PAPER_TYPE_COMMAND = bytes([0x10, 0xFF, 0x10, 0x03])
_PAPER_CONTINUOUS = 0x01
_PAPER_TAG = 0x02


@dataclass(frozen=True)
class ElephTsplPaperRecipe:
    media_paper_type: int
    gap_mm: float
    height_extra_mm: float = 0.0
    include_speed: bool = True


def build_job(request: PrintJobRequest) -> ProtocolPlan:
    variant = request.protocol_variant or "p1"
    if variant != "p1":
        raise ValueError(f"Unsupported Eleph TSPL protocol variant: {variant!r}")
    raster = request.require_raster(PixelFormat.BW1)
    raster.validate()
    recipes = {
        PaperMode.TAG: ElephTsplPaperRecipe(_PAPER_TAG, 3.0),
        PaperMode.PLAIN: ElephTsplPaperRecipe(
            _PAPER_CONTINUOUS,
            0.0,
            height_extra_mm=5.0,
            include_speed=False,
        ),
    }
    recipe = recipes[request.paper_mode or PaperMode.TAG]
    width_bytes = _width_bytes(raster)
    density = max(0, min(15, int(9 if request.density is None else request.density)))

    payload = bytearray(_PAPER_TYPE_COMMAND + bytes([recipe.media_paper_type]))
    payload += _command(
        "SIZE",
        (
            f"{_px_to_mm(raster.width, request.dev_dpi)} mm,"
            f"{_px_to_mm(raster.height, request.dev_dpi, extra_mm=recipe.height_extra_mm)} mm"
        ),
    )
    payload += _command("DIRECTION", "0,0")
    payload += _command("GAP", f"{_format_mm(recipe.gap_mm)} mm,0 mm")
    payload += _command("SET RIBBON", "OFF")
    payload += _command("DENSITY", str(density))
    payload += _command("REFERENCE", "0,0")
    if recipe.include_speed:
        payload += _command("SPEED", str(request.speed))
    payload += _command("CLS")
    payload += (
        _command_head("BITMAP", f"0,0,{width_bytes},{raster.height},0,")
        + pack_bw1_rows(raster, lsb_first=False)
        + _LINE_END
    )
    payload += _command("PRINT", "1,1")
    return ProtocolPlan.stream(bytes(payload))


def advance_paper_cmd(_dpi: int, _family, _variant: str | None = None) -> bytes:
    return _command("FORMFEED")


def retract_paper_cmd(_dpi: int, _family, _variant: str | None = None) -> bytes:
    return _command("BACKFEED", "40")


def _width_bytes(raster: RasterBuffer) -> int:
    if raster.width % 8 != 0:
        raise ValueError("Eleph TSPL bitmap jobs require width divisible by 8")
    return packed_row_width_bytes(raster.width)


def _px_to_mm(value: int, dpi: int, *, extra_mm: float = 0.0) -> str:
    return _format_mm(float(value) * 25.4 / float(dpi) + extra_mm)


def _format_mm(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".") or "0"


def _command(name: str, value: str | None = None) -> bytes:
    return _command_head(name, value) + _LINE_END


def _command_head(name: str, value: str | None = None) -> bytes:
    if value is None:
        return name.encode("ascii")
    return f"{name} {value}".encode("ascii")


BEHAVIOR = ProtocolBehavior(
    default_image_pipeline=ImagePipelineConfig(
        formats=(PixelFormat.BW1,),
        encoding=ImageEncoding.ELEPH_TSPL_BITMAP,
    ),
    image_encoding_support={
        ImageEncoding.ELEPH_TSPL_BITMAP: (PixelFormat.BW1,),
    },
    supported_protocol_variants=("p1",),
    supported_paper_modes=(PaperMode.TAG, PaperMode.PLAIN),
    advance_paper_builder=advance_paper_cmd,
    retract_paper_builder=retract_paper_cmd,
    job_builder=build_job,
)
