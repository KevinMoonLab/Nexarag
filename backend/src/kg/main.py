import asyncio
import logging
from rabbit import publish_message, subscribe_to_queue, ChannelType
from rabbit.events import ChatMessage, ChatResponse, ResponseCompleted, DocumentGraphUpdated, GraphUpdated
from kg.graph_embeddings import init_graph, handle_documents_created, create_abstract_embeddings
from kg.rag import ask_llm_kg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_chat_message(message: ChatMessage, cb, complete):
    logger.info(f"Handling chat request: {message}")
    for chunk in ask_llm_kg(message):
        await cb(chunk)
    await complete()

async def handle_graph_update(message: GraphUpdated):
    logger.info(f"Received graph update: {message}")
    create_abstract_embeddings(message.nodeIds)
    logger.info(f"Abstract embeddings created for nodes: {message.nodeIds}")

def callbacks(message: ChatMessage):
    first_response = ChatResponse(message="", chatId=message.chatId, userMessageId=message.messageId)
    make_response = lambda msg: ChatResponse(message=msg, chatId=message.chatId, userMessageId=message.messageId, responseId=first_response.responseId)
    async def async_chat_callback(msg: str):
        await publish_message(ChannelType.CHAT_RESPONSE, make_response(msg))
    async def async_completion_callback():
        await publish_message(ChannelType.RESPONSE_COMPLETED, ResponseCompleted(chatId = message.chatId, responseId = first_response.responseId))
    return (async_chat_callback, async_completion_callback)

async def handle_chat_message(message: ChatMessage):
    logger.info(f"Received chat message: {message}")
    response_callback, completion_callback = callbacks(message)
    await handle_chat_message(message, response_callback, completion_callback)

async def main():
    logger.info("Subscribing to RabbitMQ events...")
    await asyncio.gather(
        subscribe_to_queue(ChannelType.CHAT_MESSAGE_CREATED, handle_chat_message, ChatMessage),
        subscribe_to_queue(ChannelType.DOCUMENT_GRAPH_UPDATED, handle_documents_created, DocumentGraphUpdated),
        subscribe_to_queue(ChannelType.GRAPH_UPDATED, handle_graph_update, GraphUpdated),
    )

if __name__ == "__main__":
    logger.info("Starting Knowledge Graph worker...")
    logger.info("Initializing graph...")
    init_graph()
    logger.info("Graph initialized.")
    logger.info("Starting event loop...")

    # Start the event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())