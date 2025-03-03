import os
from aio_pika import connect_robust, Message
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

async def publish_message(channel_type: ChannelType, message: BaseModel):
    """Publish a message to a specified queue."""
    connection = await create_connection()
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(channel_type.name, durable=True)
        await channel.default_exchange.publish(
            Message(body=serialize_message(message)),
            routing_key=channel_type.name,
        )

async def get_publisher(channel_type: ChannelType):
    """
    Return a reusable publisher function for the specified queue.
    The returned function can be used to publish multiple messages without creating a new connection each time.
    """
    connection = await create_connection()
    queue_name = channel_type.name
    channel = await connection.channel()
    await channel.declare_queue(queue_name, durable=True)
    async def publish_message(message: BaseModel):
        await channel.default_exchange.publish(
            Message(body=serialize_message(message)),
            routing_key=queue_name,
        )

    return publish_message, connection

async def subscribe_to_queue(
    channel_type: ChannelType,
    callback: Callable[[BaseModel], Awaitable[None]],
    model: Type[BaseModel],
):
    queue_name = channel_type.name
    connection = await create_connection()
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    deserialized_message = deserialize_message(message.body, model)
                    await callback(deserialized_message)