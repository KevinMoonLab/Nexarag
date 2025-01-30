from fastapi import FastAPI, UploadFile, File, Query
from typing import List
from db.util import check_connection as check_neo4j_connection, load_kg_db
from db.queries import search_papers_by_id, get_all_papers, get_graph
from shared.rabbit import check_connection as check_rabbit_connection, publish_message, ChannelType
from shared.schemas import AddPapersByTitle, ClearGraph
from .upload import upload_many
from .util import transform_for_cytoscape
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI instance
app = FastAPI(title="LitReview API", description="API for managing the LitReview knowledge graph")

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)
# Root
@app.get("/", tags=["General"])
def welcome():
    return {"message": "Thanks for using LitReview!"}

@app.post("/docs/upload/", tags=["Documents"])
async def upload_docs(docs: List[UploadFile] = File(...)):
    upload_info = await upload_many(docs)
    return {
        "message": "Files uploaded successfully",
        "files": upload_info
    }

@app.post("/papers/add/", tags=["Papers"])
async def add_papers(papers: List[str]):
    message = AddPapersByTitle(titles=papers)
    await publish_message(ChannelType.ADD_PAPER, message)
    return { "message": "Papers added to the queue" }

@app.get("/papers/get/", tags=["Papers"])
async def get_paper_by_id(id: str = Query(default=None)):
    loader = load_kg_db()
    with loader() as db:
        papers = search_papers_by_id(db, id)
    return papers

@app.get("/papers/search/", tags=["Papers"])
async def search_papers_by_title(id: str = Query(default=None)):
    loader = load_kg_db()
    with loader() as db:
        papers = search_papers_by_id(db, id)
    return papers

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