from langchain_community.tools import DuckDuckGoSearchResults
from langchain.tools import Tool
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Option 1: DuckDuckGo (Free, no API key needed) - Currently active
search_tool = DuckDuckGoSearchResults(num_results=5)

# Option 2: SerpAPI (Better results, requires API key) - Uncomment to use
# from langchain_community.tools import SerpAPIWrapper
# serpapi_key = os.getenv("SERPAPI_API_KEY")
# if serpapi_key:
#     search_tool = SerpAPIWrapper(serpapi_api_key=serpapi_key)
#     print("✅ Using SerpAPI for web search")
# else:
#     print("ℹ️ Using DuckDuckGo for web search (add SERPAPI_API_KEY to .env for SerpAPI)")

def web_search_tool(query: str, max_results: int = 3) -> str:
    """Search the web using DuckDuckGo and return formatted results with relevance filtering"""
    try:
        results = search_tool.run(query)
        
        # Parse the results if they come as string
        if isinstance(results, str):
            # Try to parse as JSON if possible
            try:
                results_list = json.loads(results)
            except json.JSONDecodeError:
                # If not JSON, return as is but truncated
                return results[:2000] + "..." if len(results) > 2000 else results
        else:
            results_list = results
        
        # Format and filter relevant results
        formatted_results = []
        query_terms = query.lower().split()
        
        for i, result in enumerate(results_list[:max_results * 2]):  # Get more to filter
            if isinstance(result, dict):
                title = result.get('title', 'No title')
                snippet = result.get('snippet', result.get('content', 'No content'))
                link = result.get('link', result.get('url', ''))
                
                # Check relevance - title and snippet should contain query terms
                combined_text = f"{title} {snippet}".lower()
                relevance_score = sum(1 for term in query_terms if term in combined_text) / len(query_terms)
                
                # Only include if at least 20% of query terms are found
                if relevance_score > 0.2:
                    formatted_result = f"**{title}**\n{snippet}"
                    if link:
                        formatted_result += f"\nSource: {link}"
                    formatted_results.append(formatted_result)
                    
                    # Stop when we have enough relevant results
                    if len(formatted_results) >= max_results:
                        break
            else:
                formatted_results.append(str(result))
        
        if not formatted_results:
            return "No relevant web search results found for this query."
        
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        print(f"Web search failed: {e}")
        return f"Web search temporarily unavailable. Error: {str(e)}"
