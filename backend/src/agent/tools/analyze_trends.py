import os
import json
from tavily import TavilyClient

def analyze_trends_tool(query: str):
    """
    Uses Tavily API to analyze market trends.
    """
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "[ERROR] TAVILY_API_KEY not found"
            
        client = TavilyClient(api_key=api_key)
        
        print(f"    [Tavily] Analyzing trends for: {query}")
        response = client.search(
            query=f"Market trends and job demand for {query}",
            search_depth="advanced",
            max_results=3
        )
        
        return json.dumps(response.get("results", []), indent=2)
        
    except Exception as e:
        return f"[ERROR] Trend Analysis Failed: {str(e)}"
