import os
import json
from tavily import TavilyClient

def fetch_jd_tool(query: str):
    """
    Uses Tavily API to fetch Job Descriptions.
    """
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "[ERROR] TAVILY_API_KEY not found"
            
        client = TavilyClient(api_key=api_key)
        
        print(f"    [Tavily] Fetching JD for: {query}")
        response = client.search(
            query=f"Job description and requirements for {query}",
            search_depth="advanced",
            max_results=3
        )
        
        return json.dumps(response.get("results", []), indent=2)
        
    except Exception as e:
        return f"[ERROR] JD Fetch Failed: {str(e)}"
