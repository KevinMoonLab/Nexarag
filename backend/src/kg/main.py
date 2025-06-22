import asyncio
import logging
from rabbit import publish_message, subscribe_to_queue, ChannelType
from rabbit.events import ChatMessage, ChatResponse, ResponseCompleted, DocumentGraphUpdated, GraphUpdated, EmbeddingPlotCreated
from rabbit.commands import CreateEmbeddingPlot
from kg.embeddings import init_graph, create_document_embeddings, create_abstract_embeddings
from kg.rag import ask_llm_kg_with_conversation
from kg.visualization import create_plot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def ask_kg(message: ChatMessage, cb, complete):
    logger.info(f"Handling chat request: {message}")
    try:
        for chunk in ask_llm_kg_with_conversation(message, message.chatId):
            await cb(chunk)
        await complete()
    except Exception as e:
        logger.error(f"Error in ask_kg: {e}")
        await complete()

async def handle_plot_request(message: CreateEmbeddingPlot):
    logger.info(f"Received plot request: {message}")
    embeddings, labels, paper_ids = create_plot(message.model_id, message.queries, message.color_var, message.labels, message.num_docs, message.num_components)
    plot_evt = EmbeddingPlotCreated.from_numpy(embeddings, labels, paper_ids)
    await publish_message(ChannelType.EMBEDDING_PLOT_CREATED, plot_evt)

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
    response_callback, completion_callback = callbacks(message)
    await ask_kg(message, response_callback, completion_callback)

async def main():
    logger.info("Subscribing to RabbitMQ events...")
    await asyncio.gather(
        subscribe_to_queue(ChannelType.CHAT_MESSAGE_CREATED, handle_chat_message, ChatMessage),
        subscribe_to_queue(ChannelType.DOCUMENT_GRAPH_UPDATED, create_document_embeddings, DocumentGraphUpdated),
        subscribe_to_queue(ChannelType.GRAPH_UPDATED, handle_graph_update, GraphUpdated),
        subscribe_to_queue(ChannelType.EMBEDDING_PLOT_REQUESTED, handle_plot_request, CreateEmbeddingPlot),
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