import importlib
import sys
import types

import pytest
from pydantic import BaseModel


class TestMessage(BaseModel):
    value: str


def _load_rabbit_main_with_stubs(monkeypatch):
    aio_pika = types.ModuleType("aio_pika")

    class FakeMessage:
        def __init__(self, body):
            self.body = body

    class FakeExchangeType:
        FANOUT = "fanout"

    async def connect_robust(_url):
        return None

    aio_pika.connect_robust = connect_robust
    aio_pika.Message = FakeMessage
    aio_pika.ExchangeType = FakeExchangeType
    aio_pika.Channel = object

    monkeypatch.setitem(sys.modules, "aio_pika", aio_pika)
    sys.modules.pop("rabbit.main", None)

    return importlib.import_module("rabbit.main")


def test_exchange_name_uses_suffix(monkeypatch):
    rabbit_main = _load_rabbit_main_with_stubs(monkeypatch)

    assert rabbit_main.exchange_name(rabbit_main.ChannelType.ADD_PAPER) == "ADD_PAPER.broadcast"


def test_serialize_and_deserialize_message_round_trip(monkeypatch):
    rabbit_main = _load_rabbit_main_with_stubs(monkeypatch)

    original = TestMessage(value="payload")
    raw = rabbit_main.serialize_message(original)
    restored = rabbit_main.deserialize_message(raw, TestMessage)

    assert isinstance(raw, bytes)
    assert restored == original


def test_get_rabbitmq_url_uses_module_credentials(monkeypatch):
    rabbit_main = _load_rabbit_main_with_stubs(monkeypatch)
    monkeypatch.setattr(rabbit_main, "RABBITMQ_USER", "alice")
    monkeypatch.setattr(rabbit_main, "RABBITMQ_PASSWORD", "secret")

    assert rabbit_main.get_rabbitmq_url() == "amqp://alice:secret@nexarag.rabbitmq:5672/"


@pytest.mark.asyncio
async def test_check_connection_returns_false_on_connection_error(monkeypatch):
    rabbit_main = _load_rabbit_main_with_stubs(monkeypatch)

    async def broken_connection():
        raise RuntimeError("cannot connect")

    monkeypatch.setattr(rabbit_main, "create_connection", broken_connection)

    assert await rabbit_main.check_connection() is False


@pytest.mark.asyncio
async def test_publish_message_declares_fanout_exchange_and_publishes(monkeypatch):
    rabbit_main = _load_rabbit_main_with_stubs(monkeypatch)

    calls = {"declare": [], "publish": []}

    class FakeExchange:
        async def publish(self, message, routing_key):
            calls["publish"].append((message.body, routing_key))

    class FakeChannel:
        async def declare_exchange(self, name, exchange_type, durable):
            calls["declare"].append((name, exchange_type, durable))
            return FakeExchange()

    class FakeConnection:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def channel(self):
            return FakeChannel()

    async def fake_create_connection():
        return FakeConnection()

    monkeypatch.setattr(rabbit_main, "create_connection", fake_create_connection)

    await rabbit_main.publish_message(rabbit_main.ChannelType.CHAT_MESSAGE, TestMessage(value="hello"))

    assert calls["declare"] == [("CHAT_MESSAGE.broadcast", "fanout", True)]
    assert calls["publish"] == [(b'{"value":"hello"}', "")]
