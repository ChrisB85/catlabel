from __future__ import annotations

from ..family import ProtocolCommandSet, ProtocolFamily, ProtocolSpec
from .base import (
    PrintJobRequest,
    ProtocolBehavior,
    ProtocolDefinition,
    SplitWritePlan,
    split_prefixed_bulk_stream,
)
from .dck import BEHAVIOR as DCK_BEHAVIOR
from .eleph_hprt_esc import BEHAVIOR as ELEPH_HPRT_ESC_BEHAVIOR
from .eleph_tspl import BEHAVIOR as ELEPH_TSPL_BEHAVIOR
from .instaprint_core import BEHAVIOR as INSTAPRINT_CORE_BEHAVIOR
from .funny_lx import BEHAVIOR as FUNNY_LX_BEHAVIOR
from .legacy import BEHAVIOR as LEGACY_BEHAVIOR
from .luck_normal import BEHAVIOR as LUCK_NORMAL_BEHAVIOR
from .luck_normal_a4 import BEHAVIOR as LUCK_NORMAL_A4_BEHAVIOR
from .v5c import BEHAVIOR as V5C_BEHAVIOR
from .v5g import BEHAVIOR as V5G_BEHAVIOR
from .v5x import BEHAVIOR as V5X_BEHAVIOR


def _definition(
    prefix: bytes | None,
    command_set: ProtocolCommandSet,
    behavior: ProtocolBehavior,
) -> ProtocolDefinition:
    return ProtocolDefinition(
        spec=ProtocolSpec(packet_prefix=prefix, command_set=command_set),
        behavior=behavior,
    )


_DEFINITIONS = {
    ProtocolFamily.LEGACY: _definition(
        bytes([0x51, 0x78]), ProtocolCommandSet.LEGACY, LEGACY_BEHAVIOR
    ),
    ProtocolFamily.LEGACY_PREFIXED: _definition(
        bytes([0x12, 0x51, 0x78]), ProtocolCommandSet.LEGACY, LEGACY_BEHAVIOR
    ),
    ProtocolFamily.LUCK_NORMAL: _definition(
        None, ProtocolCommandSet.LUCK_NORMAL, LUCK_NORMAL_BEHAVIOR
    ),
    ProtocolFamily.LUCK_NORMAL_A4: _definition(
        None, ProtocolCommandSet.LUCK_NORMAL, LUCK_NORMAL_A4_BEHAVIOR
    ),
    ProtocolFamily.V5G: _definition(
        bytes([0x51, 0x78]), ProtocolCommandSet.V5G, V5G_BEHAVIOR
    ),
    ProtocolFamily.V5X: _definition(
        bytes([0x22, 0x21]), ProtocolCommandSet.V5X, V5X_BEHAVIOR
    ),
    ProtocolFamily.V5C: _definition(
        bytes([0x56, 0x88]), ProtocolCommandSet.V5C, V5C_BEHAVIOR
    ),
    ProtocolFamily.DCK: _definition(
        bytes([0x55, 0xAA]), ProtocolCommandSet.DCK, DCK_BEHAVIOR
    ),
    ProtocolFamily.ELEPH_HPRT_ESC: _definition(
        None, ProtocolCommandSet.ELEPH_HPRT_ESC, ELEPH_HPRT_ESC_BEHAVIOR
    ),
    ProtocolFamily.ELEPH_TSPL: _definition(
        None, ProtocolCommandSet.ELEPH_TSPL, ELEPH_TSPL_BEHAVIOR
    ),
    ProtocolFamily.INSTAPRINT_CORE: _definition(
        None, ProtocolCommandSet.INSTAPRINT_CORE, INSTAPRINT_CORE_BEHAVIOR
    ),
    ProtocolFamily.FUNNY_LX: _definition(
        None, ProtocolCommandSet.FUNNY_LX, FUNNY_LX_BEHAVIOR
    ),
}


def get_protocol_definition(
    protocol_family: ProtocolFamily | str | None,
) -> ProtocolDefinition:
    family = ProtocolFamily.from_value(protocol_family)
    try:
        return _DEFINITIONS[family]
    except KeyError as exc:
        raise ValueError(f"Unsupported protocol family: {family}") from exc


def get_protocol_behavior(
    protocol_family: ProtocolFamily | str | None,
) -> ProtocolBehavior:
    return get_protocol_definition(protocol_family).behavior


__all__ = [
    "PrintJobRequest",
    "ProtocolBehavior",
    "ProtocolDefinition",
    "SplitWritePlan",
    "get_protocol_behavior",
    "get_protocol_definition",
    "split_prefixed_bulk_stream",
]
