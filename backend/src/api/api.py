from fastapi import FastAPI, UploadFile, File, Query, WebSocket, WebSocketDisconnect, Depends
from typing import List
from db.util import check_connection as check_neo4j_connection, load_kg_db
from db.queries import search_papers_by_id, get_all_papers, get_graph
from rabbit.schemas import AddPapersById, ClearGraph, PapersAdded
from scholar.api import partial_search, relevance_search
from scholar.util import retry
from rabbit import publish_message, ChannelType, check_connection as check_rabbit_connection, subscribe_to_queue
from .upload import upload_many
from .util import transform_for_cytoscape
from fastapi.middleware.cors import CORSMiddleware
from .sockets import ConnectionManager
from contextlib import asynccontextmanager
import asyncio
import logging

######################## Configuration ########################

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

######################## WebSockets ########################

manager = ConnectionManager()
def get_connection_manager():
    return manager

async def handle_add_result(message: PapersAdded):
    logger.info(f"Received add result: {message}")
    await manager.broadcast("add_papers_result", {})

async def subscribe_to_rabbitmq():
    logger.info("Subscribing to RabbitMQ events...")
    await asyncio.gather(
        subscribe_to_queue(ChannelType.PAPERS_ADDED, handle_add_result, PapersAdded)
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
    allow_origins=["http://localhost:4200"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

######################## API ########################

@app.get("/", tags=["General"])
def welcome():
    return {"message": "Thanks for using Nexarag!"}

@app.post("/docs/upload/", tags=["Documents"])
async def upload_docs(docs: List[UploadFile] = File(...)):
    upload_info = await upload_many(docs)
    return {
        "message": "Files uploaded successfully",
        "files": upload_info
    }

@app.post("/papers/add/", tags=["Papers"])
async def add_papers(papers: List[str]):
    message = AddPapersById(paperIds=papers)
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

@app.post("/papers/add", tags=["Papers"])
async def add_papers_by_id(paperIds: List[str]):
    message = AddPapersById(paperIds=paperIds)
    await publish_message(ChannelType.ADD_PAPER, message)
    return { "message": "Papers added to the queue" }

@app.get("/papers/get/all/", tags=["Papers"])
async def get_papers():
    loader = load_kg_db()
    with loader() as db:
        papers = get_all_papers(db)
    return papers

@app.get("/graph/get/", tags=["Graph"])
def get_whole_graph():
    loader = load_kg_db()
    with loader() as db:
        graph = get_graph(db)
    return transform_for_cytoscape(graph)

@app.post("/graph/remove/all", tags=["Graph"])
async def remove_whole_graph():
    message = ClearGraph(reason="User requested")
    await publish_message(ChannelType.CLEAR_GRAPH, message)
    return { "message": "Graph removal request sent" }

@app.get("/neo4j/health/", tags=["Health"])
def test_neo4j_connection():
    success = check_neo4j_connection()
    return { "message": f"Connection {'successful' if success else 'failed'}" }
    
@app.get("/rabbit/health/", tags=["Health"])
async def test_rabbit_connection():
    success = await check_rabbit_connection()
    return { "message": f"Connection {'successful' if success else 'failed'}" }