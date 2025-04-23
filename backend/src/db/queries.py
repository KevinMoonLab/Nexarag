from .util import run_query

def get_all_papers(kg):
    cypher = """
    MATCH (p:Paper)
    RETURN p
    """
    result = run_query(kg, cypher)
    return result

def get_graph(kg):
    cypher = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    result = run_query(kg, cypher)
    return result

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