from .models import Paper, Author, PartialPaper, Citation, PaperRelevanceResult
from .util import RateLimitExceededError, retry
import requests
import json
from typing import List

DEFAULT_PAPER_FIELDS = "title,abstract,venue,publicationVenue,year,referenceCount,citationCount,influentialCitationCount,publicationTypes,publicationDate,journal,authors"
DEFAULT_AUTHOR_FIELDS = "authorId,url,name,affiliations,homepage,paperCount,citationCount,hIndex"

def relevance_search(text, limit = 100) -> list[PaperRelevanceResult]:
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={text}&fields=title,authors,year&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            return PaperRelevanceResult.schema().load(data.get("data"), many=True)
        else:
            return []
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        response.raise_for_status()

def partial_search(text) -> list[PartialPaper]:
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={text}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("matches"):
            return PartialPaper.schema().load(data.get("matches"), many=True)
        else:
            return []
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        response.raise_for_status()

def title_search(title, year=None, fields = DEFAULT_PAPER_FIELDS) -> list[Paper]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": f"title:({title})",
        "fields": fields
    }
    if year and year > 0:
        params['year'] = year

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            return Paper.schema().load(data.get("data"), many=True)
        else:
            return []
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        response.raise_for_status()

def enrich_papers(paper_ids: list[str], fields: str = DEFAULT_PAPER_FIELDS) -> list[Paper]:
    url = f"https://api.semanticscholar.org/graph/v1/paper/batch"
    params = { 'fields': fields }
    paper_ids = { 'ids': paper_ids }
    response = requests.post(url, params=params, json=paper_ids)
    if response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    return Paper.schema().load(response.json(), many=True)

def enrich_authors(author_ids: list[str], fields: str = DEFAULT_AUTHOR_FIELDS) -> list[Author]:
    url = f"https://api.semanticscholar.org/graph/v1/author/batch"
    params = {'fields': fields}
    author_ids_payload = {'ids': author_ids}

    response = requests.post(url, params=params, json=author_ids_payload)
    if response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")

    data = response.json()
    data = filter(lambda x: x is not None, data)
    return Author.schema().load(data, many=True)

def get_citations(paper_id: str) -> list[Citation]:
    base_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    response = requests.get(base_url, params={})
    if response.status_code == 200:
        data = response.json()
        papers = [d['citingPaper'] for d in data['data']]
        return Citation.schema().load(papers, many=True)
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        print(f"Error {response.status_code}: Unable to fetch citations for paper ID {paper_id}")
        return []
    
def get_references(paper_id: str) -> list[Citation]:
    base_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references"
    params = {}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        references = [d['citedPaper'] for d in data['data'] if d['citedPaper']['paperId'] is not None]
        return Citation.schema().load(references, many=True)
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        print(f"Error {response.status_code}: Unable to fetch citations for paper ID {paper_id}")
        return None
    
def get_recommendations(positive_paper_ids, negative_paper_ids, limit = 100) -> list[Citation]:
    url = f"http://api.semanticscholar.org/recommendations/v1/papers?fields=paperId,title&limit={limit}"
    params = {
        "positivePaperIds": positive_paper_ids,
        "negativePaperIds": negative_paper_ids
    }
    response = requests.post(url, data=json.dumps(params))
    if response.status_code == 200:
        data = response.json()
        return Citation.schema().load(data.get("recommendedPapers", []), many=True)
    else:
        print(f"Failed to get recommendations: {response.status_code} {response.text}")
        return []
    
def search_papers_by_title(title:str, year:int) -> Paper:
    res = retry(title_search, title, year)
    if len(res) > 0:
        return res[0]
    return None