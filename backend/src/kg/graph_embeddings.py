from kg.docs import create_chunk_nodes
from db.util import load_default_kg
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rabbit.events import DocumentGraphUpdated
import logging
from transformers import AutoTokenizer, AutoModel
from kg.rag import compute_embedding_nomic

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

def handle_graph_update(paper_ids, model_id='nomic-ai/nomic-embed-text-v1.5'):
    # Load database and extract paper nodes
    kg = load_default_kg()
    result = kg.query(
        """
        MATCH (p:Paper) 
        WHERE p.paper_id IN $paper_ids
        RETURN elementId(p) AS node_id, p.abstract AS abstract
        """,
        parameters={"paper_ids": paper_ids}
    )
    
    # Load the model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id, model_max_length=8192)
    model = AutoModel.from_pretrained(model_id, trust_remote_code=True, rotary_scaling_factor=2)
    model.eval()

    # Compute embeddings for each paper
    for record in result:
        if record["abstract"]:
            embedding = compute_embedding_nomic(record["abstract"], tokenizer, model, config)
            # embedding = rag.compute_embedding(record["abstract"], tokenizer, model)
            kg.query("""
                MATCH (p:Paper) WHERE elementId(p) = $node_id
                SET p.abstractEmbedding = $embedding
                RETURN elementId(p) AS node_id, p.abstract AS abstract
                """, params={"node_id":record["node_id"], "embedding":embedding}
            )