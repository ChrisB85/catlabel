from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from PIL import Image

from catlabel.printing.runtime.v5g import V5GRuntimeController
from catlabel.vendors.generic.client import GenericClient
from catlabel.vendors.generic.manifest import GenericManifest
from catlabel.transport.bluetooth.types import DeviceTransport


class _Backend:
    def __init__(self) -> None:
        self.writes: list[tuple[bytes, object]] = []
        self.attached = []
        self.attempts = []

    async def connect_attempts(self, attempts) -> None:
        self.attempts.append(tuple(attempts))

    async def write(self, data: bytes, **kwargs) -> None:
        self.writes.append((data, kwargs.get("runtime_controller")))

    async def attach_runtime_controller(self, controller, timeout: float = 1.0) -> None:
        self.attached.append(controller)


class GenericClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_interactive_families_only_attempt_capable_transport(self) -> None:
        profile = SimpleNamespace(speed=None, energy=None, feed_lines=0, paper_mode=None)
        settings = SimpleNamespace(speed=0, energy=0, feed_lines=0)
        cases = (
            ("LX-D01", (DeviceTransport.BLE,)),
            ("PPA2L_1234", (DeviceTransport.CLASSIC,)),
        )
        for name, expected in cases:
            with self.subTest(name=name):
                device = SimpleNamespace(name=name, address="00:11:22:33:44:55")
                hardware = GenericManifest().identify_device(name, device, device.address)
                self.assertIsNotNone(hardware)
                client = GenericClient(device, hardware, profile, settings)
                backend = _Backend()
                client.backend = backend
                self.assertTrue(await client.connect())
                self.assertEqual(
                    tuple(attempt.transport for attempt in backend.attempts[0]),
                    expected,
                )

    async def test_client_prepares_one_runtime_and_sends_both_pages(self) -> None:
        device = SimpleNamespace(name="MX10", address="00:11:22:33:44:55")
        hardware = GenericManifest().identify_device(device.name, device, device.address)
        self.assertIsNotNone(hardware)
        profile = SimpleNamespace(speed=None, energy=None, feed_lines=0, paper_mode=None)
        settings = SimpleNamespace(speed=0, energy=0, feed_lines=0)
        client = GenericClient(device, hardware, profile, settings)
        backend = _Backend()
        client.backend = backend
        image = Image.new("RGB", (hardware["width_px"], 1), "white")

        with patch(
            "catlabel.vendors.generic.client.asyncio.sleep",
            new=AsyncMock(),
        ):
            await client.print_images([image, image.copy()], dither=False)

        self.assertEqual(len(backend.writes), 2)
        self.assertTrue(all(runtime is None for _, runtime in backend.writes))
        self.assertIsInstance(client._runtime_context.runtime_controller, V5GRuntimeController)
        self.assertGreaterEqual(len(backend.attached), 1)
        self.assertTrue(
            all(controller is client._runtime_context.runtime_controller for controller in backend.attached)
        )


if __name__ == "__main__":
    unittest.main()
