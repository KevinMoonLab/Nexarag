import asyncio
import logging
from db.util import load_kg_db
from db.commands import clear_graph
from rabbit import publish_message, subscribe_to_queue, ChannelType
from rabbit.schemas import AddPaperCitations, AddPaperReferences, GraphUpdated, AddPapersById, ClearGraph, ChatMessage, ChatResponse
from db.builder import create_paper_graph, add_citations, add_references
from db.util import neomodel_connect
from db.chat import create_chat_message, update_chat_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_add_papers(message: AddPapersById):
    logger.info(f"Received add paper request: {message}")
    await create_paper_graph(message.paperIds)
    await publish_message(ChannelType.GRAPH_UPDATED, GraphUpdated(nodeIds=message.paperIds))

async def handle_add_references(message: AddPaperReferences):
    logger.info(f"Received add references request: {message}")
    await add_references(message.paperIds)
    await publish_message(ChannelType.GRAPH_UPDATED, GraphUpdated(nodeIds=message.paperIds))

async def handle_add_citations(message: AddPaperCitations):
    logger.info(f"Received add citations request: {message}")
    await add_citations(message.paperIds)
    await publish_message(ChannelType.GRAPH_UPDATED, GraphUpdated(nodeIds=message.paperIds))

async def handle_clear_graph(message: ClearGraph):
    loader = load_kg_db()
    with loader() as db:
        clear_graph(db)
    await publish_message(ChannelType.GRAPH_UPDATED, GraphUpdated(nodeIds=[]))
    logger.info("Graph cleared.")

async def handle_chat_response(message: ChatResponse):
    logger.info(f"Received chat response: {message}")
    await update_chat_response(message)
    await publish_message(ChannelType.CHAT_RESPONSE_CREATED, message)


async def handle_chat_message(message: ChatMessage):
    logger.info(f"Received chat message: {message}")
    await create_chat_message(message)
    await publish_message(ChannelType.CHAT_MESSAGE_CREATED, message)

async def main():
    logger.info("Initializing Neo4j database...")
    result = await neomodel_connect('neo4j')
    if result.success:
        logger.info(result.message)
    else:
        logger.error(result.message)
        exit(1)

    logger.info("Subscribing to RabbitMQ events...")
    await asyncio.gather(
        subscribe_to_queue(ChannelType.ADD_PAPER, handle_add_papers, AddPapersById),
        subscribe_to_queue(ChannelType.ADD_CITATIONS, handle_add_citations, AddPaperCitations),
        subscribe_to_queue(ChannelType.ADD_REFERENCES, handle_add_references, AddPaperReferences),
        subscribe_to_queue(ChannelType.CLEAR_GRAPH, handle_clear_graph, ClearGraph),
        subscribe_to_queue(ChannelType.CHAT_MESSAGE, handle_chat_message, ChatMessage),
        subscribe_to_queue(ChannelType.CHAT_RESPONSE, handle_chat_response, ChatResponse),
    )

if __name__ == "__main__":
    logger.info("Starting Neo4J graph database worker...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())