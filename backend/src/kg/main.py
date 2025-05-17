import asyncio
import logging
from rabbit import publish_message, subscribe_to_queue, ChannelType
from rabbit.events import ChatMessage, ChatResponse, ResponseCompleted, DocumentGraphUpdated
from kg.graph_embeddings import init_graph, handle_documents_created
from typing import Callable


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example: Echo response
async def handle_request(message: ChatMessage, cb: Callable, complete: Callable):
    # Your code here
    # Example: Echo response
    await asyncio.sleep(1)
    # await cb("Hi! I'm Nexarag.")
    # await asyncio.sleep(1)
    # await cb(f"Thanks for asking about '{message.message}'!")
    # await asyncio.sleep(1)
    # await cb("I can help you with papers, authors, and more.")
    await cb("""To leverage the structure of a latent space in diffusion models for influencing generation, several approaches can be employed:
        1. **Vector Arithmetic**: Utilize vector operations within the latent space to perform semantic image manipulations, allowing for controlled edits by traversing along specific directions.

        2. **Hierarchical Semantic Features**: Employ encoders to capture structured representations at different levels of abstraction, enhancing conditional generation capabilities and enabling more intricate pattern capturing.

        3. **Guidance Techniques**: Adjust latent variables during the generation process through guidance methods, which can steer the output towards desired attributes or styles.

        4. **Intermediate Bottlenecks as Semantic Spaces**: Identify and use bottleneck layers in the model architecture as a semantic space (e.g., "h-space") for effective image editing by manipulating these intermediate representations.

        These techniques collectively enhance the controllability and quality of generated outputs in diffusion models.
        """)
    await asyncio.sleep(1)
    await complete()

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
    await handle_request(message, response_callback, completion_callback)

async def main():
    logger.info("Subscribing to RabbitMQ events...")
    await asyncio.gather(
        subscribe_to_queue(ChannelType.CHAT_MESSAGE_CREATED, handle_chat_message, ChatMessage),
        subscribe_to_queue(ChannelType.DOCUMENT_GRAPH_UPDATED, handle_documents_created, DocumentGraphUpdated),
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