from kg.docs import create_chunk_nodes
from db.util import load_default_kg
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rabbit.events import DocumentGraphUpdated
import logging

async def handle_documents_created(update: DocumentGraphUpdated, logger = logging.getLogger(__name__)):
    doc = update.doc
    logger.info(f"Received documents created: {doc}")

    # Load file content
    doc_path = f"/docs/{doc.path}"
    with open(doc_path, "r") as f:
        content = f.read()
    
    # Chunk the content
    kg = load_default_kg()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000, # FIXME
        chunk_overlap  = 200,
        length_function = len,
        is_separator_regex = False,
    )
    
    create_chunk_nodes(kg, content, doc.node_id, text_splitter)
    logger.info(f"Created chunk nodes for document: {doc.node_id}: {doc.path}")

def init_graph(embedding_size=768, similarity="cosine"):
    kg = load_default_kg()
    kg.query("""
        CREATE VECTOR INDEX `paper_chunks` IF NOT EXISTS
        FOR (c:Chunk) ON (c.textEmbedding) 
        OPTIONS { indexConfig: {
            `vector.dimensions`: $dimension,
            `vector.similarity_function`: $similarity    
        }}""", params={'dimension': embedding_size, 'similarity': similarity }
    )

    kg.query("""
        CREATE VECTOR INDEX abstract_embeddings IF NOT EXISTS
        FOR (p:Paper) ON (p.abstractEmbedding) 
        OPTIONS { indexConfig: {
            `vector.dimensions`: $dimension,
            `vector.similarity_function`: $similarity
        }}""", params={'dimension': embedding_size, 'similarity': similarity }
    )