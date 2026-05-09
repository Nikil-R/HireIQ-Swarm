import os
import json
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def search_jobs_tool(query: str):
    """
    Real tool that uses Tavily API to search the web for jobs, salaries, and trends.
    """
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return f"[ERROR] TAVILY_API_KEY not found in environment. Please add it to .env"
            
        client = TavilyClient(api_key=api_key)
        
        print(f"    [Tavily] Searching web for: {query}")
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )
        
        # We store the raw results as requested for now.
        return json.dumps(response.get("results", []), indent=2)
        
    except Exception as e:
        return f"[ERROR] Tavily Search Failed: {str(e)}"
