import asyncio
import logging
from db.util import load_kg_db, initialize
from db.commands import clear_graph
from rabbit import publish_message, subscribe_to_queue, ChannelType
from rabbit.schemas import PapersAdded, AddPapersById, ClearGraph
from kg.builder import create_paper_graph
from db.util import neomodel_connect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_add_papers(message: AddPapersById):
    logger.info(f"Received paper ids: {message}")
    await create_paper_graph(message.paperIds)
    await publish_message(ChannelType.PAPERS_ADDED, PapersAdded(paperIds=message.paperIds))
    logger.info(f"Added {len(message.paperIds)} paper references.")

async def handle_clear_graph(message: ClearGraph):
    loader = load_kg_db()
    with loader() as db:
        clear_graph(db)
    logger.info("Graph cleared.")

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
        subscribe_to_queue(ChannelType.CLEAR_GRAPH, handle_clear_graph, ClearGraph)
    )

if __name__ == "__main__":
    logger.info("Starting Knowledge Graph worker...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())