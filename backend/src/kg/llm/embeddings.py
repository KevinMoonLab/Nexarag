from kg.db.util import load_default_kg
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rabbit.events import DocumentGraphUpdated
from kg.llm.chat import NomicEmbeddingAdapter
from kg.db.models import Paper, Chunk
import re


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
    
    for chunk in chunks:
        # Compute embedding
        embedding = nomic_adapter.embed_query(chunk['text'])
        
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
        chunk_size = 5000,
        chunk_overlap  = 200,
        length_function = len,
        is_separator_regex = False,
    )
    
    await create_chunk_nodes_with_embeddings(content, doc.node_id, text_splitter)
