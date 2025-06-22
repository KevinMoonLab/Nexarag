from kg.llm.docs import create_chunk_nodes_with_embeddings
from kg.db.util import load_default_kg
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rabbit.events import DocumentGraphUpdated
from kg.llm.chat import NomicEmbeddingAdapter

async def create_document_embeddings(update: DocumentGraphUpdated):
    doc = update.doc
    # Load file content
    doc_path = f"/docs/{doc.path}"
    with open(doc_path, "r") as f:
        content = f.read()
    
    # Chunk the content
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 10000,
        chunk_overlap  = 200,
        length_function = len,
        is_separator_regex = False,
    )
    
    await create_chunk_nodes_with_embeddings(content, doc.node_id, text_splitter)

def create_abstract_embeddings(paper_ids, model_id='nomic-embed-text:v1.5'):
    result = kg.query(
        """
        MATCH (p:Paper) 
        WHERE p.paper_id IN $paper_ids
        RETURN elementId(p) AS node_id, p.abstract AS abstract
        """,
        params={"paper_ids": paper_ids}
    )
    
    # Load the embedding adapter
    nomic_adapter = NomicEmbeddingAdapter(model_id=model_id)

    # Compute embeddings for each paper
    for record in result:
        if record["abstract"]:
            embedding = nomic_adapter.embed_query(record["abstract"])
            kg.query("""
                MATCH (p:Paper) WHERE elementId(p) = $node_id
                SET p.abstractEmbedding = $embedding
                RETURN elementId(p) AS node_id, p.abstract AS abstract
                """, params={"node_id":record["node_id"], "embedding":embedding}
            )

    return result
