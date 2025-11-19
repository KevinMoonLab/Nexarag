from .util import run_query
from neomodel import db

def get_all_papers(kg):
    cypher = """
    MATCH (p:Paper)
    RETURN p
    """
    result = run_query(kg, cypher)
    return result

def get_graph(kg):
    # Get relationships
    cypher_rels = """
    MATCH (n)-[r]->(m)
    WHERE (n:Paper OR n:Author OR n:Document OR n:PublicationVenue OR n:Journal OR n:ChatMessage OR n:ChatResponse)
      AND (m:Paper OR m:Author OR m:Document OR m:PublicationVenue OR m:Journal OR m:ChatMessage OR m:ChatResponse)
    RETURN n, r, m
    """
    
    # Get isolated nodes
    cypher_isolated = """
    MATCH (n)
    WHERE (n:Paper OR n:Author OR n:Document OR n:PublicationVenue OR n:Journal OR n:ChatMessage OR n:ChatResponse)
      AND NOT (n)-[]-()
    RETURN n, null as r, null as m
    """
    
    relationships = run_query(kg, cypher_rels)
    isolated = run_query(kg, cypher_isolated)
    
    return relationships + isolated

def search_papers_by_id(kg, paper_id):
    cypher = """
    MATCH (p:Paper {paper_id: $paper_id})
    RETURN p
    """
    result = run_query(kg, cypher, params={'paper_id': paper_id})
    return result

def search_papers_by_title(kg, searchTerm):
    cypher = """
    MATCH (p:Paper)
    WHERE p.title CONTAINS $searchTerm
    RETURN p
    """
    result = run_query(kg, cypher, params={'searchTerm': searchTerm})
    return result

def retrieve_similar_chunks(embedding, k=30):
    query = """
        MATCH (c:Chunk)
        WITH DISTINCT c, vector.similarity.cosine(c.textEmbedding, $embedding) AS score
        WHERE score > 0.5 
        ORDER BY score DESC LIMIT $k
        RETURN c.text AS text, score, c.source AS source, c.chunkId AS chunkId
    """
    
    results, meta = db.cypher_query(
        query, 
        {'embedding': embedding, 'k': k}
    )
    
    return [
        {
            'text': row[0],
            'score': row[1],
            'metadata': {
                'source': row[2],
                'chunkId': row[3]
            }
        }
        for row in results
    ]

def retrieve_similar_abstracts(embedding, k=30):
    query = """
        MATCH (p:Paper)
        WHERE p.abstract IS NOT NULL AND p.title IS NOT NULL
        WITH DISTINCT p, vector.similarity.cosine(p.abstract_embedding, $embedding) AS score
        WHERE score > 0.5 
        ORDER BY score DESC LIMIT $k
        RETURN 'Title: ' + p.title + '\\n\\n' + 'Abstract: ' + p.abstract AS text, 
               score, p.paper_id AS paper_id
    """
    
    results, meta = db.cypher_query(
        query, 
        {'embedding': embedding, 'k': k}
    )
    
    return [
        {
            'text': row[0],
            'score': row[1],
            'metadata': {
                'paper_id': row[2]
            }
        }
        for row in results
    ]