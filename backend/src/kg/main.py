import asyncio
import logging
from kg.llm.chat import ask_llm_kg_with_conversation
from kg.llm.visualization import create_plot
from kg.llm.embeddings import create_document_embeddings
from rabbit import publish_message, subscribe_to_queue, ChannelType
from kg.db.util import load_kg_db
from kg.db.commands import clear_graph
from kg.db.builder import create_paper_graph, add_citations, add_references
from kg.db.util import neomodel_connect
from kg.db.chat import create_chat_message, update_chat_response
from kg.db.docs import add_document_refs
from scholar.api import search_papers_by_title
from rabbit.commands import (
    AddPaperCitations, AddPaperReferences,  AddPapersById, ClearGraph, AddPapersByTitle, CreateEmbeddingPlot
)
from rabbit.events import (
    DocumentGraphUpdated, GraphUpdated, ChatMessage, ChatResponse, DocumentsCreated, EmbeddingPlotCreated, ResponseCompleted
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_documents_created(docs: DocumentsCreated):
    logger.info(f"Received documents: {docs}")
    saved_docs = await add_document_refs(docs)
    for result, new_doc in zip(saved_docs, docs.documents):
        if result.success:
            await publish_message(ChannelType.DOCUMENT_GRAPH_UPDATED, DocumentGraphUpdated(doc=new_doc))
            await publish_message(ChannelType.GRAPH_UPDATED, GraphUpdated(nodeIds=[]))
        logger.error(result.message)

async def handle_add_papers(message: AddPapersById):
    logger.info(f"Received add paper request: {message}")
    await create_paper_graph(message.paper_ids)
    await publish_message(ChannelType.GRAPH_UPDATED, GraphUpdated(nodeIds=message.paper_ids))

async def handle_add_papers_by_title(message: AddPapersByTitle):
    logger.info(f"Received add paper request: {message}")
    # Query API for papers
    papers = []
    for paper in message.papers:
        res = search_papers_by_title(paper.title, paper.year)
        if res:
            papers.append(res)

    # Create graph for each paper
    paper_ids = [paper.paperId for paper in papers]
    await create_paper_graph(paper_ids)
    await publish_message(ChannelType.GRAPH_UPDATED, GraphUpdated(nodeIds=paper_ids))

async def handle_add_references(message: AddPaperReferences):
    logger.info(f"Received add references request: {message}")
    references = await add_references(message.paper_ids)
    await publish_message(ChannelType.GRAPH_UPDATED, GraphUpdated(nodeIds=references))

async def handle_add_citations(message: AddPaperCitations):
    logger.info(f"Received add citations request: {message}")
    citations = await add_citations(message.paper_ids)
    await publish_message(ChannelType.GRAPH_UPDATED, GraphUpdated(nodeIds=citations))

async def handle_clear_graph(message: ClearGraph):
    loader = load_kg_db()
    with loader() as db:
        clear_graph(db)
    await publish_message(ChannelType.GRAPH_UPDATED, GraphUpdated(nodeIds=[]))
    logger.info("Graph cleared.")

async def handle_chat_response(message: ChatResponse):
    await update_chat_response(message)
    await publish_message(ChannelType.CHAT_RESPONSE_CREATED, message)

async def handle_chat_message(message: ChatMessage):
    logger.info(f"Database received chat message: {message}")
    await create_chat_message(message)
    await publish_message(ChannelType.CHAT_MESSAGE_CREATED, message)
    logger.info(f"Saved chat message: {message}")

async def ask_kg(message: ChatMessage, cb, complete):
    logger.info(f"Handling chat request: {message}")
    logger.info(f"Message ID: {message.messageId}")
    try:
        for chunk in ask_llm_kg_with_conversation(message, message.chatId):
            await cb(chunk)
        await complete()
    except Exception as e:
        logger.error(f"Error in ask_kg: {e}")
        await cb(f"Error processing request: {e}")
        await complete()

async def handle_plot_request(message: CreateEmbeddingPlot):
    logger.info(f"Received plot request: {message}")
    embeddings, labels, paper_ids = create_plot(message.model_id, message.queries, message.color_var, message.labels, message.num_docs, message.num_components)
    plot_evt = EmbeddingPlotCreated.from_numpy(embeddings, labels, paper_ids)
    await publish_message(ChannelType.EMBEDDING_PLOT_CREATED, plot_evt)

def callbacks(message: ChatMessage):
    first_response = ChatResponse(message="", chatId=message.chatId, userMessageId=message.messageId)
    make_response = lambda msg: ChatResponse(message=msg, chatId=message.chatId, userMessageId=message.messageId, responseId=first_response.responseId)
    async def async_chat_callback(msg: str):
        await publish_message(ChannelType.CHAT_RESPONSE, make_response(msg))
    async def async_completion_callback():
        await publish_message(ChannelType.RESPONSE_COMPLETED, ResponseCompleted(chatId = message.chatId, responseId = first_response.responseId))
    return (async_chat_callback, async_completion_callback)

async def handle_chat_message_created(message: ChatMessage):
    response_callback, completion_callback = callbacks(message)
    await ask_kg(message, response_callback, completion_callback)

async def main():
    logger.info("Initializing Neo4j database...")
    result = await neomodel_connect()
    if result.success:
        logger.info(result.message)
    else:
        logger.error(result.message)
        exit(1)

    logger.info("Subscribing to RabbitMQ events...")
    await asyncio.gather(
        subscribe_to_queue(ChannelType.ADD_PAPER, handle_add_papers, AddPapersById),
        subscribe_to_queue(ChannelType.ADD_PAPER_BY_TITLE, handle_add_papers_by_title, AddPapersByTitle),
        subscribe_to_queue(ChannelType.ADD_CITATIONS, handle_add_citations, AddPaperCitations),
        subscribe_to_queue(ChannelType.ADD_REFERENCES, handle_add_references, AddPaperReferences),
        subscribe_to_queue(ChannelType.CHAT_MESSAGE, handle_chat_message, ChatMessage),
        subscribe_to_queue(ChannelType.CHAT_RESPONSE, handle_chat_response, ChatResponse),
        subscribe_to_queue(ChannelType.CHAT_MESSAGE_CREATED, handle_chat_message_created, ChatMessage),
        subscribe_to_queue(ChannelType.DOCUMENTS_CREATED, handle_documents_created, DocumentsCreated),
        subscribe_to_queue(ChannelType.DOCUMENT_GRAPH_UPDATED, create_document_embeddings, DocumentGraphUpdated),
        subscribe_to_queue(ChannelType.EMBEDDING_PLOT_REQUESTED, handle_plot_request, CreateEmbeddingPlot),
        subscribe_to_queue(ChannelType.CLEAR_GRAPH, handle_clear_graph, ClearGraph),
    )

if __name__ == "__main__":
    logger.info("Starting Neo4J graph database worker...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())