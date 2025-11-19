import os
from aio_pika import connect_robust, Message, ExchangeType, Channel
import logging
from enum import Enum, auto
import json
from pydantic import BaseModel
from typing import Awaitable, Callable, Type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
RABBITMQ_USER = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

class ChannelType(Enum):
    ADD_PAPER = auto()
    ADD_PAPER_BY_TITLE = auto()
    ADD_REFERENCES = auto()
    ADD_CITATIONS = auto()
    GRAPH_UPDATED = auto()
    CLEAR_GRAPH = auto()
    CHAT_MESSAGE = auto()
    CHAT_RESPONSE = auto()
    RESPONSE_COMPLETED = auto()
    CHAT_MESSAGE_CREATED = auto()
    CHAT_RESPONSE_CREATED = auto()
    DOCUMENTS_CREATED = auto()
    DOCUMENT_GRAPH_UPDATED = auto()
    EMBEDDING_PLOT_REQUESTED = auto()
    EMBEDDING_PLOT_CREATED = auto()

def serialize_message(message: BaseModel) -> bytes:
    return message.json().encode("utf-8")

def deserialize_message(data: bytes, model: type[BaseModel]) -> BaseModel:
    return model.parse_raw(data)

def get_rabbitmq_url():
    return f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@nexarag.rabbitmq:5672/"

async def create_connection():
    # Construct the RabbitMQ connection URL
    connection_url = get_rabbitmq_url()
    return await connect_robust(connection_url)

async def check_connection():
    try:
        connection_url = get_rabbitmq_url()
        logger.info(f"Checking RabbitMQ connection at {connection_url}")
        connection = await create_connection()
        await connection.close()
        return True
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
        return False

EXCHANGE_SUFFIX = ".broadcast"


def exchange_name(channel_type: ChannelType) -> str:
    """Fan-out exchange name derived from the enum value."""
    return f"{channel_type.name}{EXCHANGE_SUFFIX}"


async def _get_channel() -> Channel:
    connection = await create_connection()
    return await connection.channel()

async def publish_message(channel_type: ChannelType, message: BaseModel):
    # Get the connection
    connection = await create_connection()
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            exchange_name(channel_type),
            ExchangeType.FANOUT,
            durable=True,
        )
        await exchange.publish(
            Message(body=serialize_message(message)),
            routing_key="",
        )


async def get_publisher(channel_type: ChannelType):
    connection = await create_connection()
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        exchange_name(channel_type),
        ExchangeType.FANOUT,
        durable=True,
    )

    async def _publish(message: BaseModel):
        await exchange.publish(
            Message(body=serialize_message(message)),
            routing_key="",
        )

    return _publish, connection


async def subscribe_to_queue(
    channel_type: ChannelType,
    callback: Callable[[BaseModel], Awaitable[None]],
    model: Type[BaseModel],
    *,
    queue_name: str | None = None,
    durable: bool = False,
) -> None:
    connection = await create_connection()

    async with connection:
        channel = await connection.channel()

        # Declare fan out exchange
        exchange = await channel.declare_exchange(
            exchange_name(channel_type),
            ExchangeType.FANOUT,
            durable=True,
        )

        # Create private queue
        if queue_name is None:
            queue = await channel.declare_queue(exclusive=True)
        else:
            queue = await channel.declare_queue(queue_name, durable=durable)

        # Bind queue
        await queue.bind(exchange)

        # Consume messages
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = deserialize_message(message.body, model)
                    await callback(data)