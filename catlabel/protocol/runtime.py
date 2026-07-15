from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimePrintCapabilities:
    """Capabilities learned from a connected printer at runtime."""

    supports_gray: bool | None = None
    gray_level_override: int | None = None
