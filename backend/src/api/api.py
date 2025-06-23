from fastapi import FastAPI, UploadFile, File, Query, WebSocket, WebSocketDisconnect, Depends
from typing import List
from kg.db.util import check_connection as check_neo4j_connection, load_kg_db
from kg.db.queries import search_papers_by_id, get_all_papers, get_graph
from rabbit.commands import (
    AddPaperCitations, AddPaperReferences, AddPapersById, 
    AddPapersByTitle, ClearGraph, PaperTitleWithYear
)
from rabbit.events import (
    GraphUpdated, ChatMessage, ChatResponse, ResponseCompleted, DocumentCreated, 
    DocumentsCreated, EmbeddingPlotCreated
)
from pathlib import Path
from rabbit.commands import CreateEmbeddingPlot
from scholar.api import relevance_search
from scholar.models import Paper
from scholar.util import retry
from rabbit import publish_message, ChannelType, check_connection as check_rabbit_connection, subscribe_to_queue
from .upload import upload_many
from .util import transform_for_cytoscape, transform_bibtex_for_cytoscape
from fastapi.middleware.cors import CORSMiddleware
from .sockets import ConnectionManager
import bibtexparser
from contextlib import asynccontextmanager
import asyncio
import logging
from kg.llm.chat import default_prefix
from .types import BibTexPaper, BibTexRequest
from ollama import Client
from langchain_ollama.llms import OllamaLLM
import os
from fastapi.staticfiles import StaticFiles
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")


######################## Configuration ########################

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

######################## WebSockets ########################

manager = ConnectionManager()
def get_connection_manager():
    return manager

async def handle_update_result(message: GraphUpdated):
    await manager.broadcast("graph_updated", {})

async def handle_chat_response(message: ChatResponse):
    await manager.broadcast("chat_response", message.model_dump())

async def handle_response_completed(message: ResponseCompleted):
    logger.info(f"Response completed: {message.responseId}")
    await manager.broadcast("response_completed", message.model_dump())

async def handle_plot_created(message: EmbeddingPlotCreated):
    await manager.broadcast("plot_created", message.model_dump())

async def subscribe_to_rabbitmq():
    logger.info("Subscribing to RabbitMQ events...")
    await asyncio.gather(
        subscribe_to_queue(ChannelType.GRAPH_UPDATED, handle_update_result, GraphUpdated),
        subscribe_to_queue(ChannelType.CHAT_RESPONSE_CREATED, handle_chat_response, ChatResponse),
        subscribe_to_queue(ChannelType.RESPONSE_COMPLETED, handle_response_completed, ResponseCompleted),
        subscribe_to_queue(ChannelType.EMBEDDING_PLOT_CREATED, handle_plot_created, EmbeddingPlotCreated)
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(subscribe_to_rabbitmq())
    yield
    
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    manager.disconnect_all()

app = FastAPI(title="Nexarag API", description="API for managing the Nexarag knowledge graph", lifespan=lifespan)

app.mount("/documents", StaticFiles(directory="/docs"), name="docs")

@app.websocket("/ws/events/")
async def websocket_endpoint(websocket: WebSocket, manager: ConnectionManager = Depends(get_connection_manager)):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

######################## General ########################

@app.get("/", tags=["General"])
def welcome():
    return {"message": "Thanks for using Nexarag!"}

######################## Papers ########################

@app.post("/papers/add/", tags=["Papers"])
async def add_papers(papers: List[str]):
    message = AddPapersById(paper_ids=papers)
    await publish_message(ChannelType.ADD_PAPER, message)
    return { "message": "Papers added to the queue" }

@app.get("/papers/get/", tags=["Papers"])
async def get_paper_by_id(id: str = Query(default=None)):
    loader = load_kg_db()
    with loader() as db:
        papers = search_papers_by_id(db, id)
    return papers

@app.get("/papers/search/", tags=["Papers"])
async def search_papers_by_id(id: str = Query(default=None)):
    loader = load_kg_db()
    with loader() as db:
        papers = search_papers_by_id(db, id)
    return papers

def handle_rate_limit_exceeded(manager:ConnectionManager, e):
    manager.broadcast("error", { "message": "Rate limit exceeded. Re-attempting..."})

@app.get("/papers/search/relevance/", tags=["Papers"])
async def relevance_search_papers(query: str = Query(default=''), manager: ConnectionManager = Depends(get_connection_manager)):
    results = retry(relevance_search, query, cb=lambda e: handle_rate_limit_exceeded(manager, e))
    return results

@app.post("/papers/add/", tags=["Papers"])
async def add_papers_by_id(paper_ids: List[str]):
    message = AddPapersById(paper_ids=paper_ids)
    await publish_message(ChannelType.ADD_PAPER, message)
    return { "message": "Papers added to the queue" }

@app.get("/papers/get/all/", tags=["Papers"])
async def get_papers():
    loader = load_kg_db()
    with loader() as db:
        papers = get_all_papers(db)
    return papers

@app.post("/papers/bibtex/", tags=["Papers"])
async def add_papers_bibtex(req: BibTexRequest):
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
    bib_database = bibtexparser.loads(req.bibtex, parser=parser)

    # Parse paper data
    papers = [
        BibTexPaper(
            title=entry.get("title", "").strip(),
            author=entry.get("author", "").strip(),
            journal=entry.get("journal", "").strip(),
            year=int(entry.get("year", 0))
        )
        for entry in bib_database.entries
    ]

    # Submit for processing
    message = AddPapersByTitle(papers=[PaperTitleWithYear(title=p.title, year=p.year) for p in papers])
    await publish_message(ChannelType.ADD_PAPER_BY_TITLE, message)

    return transform_bibtex_for_cytoscape(papers)

@app.post("/papers/citations/add/", tags=["Papers"])
async def add_citations(paper_ids: List[str]):
    message = AddPaperCitations(paper_ids=paper_ids)
    await publish_message(ChannelType.ADD_CITATIONS, message)
    return { "message": "Citations added to the queue" }

@app.post("/papers/references/add/", tags=["Papers"])
async def add_references(paper_ids: List[str]):
    message = AddPaperReferences(paper_ids=paper_ids)
    await publish_message(ChannelType.ADD_REFERENCES, message)
    return { "message": "Citations added to the queue" }

######################## Graph ########################

@app.get("/graph/get/", tags=["Graph"])
def get_whole_graph():
    loader = load_kg_db()
    with loader() as db:
        graph = get_graph(db)
    return transform_for_cytoscape(graph)

@app.post("/graph/clear/", tags=["Graph"])
async def remove_whole_graph():
    message = ClearGraph(reason="User requested")
    await publish_message(ChannelType.CLEAR_GRAPH, message)
    return { "message": "Graph removal request sent" }

######################## Chat ########################
@app.post("/chat/send/", tags=["Chat"])
async def send_chat_message(request: ChatMessage):
    logger.info(f"Received chat message: {request}")
    await publish_message(ChannelType.CHAT_MESSAGE, request)
    return request

@app.get("/chat/prefix/default/", tags=["Chat"])
def get_default_prefix():
    cleaned = default_prefix.strip()
    return cleaned

######################## Documents ########################

@app.post("/docs/upload/{paper_id}", tags=["Documents"])
async def upload_docs(paper_id:str, docs: List[UploadFile] = File(...)):
    upload_info = await upload_many(docs, ollama_base_url)
    documents = [DocumentCreated(id=doc.id, node_id=paper_id, path=doc.path, og_path=doc.og_path, name=doc.name) for doc in upload_info]
    message = DocumentsCreated(documents=documents)
    await publish_message(ChannelType.DOCUMENTS_CREATED, message)
    return {
        "message": "Files uploaded successfully",
        "files": upload_info
    }

@app.post("/docs/bulk/upload/", tags=["Documents"])
async def upload_docs_no_paper(docs: List[UploadFile] = File(...)):
    logger.info(f"Uploading {len(docs)} documents without associated paper")
    upload_info = await upload_many(docs, ollama_base_url)
    documents = [DocumentCreated(id=doc.id, path=doc.path, og_path=doc.og_path, name=doc.name) for doc in upload_info]
    message = DocumentsCreated(documents=documents)
    await publish_message(ChannelType.DOCUMENTS_CREATED, message)
    return {
        "message": "Files uploaded successfully",
        "files": upload_info
    }

@app.get("/docs/list/", tags=["Documents"])
def list_available_files():
    """List all files in the documents directory with metadata"""
    docs_dir = Path("/docs")
    
    if not docs_dir.exists():
        return {"files": [], "message": "Documents directory not found"}
    
    files = []
    
    for file_path in docs_dir.iterdir():
        if file_path.is_file():
            try:
                stat = file_path.stat()
                file_info = {
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "extension": file_path.suffix.lower(),
                    "url": f"/documents/{file_path.name}",
                }
                files.append(file_info)
            except Exception as e:
                logger.warning(f"Error reading file {file_path.name}: {e}")
                continue
    
    return {
        "files": files,
        "total_count": len(files),
        "total_size": sum(f["size"] for f in files),
    }

######################## Health ########################

@app.get("/neo4j/health/", tags=["Health"])
def test_neo4j_connection():
    success = check_neo4j_connection()
    return { "message": f"Connection {'successful' if success else 'failed'}" }
    
@app.get("/rabbit/health/", tags=["Health"])
async def test_rabbit_connection():
    success = await check_rabbit_connection()
    return { "message": f"Connection {'successful' if success else 'failed'}" }

######################## LLMs ########################
@app.get("/ollama/list/", tags=["LLMs"])
def list_ollama_models():
    client = Client(host=ollama_base_url)
    models = client.list()
    return models

@app.get("/ollama/ask/", tags=["LLMs"])
def ask_ollama_model(model:str, question:str):
    llm = OllamaLLM(model=model, base_url=ollama_base_url)
    response = llm.invoke(question)
    return response

######################## Visualization ########################
@app.post("/viz/plot/", tags=["Visualizations"])
async def create_plot(cmd: CreateEmbeddingPlot):
    await publish_message(ChannelType.EMBEDDING_PLOT_REQUESTED, cmd)
    return cmd