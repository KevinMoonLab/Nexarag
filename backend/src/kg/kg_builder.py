import semantic_scholar_api as ss_api
import logging
from db.commands import create_cites_rel, create_paper_node, create_author_node, create_authored_rel
from db.queries import search_papers_by_id

logger = logging.getLogger(__name__)

DEFAULT_CITATION_FIELDS = ["title", "abstract", "citationCount", "publicationDate", "authors"]

def create_citation_graph(kg, paper_data):
    results = []
    for paper in paper_data:
        try:
            citation_data = ss_api.exponential_backoff_retry(ss_api.get_paper_references, paper['paperId'], fields=DEFAULT_CITATION_FIELDS)
            for cited_paper in citation_data['data']:
                cited_paper = cited_paper['citedPaper']
                cited_paper_nodes = search_papers_by_id(kg, cited_paper['paperId'])
                if len(cited_paper_nodes) == 0:
                    cited_paper['level'] = 2
                    paper_properties = {key: value for key, value in cited_paper.items() if key != 'authors'}
                    cited_paper_nodes = create_paper_node(kg, paper_properties)
                rel_cites = create_cites_rel(kg, paper['paperId'], cited_paper['paperId'])     
                author_data = build_author_data(kg, cited_paper['authors'], cited_paper['paperId'])
                result = {
                    "papers": cited_paper_nodes,
                    "citations": rel_cites,
                    "author": author_data
                }
                results.append(result)
        except ss_api.RateLimitExceededError:
            logger.error("Exceeded rate limit. Please try again later.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
    return results
                
def build_author_data(kg, authors, paperId):
    results = []
    for author in authors:
        if author['authorId'] is None:
            continue
        author_node = create_author_node(kg, author)   
        author_rel = create_authored_rel(kg, paperId, author['authorId']) 
        result = {
            "author": author_node,
            "authored": author_rel
        }
        results.append(result)
    return results