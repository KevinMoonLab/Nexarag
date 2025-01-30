from .models import ScholarPaper, ScholarAuthor
from shared.utils import RateLimitExceededError
import requests

DEFAULT_PAPER_FIELDS = "title,abstract,venue,publicationVenue,year,referenceCount,citationCount,influentialCitationCount,publicationTypes,publicationDate,journal,authors"
DEFAULT_AUTHOR_FIELDS = "authorId,url,name,affiliations,homepage,paperCount,citationCount,hIndex"

def title_search(title, year=None, fields = DEFAULT_PAPER_FIELDS) -> list[ScholarPaper]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": f"title:({title})",
        "fields": fields
    }
    if year:
        params['year'] = year

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            return [ScholarPaper.from_dict(paper) for paper in data["data"]]
        else:
            return []
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        response.raise_for_status()

def partial_search(text) -> list[ScholarPaper]:
    url = f"https://api.semanticscholar.org/graph/v1/paper/autocomplete?query={text}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("matches"):
            return [ScholarPaper.from_dict(paper) for paper in data["matches"]]
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        response.raise_for_status()

def enrich_papers(papers: list[ScholarPaper], fields: str = DEFAULT_PAPER_FIELDS) -> list[ScholarPaper]:
    url = f"https://api.semanticscholar.org/graph/v1/paper/batch"
    paper_ids = [paper.paper_id for paper in papers]
    params = { 'fields': fields }
    paper_ids = { 'ids': paper_ids }
    response = requests.post(url, params=params, json=paper_ids)
    if response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    data = response.json()
    return [ScholarPaper.from_dict(paper) for paper in data]

def enrich_authors(author_ids: list[str], fields: str = DEFAULT_AUTHOR_FIELDS) -> list[ScholarAuthor]:
    url = f"https://api.semanticscholar.org/graph/v1/author/batch"
    params = { 'fields': fields }
    author_ids = { 'ids': author_ids }
    response = requests.post(url, params=params, json=author_ids)
    if response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    data = response.json()
    return ScholarAuthor.from_list(data)

def get_paper_citations(paper_id) -> list[ScholarPaper]:
    base_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    response = requests.get(base_url, params={})
    if response.status_code == 200:
        data = response.json()
        data = [d['citingPaper'] for d in data['data']]
        return ScholarPaper.from_list(data)
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        print(f"Error {response.status_code}: Unable to fetch citations for paper ID {paper_id}")
        return None
    
def get_paper_references(paper_id) -> list[ScholarPaper]:
    base_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references"
    params = {}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        data = [d['citedPaper'] for d in data['data']]
        return ScholarPaper.from_list(data)
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        print(f"Error {response.status_code}: Unable to fetch citations for paper ID {paper_id}")
        return None