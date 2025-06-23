from .util import run_query

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
    WHERE (n:Paper OR n:Author OR n:Document OR n:PublicationVenue OR n:Journal)
      AND (m:Paper OR m:Author OR m:Document OR m:PublicationVenue OR m:Journal)
    RETURN n, r, m
    """
    
    # Get isolated nodes
    cypher_isolated = """
    MATCH (n)
    WHERE (n:Paper OR n:Author OR n:Document OR n:PublicationVenue OR n:Journal)
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