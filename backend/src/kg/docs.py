import re

def paper_data_from_file(md_text, paperId, text_splitter, verbose=False):
    chunks_with_metadata = []
    md_text = remove_references_section(md_text)
    split_text = text_splitter.split_text(md_text)
    for i, chunk in enumerate(split_text):
        chunk = "search_document: " + chunk
        chunks_with_metadata.append({
            'text': chunk, 
            'paperId': paperId,
            'chunkId': f"{i}_{paperId}"
        })
    if verbose: print(f'\tSplit into {len(split_text)} chunks')
    return chunks_with_metadata

def remove_references_section(text):
    """
    Remove the references or bibliography section from the text.
    This function looks for headings like 'References' or 'Bibliography'
    (case-insensitive), including markdown headers (e.g. '## References'),
    and returns text before that heading.
    """
    # This regex matches a newline, optional markdown header symbols (#) and spaces,
    # then the word "References" or "Bibliography" (case-insensitive) as a whole word.
    split_result = re.split(r"(?i)(?:\n|\r\n)(?:\s*#+\s*)?(References|Bibliography)\b", text)
    return split_result[0] if split_result else text


def create_chunk_nodes(kg, md_text, paperId, text_splitter, config):
    kg.query("""
    CREATE CONSTRAINT unique_chunk IF NOT EXISTS 
        FOR (c:Chunk) REQUIRE c.chunkId IS UNIQUE
    """)

    merge_chunk_node_query = """
    MERGE (mergedChunk:Chunk {chunkId: $chunkParam.chunkId})
      ON CREATE SET 
          mergedChunk.paperId = $chunkParam.paperId, 
          mergedChunk.source = $chunkParam.paperId,
          mergedChunk.text = $chunkParam.text
    WITH mergedChunk
    MATCH (p:Paper {paperId: $chunkParam.paperId})
    MERGE (p)-[:HAS_CHUNK]->(mergedChunk)
    RETURN mergedChunk
    """

    merge_next_relationship_query = """
    MATCH (current:Chunk {chunkId: $currentChunkId})
    MATCH (next:Chunk {chunkId: $nextChunkId})
    MERGE (current)-[:NEXT]->(next)
    """

    node_count = 0
    chunks = paper_data_from_file(md_text, paperId, text_splitter)
    previous_chunk = None
    for chunk in chunks:
        kg.query(merge_chunk_node_query, params={'chunkParam': chunk})
        node_count += 1

        if previous_chunk is not None:
            kg.query(merge_next_relationship_query,
                        params={'currentChunkId': previous_chunk['chunkId'],
                                'nextChunkId': chunk['chunkId']})
        previous_chunk = chunk
    if config['general']['verbose']: print(f"Created {node_count} nodes")