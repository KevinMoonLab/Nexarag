from langchain.text_splitter import RecursiveCharacterTextSplitter
from rabbit.events import DocumentGraphUpdated
from kg.llm.chat import NomicEmbeddingAdapter
from kg.db.models import Paper, Chunk
import re
import logging
import os
logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", 500))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", 100))


def paper_data_from_file(md_text, paper_id, text_splitter):
    chunks_with_metadata = []
    md_text = remove_references_section(md_text)
    split_text = text_splitter.split_text(md_text)
    for i, chunk in enumerate(split_text):
        chunk = "search_document: " + chunk
        chunks_with_metadata.append({
            'text': chunk, 
            'paper_id': paper_id,
            'chunkId': f"{i}_{paper_id}"
        })
    return chunks_with_metadata

def remove_references_section(text):
    split_result = re.split(r"(?i)(?:\n|\r\n)(?:\s*#+\s*)?(References|Bibliography)\b", text)
    return split_result[0] if split_result else text


async def create_chunk_nodes_with_embeddings(md_text, paper_id, text_splitter, model_id='nomic-embed-text:v1.5'):
    node_count = 0
    nomic_adapter = NomicEmbeddingAdapter(model_id=model_id)
    chunks = paper_data_from_file(md_text, paper_id, text_splitter)
    previous_chunk_node = None
    
    # Get the paper node
    paper_node = await Paper.nodes.get_or_none(paper_id=paper_id)
    
    logger.info(f"Creating chunk nodes for paperId: {paper_id}, total chunks: {len(chunks)}")
    for chunk in chunks:
        try:
            embedding = nomic_adapter.embed_query(chunk['text'])
        except Exception as e:
            logger.error(f"Error creating chunk node for chunkId: {chunk['chunkId']}: {e}")
            logger.error(f"Chunk text: {chunk['text'][:-10]}...")
            logger.error("The DEFAULT_CHUNK_SIZE is likely too large for the embedding model.")
            continue    

        if embedding is None:
            logger.error(f"Embedding is None for chunkId: {chunk['chunkId']}")
            continue
        
        # Create or get chunk using neomodel
        chunk_node = await Chunk(
            chunkId=chunk['chunkId'],
            paper_id=chunk['paper_id'],
            source=chunk['paper_id'],
            text=chunk['text'],
            textEmbedding=embedding
        ).save()
        
        # Connect to paper
        if paper_node is not None:
            await chunk_node.paper.connect(paper_node)
        
        # Link to previous chunk
        if previous_chunk_node is not None:
            await previous_chunk_node.next_chunk.connect(chunk_node)
        
        previous_chunk_node = chunk_node
        node_count += 1
    
    return node_count

def create_abstract_embedding(abstract: str, model_id='nomic-embed-text:v1.5'):
    nomic_adapter = NomicEmbeddingAdapter(model_id=model_id)
    embedding = nomic_adapter.embed_query(abstract)
    return embedding


async def create_document_embeddings(update: DocumentGraphUpdated):
    doc = update.doc
    # Load file content
    doc_path = f"/docs/{doc.path}"
    with open(doc_path, "r") as f:
        content = f.read()
    
    # Chunk the content
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = DEFAULT_CHUNK_SIZE,
        chunk_overlap  = DEFAULT_CHUNK_OVERLAP,
        length_function = len,
        is_separator_regex = False,
    )
    
    await create_chunk_nodes_with_embeddings(content, doc.node_id, text_splitter)
