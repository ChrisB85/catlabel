from __future__ import annotations

import os
from typing import Optional

INGRESS_PROXY_HOST = "172.30.32.2"
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1"})


def ingress_only_enabled() -> bool:
    """True when the server must answer only the Supervisor ingress proxy."""
    return bool(os.environ.get("CATLABEL_INGRESS_ONLY"))


def is_allowed_client(host: Optional[str]) -> bool:
    """Add-ons share a network, so anything but the ingress proxy is refused."""
    if not host:
        return False
    return host == INGRESS_PROXY_HOST or host in LOOPBACK_HOSTS
