from tqdm.auto import tqdm
from .util import run_query

def create_paper_nodes(kg, paper_data):
    author_info = []
    papers = []
    for i, paper in tqdm(enumerate(paper_data)):
        if paper is None:
            continue
        paper_properties = {key: value for key, value in paper.items() if key != 'authors'}
        paper_properties['level'] = 1
        result = create_paper_node(kg, paper_properties)
        papers.append(result)
        author_info.append({key: value for key, value in paper.items() if key in ['paper_id', 'authors']})
    
    return papers, author_info

def clear_graph(kg):
    cypher = "MATCH (n) DETACH DELETE n"
    return run_query(kg, cypher)
    
def create_paper_node(kg, paper_data):
    cypher = """
    MERGE (p:Paper {paper_id: $paper_data.paper_id})
    SET p += $paper_data
    RETURN p
    """
    return run_query(kg, cypher, params={'paper_data': paper_data})
    
def create_author_nodes(kg, author_info):
    results = []
    for paper_authors in tqdm(author_info):
        if paper_authors is None:
            continue
        for author in paper_authors['authors']:
            result = create_author_node(kg, author)
            results.append(result)
    return results
            
def create_author_node(kg, author_info):
    cypher = """
    MERGE (a:Author {author_id: $author.author_id, name: $author.name})
    RETURN a
    """
    return run_query(kg, cypher, params={'author': author_info})
            
def create_authored_rels_papers(kg, author_info): 
    results = []  
    for paper_authors in tqdm(author_info):
        if paper_authors is None:
            continue
        for author in paper_authors['authors']:
            result = create_authored_rel(kg, paper_authors['paper_id'], author['author_id'])
            results.append(result)
    return results
            
def create_authored_rel_paper(kg, paper_id, authors):
    results = []
    for author in authors:
        result = create_authored_rel(kg, paper_id, author['author_id'])
        results.append(result)
    return results
            
def create_authored_rel(kg, paper_id, author_id):
    cypher = """
    MATCH (p:Paper {paper_id: $paper_id})
    MATCH (a:Author {author_id: $author_id})
    MERGE (a)-[:Authored]->(p)
    """
    return run_query(kg, cypher, params={'paper_id': paper_id, 'author_id': author_id})

def create_cites_rel(kg, p1_id, p2_id):  
    cypher = """
    MATCH (p1:Paper {paper_id: $paper_id1})
    MATCH (p2:Paper {paper_id: $paper_id2})
    MERGE (p1)-[r:Cited]->(p2)
    """    
    return run_query(kg, cypher, params={'paper_id1': p1_id, 'paper_id2': p2_id})
    