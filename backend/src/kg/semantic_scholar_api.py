import time
import requests
import pandas as pd
from tqdm.auto import tqdm

class RateLimitExceededError(Exception):
    """Custom exception for rate limit errors."""
    pass

def exponential_backoff_retry(
    func,
    *args,
    max_retries=6,
    base_delay=1,
    max_delay=32,
    **kwargs
):
    """
    Retries a function with exponential backoff.

    Args:
        func: A callable that may raise an exception.
        *args: Variable number of positional arguments to pass to the function.
        max_retries (int): Maximum number of retries before giving up. Defaults to 6.
        base_delay (float): Initial delay in seconds. Defaults to 1.
        max_delay (float): Maximum delay in seconds. Defaults to 32.
        **kwargs: Variable number of keyword arguments to pass to the function.

    Returns:
        The result of the function if successful.

    Raises:
        The last exception raised if all retries fail.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except RateLimitExceededError as e:
            if attempt == max_retries:
                raise  # Re-raise the last exception
            else:
                delay = min(base_delay * 2**(attempt - 1), max_delay)
                # print(f"Attempt {attempt} failed due to rate limit. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise


def search_paper_by_title(title, year=None):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": f"title:({title})",
        "fields": "title,url,publicationTypes,publicationDate,citationCount,authors,abstract",
        "limit": 1  # Adjust as needed
    }
    if year:
        params['year'] = year

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            return data["data"][0]  # Return the first matching paper
        else:
            print(f"No matching papers found for {title}.")
            return None
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        response.raise_for_status()
        
def get_paper_citations(paper_id, fields=None, year=None, limit=None):
    """
    Retrieves citation information for a given paper ID from the Semantic Scholar API.

    Args:
        paper_id (str): The Semantic Scholar paper ID.
        fields (list, optional): List of fields to include in the response. Defaults to None. Options include:
            * title
            * url
            * publicationTypes
            * publicationDate
            * openAccessPdf
            * citationCount
            * authors
            * abstract
            * contexts
            * intents
            * isInfluential

    Returns:
        dict: Citation data for the specified paper.
    """
    base_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    params = {}
    if fields:
        params['fields'] = ','.join(fields)
    if year:
        params['year'] = year
    if limit:
        params['limit'] = limit
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        print(f"Error {response.status_code}: Unable to fetch citations for paper ID {paper_id}")
        return None
    
def get_paper_references(paper_id, fields=None, year=None, limit=None):
    """
    Retrieves citation information for a given paper ID from the Semantic Scholar API.

    Args:
        paper_id (str): The Semantic Scholar paper ID.
        fields (list, optional): List of fields to include in the response. Defaults to None. Options include:
            * title
            * url
            * publicationTypes
            * publicationDate
            * openAccessPdf
            * citationCount
            * authors
            * abstract
            * contexts
            * intents
            * isInfluential

    Returns:
        dict: Citation data for the specified paper.
    """
    base_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references"
    params = {}
    if fields:
        params['fields'] = ','.join(fields)
    if year:
        params['year'] = year
    if limit:
        params['limit'] = limit
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        raise RateLimitExceededError("Rate limit exceeded. Please wait before retrying.")
    else:
        print(f"Error {response.status_code}: Unable to fetch citations for paper ID {paper_id}")
        return None

def extract_paper_data(titles, max_retries=6, base_delay=1, max_delay=32):
    data = []
    for title in tqdm(titles):
        try:
            paper_data = exponential_backoff_retry(
                search_paper_by_title,
                title=title,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay
            )
            if paper_data:
                data.append(paper_data)
        except RateLimitExceededError:
            print("Exceeded rate limit. Please try again later.")
        except Exception as e:
            print(f"An error occurred: {e}")
    return data