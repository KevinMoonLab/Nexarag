from shared.rabbit import subscribe_to_queue, ChannelType
from shared.schemas import AddPapersByTitle, ClearGraph
import asyncio
import logging
from .semantic_scholar_api import extract_paper_data
from .kg_builder import create_citation_graph
from db.util import load_kg_db, initialize
from db.commands import clear_graph
from shared.rabbit import publish_message, ChannelType
from shared.schemas import PapersAdded, PaperRef

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_paper_refs(paper_data):
    data = paper_data['papers'][0]['p']
    db_id = data['id']
    paper_id = data['properties']['paperId']
    return PaperRef(paperId=paper_id, paperDbId=db_id)

async def handle_add_papers(message: AddPapersByTitle):
    logger.info(f"Received paper titles: {message}")
    paper_data = extract_paper_data(message.titles)
    loader = load_kg_db()
    with loader() as db:
        data = create_citation_graph(db, paper_data)
    refs = list(map(create_paper_refs, data))
    await publish_message(ChannelType.PAPERS_ADDED, PapersAdded(paperRefs=refs))
    logger.info(f"Added {len(refs)} paper references.")

def handle_clear_graph(message: ClearGraph):
    loader = load_kg_db()
    with loader() as db:
        clear_graph(db)
    logger.info("Graph cleared.")

async def main():
    await asyncio.gather(
        subscribe_to_queue(ChannelType.ADD_PAPER, handle_add_papers, AddPapersByTitle),
        subscribe_to_queue(ChannelType.CLEAR_GRAPH, handle_clear_graph, ClearGraph)
    )

if __name__ == "__main__":
    logger.info("Starting Knowledge Graph worker...")
    logger.info("Initializing Neo4j database...")
    loader = load_kg_db()
    with loader() as db:
        initialize(db)
    logger.info("Subscribing to ADD_PAPER queue...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())