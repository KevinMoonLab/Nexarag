import re
from kg.rag import NomicEmbeddingAdapter

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


def create_chunk_nodes_with_embeddings(kg, md_text, paper_id, text_splitter, model_id='nomic-embed-text:v1.5'):
    kg.query("""
        CREATE CONSTRAINT unique_chunk IF NOT EXISTS 
        FOR (c:Chunk) REQUIRE c.chunkId IS UNIQUE
    """)

    # Cypher query to merge Chunk node
    merge_chunk_node_query = """
        MERGE (mergedChunk:Chunk {chunkId: $chunkParam.chunkId})
        ON CREATE SET 
            mergedChunk.paper_id = $chunkParam.paper_id, 
            mergedChunk.source = $chunkParam.paper_id,
            mergedChunk.text = $chunkParam.text,
            mergedChunk.textEmbedding = $chunkParam.textEmbedding
        WITH mergedChunk
        MATCH (p:Paper {paper_id: $chunkParam.paper_id})
        MERGE (p)-[:HAS_CHUNK]->(mergedChunk)
        RETURN mergedChunk
    """

    # Cypher query to link chunks
    merge_next_relationship_query = """
        MATCH (current:Chunk {chunkId: $currentChunkId})
        MATCH (next:Chunk {chunkId: $nextChunkId})
        MERGE (current)-[:NEXT]->(next)
    """

    node_count = 0
    nomic_adapter = NomicEmbeddingAdapter(model_id=model_id)
    chunks = paper_data_from_file(md_text, paper_id, text_splitter)
    previous_chunk = None
    for chunk in chunks:
        # Compute embedding
        embedding = nomic_adapter.embed_query(chunk['text'])
        chunk['textEmbedding'] = embedding

        # Save chunk node with embedding
        kg.query(merge_chunk_node_query, params={'chunkParam': chunk})
        node_count += 1

        # Link to previous chunk
        if previous_chunk is not None:
            kg.query(merge_next_relationship_query,
                     params={'currentChunkId': previous_chunk['chunkId'],
                             'nextChunkId': chunk['chunkId']})
        previous_chunk = chunk