"""InstaPrint/CorePrint small-printer command dialect."""

from __future__ import annotations

from ...raster import PixelFormat
from ..plan import ProtocolPlan
from ..types import ImageEncoding, ImagePipelineConfig, PaperMode
from .base import PrintJobRequest, ProtocolBehavior
from .bitmap import build_gs_v0_blocks

_INIT = b"\x1b\x40"
_DENSITY_PREFIX = b"\x1d\x49\xf0"
_FEED_AFTER_PRINT = b"\x0a\x0a\x0a\x0a"
_DEFAULT_DENSITY = 15


def build_job(request: PrintJobRequest) -> ProtocolPlan:
    variant = request.protocol_variant or "ctp500"
    if variant != "ctp500":
        raise ValueError(f"Unsupported InstaPrint Core protocol variant: {variant!r}")
    raster = request.require_raster(PixelFormat.BW1)
    raster.validate()
    payload = (
        _INIT
        + _density_command(request.density)
        + build_gs_v0_blocks(
            raster,
            max_lines_per_block=0xFFFF,
            lsb_first=False,
            mode=0,
        )
        + _FEED_AFTER_PRINT
    )
    return ProtocolPlan.stream(payload)


def supported_paper_modes(_variant: str | None) -> tuple[PaperMode, ...]:
    return (PaperMode.PLAIN,)


def advance_paper_cmd(_dpi: int, _family, _variant: str | None = None) -> bytes:
    return _FEED_AFTER_PRINT


def retract_paper_cmd(_dpi: int, _family, _variant: str | None = None) -> bytes:
    return b""


def _density_command(density: int | None) -> bytes:
    value = _DEFAULT_DENSITY if density is None else density
    return _DENSITY_PREFIX + bytes([max(0, min(255, int(value)))])


BEHAVIOR = ProtocolBehavior(
    default_image_pipeline=ImagePipelineConfig(
        formats=(PixelFormat.BW1,),
        encoding=ImageEncoding.INSTAPRINT_CORE_RASTER,
    ),
    image_encoding_support={
        ImageEncoding.INSTAPRINT_CORE_RASTER: (PixelFormat.BW1,),
    },
    supported_protocol_variants=("ctp500",),
    supported_paper_modes=(PaperMode.PLAIN,),
    supported_paper_modes_resolver=supported_paper_modes,
    advance_paper_builder=advance_paper_cmd,
    retract_paper_builder=retract_paper_cmd,
    job_builder=build_job,
)
