from __future__ import annotations

import unittest

from catlabel import reporting
from catlabel.devices import BleTransportProfile
from catlabel.transport.bluetooth.adapters.bleak_adapter_endpoint_resolver import (
    _BleWriteEndpointResolver,
)
from catlabel.transport.bluetooth.adapters.bleak_adapter_transport import (
    _BleakTransportSession,
)


class _Characteristic:
    uuid = "0000ffe1-0000-1000-8000-00805f9b34fb"
    properties = ["write-without-response"]
    max_write_without_response_size = 23


class _ImmediateReplyClient:
    def __init__(self, session: _BleakTransportSession, reply: bytes) -> None:
        self.session = session
        self.reply = reply
        self.writes: list[bytes] = []

    async def write_gatt_char(self, char, data, *, response: bool) -> None:
        self.writes.append(bytes(data))
        self.session.handle_notification(self.reply)


class BleTransportSessionTests(unittest.IsolatedAsyncioTestCase):
    def test_write_without_response_reserve_reduces_reported_payload(self) -> None:
        self.assertEqual(
            _BleakTransportSession._effective_mtu_payload(
                _Characteristic(),
                180,
                response=False,
                reserve=5,
            ),
            18,
        )

    async def test_atomic_query_registers_waiter_before_write(self) -> None:
        session = _BleakTransportSession(
            transport_profile=BleTransportProfile(),
            write_resolver=_BleWriteEndpointResolver(reporter=reporting.DUMMY_REPORTER),
            reporter=reporting.DUMMY_REPORTER,
        )
        session.bindings.write_char = _Characteristic()
        session.bindings.write_char_uuid = _Characteristic.uuid
        session.bindings.write_selection_strategy = "preferred_uuid"
        session.bindings.write_response_preference = False
        session.notify_started = True
        client = _ImmediateReplyClient(session, b"reply")
        await session.initialize_connection(client, mtu_size=180, timeout=0.1)

        reply = await session.send_control_packet_wait_notification(
            b"query",
            label="immediate reply",
            match=lambda payload: payload == b"reply",
            timeout=0.1,
        )

        self.assertEqual(reply, b"reply")
        self.assertEqual(client.writes, [b"query"])


if __name__ == "__main__":
    unittest.main()
