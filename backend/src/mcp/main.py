from typing import Any, List
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

port = os.environ.get("MCP_PORT", 9000)
api_port = os.environ.get("API_PORT", 8000)

mcp = FastMCP("nexarag")
API_BASE_URL = f"http://nexarag.api:{api_port}"
API_TIMEOUT = 30.0

async def make_api_request(method: str, endpoint: str, json_data: dict = None) -> Any:
    """Make a request to the papers API with proper error handling."""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, timeout=API_TIMEOUT)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json_data, timeout=API_TIMEOUT)
            else:
                return None
                
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

@mcp.tool()
async def add_papers(paper_ids: List[str]) -> str:
    """Add papers to the processing queue.

    Args:
        paper_ids: List of paper IDs to add to the queue
    """
    result = await make_api_request("POST", "/papers/add/", paper_ids)
    
    if not result:
        return "Failed to add papers to queue"
    
    if "error" in result:
        return f"Error adding papers: {result['error']}"
    
    return result.get("message", "Papers added successfully")

@mcp.tool()
async def get_all_papers() -> str:
    """Get all papers from the database.
    
    Returns:
        A formatted string containing information about all papers in the database
    """
    result = await make_api_request("GET", "/papers/get/all")
    logger.info(f"Get all papers result: {result}")
    
    if not result:
        return "Failed to retrieve papers from database"
    
    if "error" in result:
        return f"Error retrieving papers: {result['error']}"
    
    if isinstance(result, list):
        if not result:
            return "No papers found in database"
        
        papers_info = []
        for item in result[:20]:  # Limit to top 20 papers for readability
            # Extract paper data from the nested structure
            paper = item.get('p', {}).get('properties', {})
            
            # Format the paper information
            paper_text = f"ID: {paper.get('paper_id', 'Unknown')}\n"
            paper_text += f"Title: {paper.get('title', 'Unknown')}\n"
            paper_text += f"Year: {paper.get('year', 'N/A')}\n"
            paper_text += f"Publication Date: {paper.get('publication_date', 'N/A')}\n"
            paper_text += f"Citation Count: {paper.get('citation_count', 'N/A')}\n"
            paper_text += f"Influential Citation Count: {paper.get('influential_citation_count', 'N/A')}\n"
            paper_text += f"Reference Count: {paper.get('reference_count', 'N/A')}\n"
            paper_text += f"Publication Types: {paper.get('publication_types', 'N/A')}\n"
            
            # Add abstract preview (first 200 characters)
            abstract = paper.get('abstract', 'No abstract available')
            if len(abstract) > 200:
                abstract = abstract[:200] + "..."
            paper_text += f"Abstract: {abstract}"
            
            papers_info.append(paper_text)
        
        total_count = len(result)
        displayed_count = len(papers_info)
        
        response = f"Found {total_count} papers in database"
        if displayed_count < total_count:
            response += f" (showing first {displayed_count})"
        response += ":\n\n" + "\n\n---\n\n".join(papers_info)
        
        return response
    
    logger.info(f"Get all papers returned unexpected result type: {type(result)}")
    return str(result)

@mcp.tool()
async def add_paper_citations(paper_ids: List[str]) -> str:
    """Add citations for the specified papers to the processing queue.

    Args:
        paper_ids: List of paper IDs to add citations for
    """
    # Prepare the request body
    request_body = paper_ids
    
    result = await make_api_request("POST", "/papers/citations/add/", json_data=request_body)
    logger.info(f"Add citations result: {result}")
    
    if not result:
        return "Failed to add citations to queue"
    
    if "error" in result:
        return f"Error adding citations: {result['error']}"
    
    # Check for success message
    if isinstance(result, dict) and "message" in result:
        return result["message"]
    
    return "Citations added to the queue"


@mcp.tool()
async def add_paper_references(paper_ids: List[str]) -> str:
    """Add references for the specified papers to the processing queue.

    Args:
        paper_ids: List of paper IDs to add references for
    """
    # Prepare the request body
    request_body = paper_ids
    
    result = await make_api_request("POST", "/papers/references/add/", json_data=request_body)
    logger.info(f"Add references result: {result}")
    
    if not result:
        return "Failed to add references to queue"
    
    if "error" in result:
        return f"Error adding references: {result['error']}"
    
    # Check for success message
    if isinstance(result, dict) and "message" in result:
        return result["message"]
    
    return "References added to the queue"

@mcp.tool()
async def relevance_search_papers(query: str) -> str:
    """Search for papers by relevance using a text query.

    Args:
        query: The search query to find relevant papers
    """
    result = await make_api_request("GET", f"/papers/search/relevance/?query={query}")
    logger.info(f"Relevance search result: {result}")
    
    if not result:
        return "Failed to search papers by relevance"
    
    if "error" in result:
        return f"Error searching papers: {result['error']}"
    
    if isinstance(result, list):
        if not result:
            return f"No papers found for query: '{query}'"
        
        papers_info = []
        for paper in result[:10]:  # Limit to top 10 results
            # Extract author names from the list of dictionaries
            authors = [author.get('name', 'Unknown') for author in paper.get('authors', [])]
            authors_str = ', '.join(authors)
            
            paper_text = f"ID: {paper.get('paperId', 'Unknown')}\nTitle: {paper.get('title', 'Unknown')}\nAuthors: {authors_str}\nYear: {paper.get('year', 'N/A')}"
            papers_info.append(paper_text)
        
        logger.info(f"Top {len(papers_info)} papers for query '{query}': {papers_info}")
        return f"Found {len(result)} papers for '{query}':\n\n" + "\n\n---\n\n".join(papers_info)

    logger.info(f"Relevance search returned unexpected result type: {type(result)}")
    return str(result)

# Add FastAPI healthcheck endpoint using custom_route
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for container orchestration."""
    return JSONResponse({
        "status": "healthy",
        "service": "nexarag-mcp-server",
        "tools_available": [
            "add_papers",
            "relevance_search_papers"
        ]
    })

if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = int(port)
    mcp.run(transport="streamable-http")
