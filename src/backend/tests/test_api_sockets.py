import pytest

from api.sockets import ConnectionManager


class FakeWebSocket:
    def __init__(self):
        self.accepted = False
        self.closed = False
        self.messages = []

    async def accept(self):
        self.accepted = True

    async def send_json(self, data):
        self.messages.append(data)

    def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_connect_accepts_and_tracks_websocket():
    manager = ConnectionManager()
    ws = FakeWebSocket()

    await manager.connect(ws)

    assert ws.accepted is True
    assert ws in manager.active_connections


def test_disconnect_removes_websocket():
    manager = ConnectionManager()
    ws = FakeWebSocket()
    manager.active_connections.add(ws)

    manager.disconnect(ws)

    assert ws not in manager.active_connections


@pytest.mark.asyncio
async def test_broadcast_sends_wrapped_event_to_all_connections():
    manager = ConnectionManager()
    ws1 = FakeWebSocket()
    ws2 = FakeWebSocket()
    manager.active_connections.update({ws1, ws2})

    await manager.broadcast("graph_updated", {"count": 2})

    expected = {"type": "graph_updated", "body": {"count": 2}}
    assert ws1.messages == [expected]
    assert ws2.messages == [expected]


def test_disconnect_all_closes_all_connections():
    manager = ConnectionManager()
    ws1 = FakeWebSocket()
    ws2 = FakeWebSocket()
    manager.active_connections.update({ws1, ws2})

    manager.disconnect_all()

    assert ws1.closed is True
    assert ws2.closed is True
