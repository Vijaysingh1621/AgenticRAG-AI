from .chroma_store import load_chroma
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.web_search_agent import web_search_tool
from mcp.google_drive_client import get_drive_client
import json
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LLM with API key from environment
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)

def query_rag(user_input, k=5):
    """Enhanced RAG with web search, Google Drive MCP, and citations"""
    
    # Initialize all sources
    vectorstore = load_chroma()
    drive_client = get_drive_client()
    
    # 1. Local RAG Search
    rag_docs = vectorstore.similarity_search(user_input, k=k)
    rag_context = []
    citations = []
    
    for i, doc in enumerate(rag_docs):
        rag_context.append(doc.page_content)
        citation_num = len(citations) + 1
        citations.append({
            "citation": f"[{citation_num}]",
            "page": doc.metadata.get("page", "Unknown"),
            "image": doc.metadata.get("image_path", None),
            "type": "pdf",
            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
        })
    
    # 2. Google Drive MCP Search (for current/latest info requests)
    drive_results = []
    if any(word in user_input.lower() for word in ["latest", "current", "recent", "update", "new"]):
        print("🔍 Searching Google Drive...")
        try:
            drive_results = drive_client.search_and_retrieve(user_input, max_results=3)
            for result in drive_results:
                citation_num = len(citations) + 1
                citations.append({
                    "citation": f"[{citation_num}]",
                    "page": "N/A",
                    "image": None,
                    "type": "google_drive",
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "name": result.get("name", "Google Drive Document")
                })
        except Exception as e:
            print(f"Google Drive search failed: {e}")
    
    # 3. Web Search (for very recent or external info)
    web_context = ""
    if len(rag_docs) < 2 or any(word in user_input.lower() for word in ["latest", "current", "today", "news", "update", "recent"]):
        print("🔍 Triggering web search agent...")
        try:
            web_results = web_search_tool(user_input)
            web_context = web_results
            
            # Add web search citation
            if web_context:
                citation_num = len(citations) + 1
                citations.append({
                    "citation": f"[{citation_num}]",
                    "page": "N/A",
                    "image": None,
                    "type": "web",
                    "url": "https://duckduckgo.com",
                    "content": web_context[:200] + "..." if len(web_context) > 200 else web_context
                })
        except Exception as e:
            print(f"Web search failed: {e}")
            web_context = ""
    
    # 4. Combine all contexts
    all_context = []
    if rag_context:
        all_context.extend(rag_context)
    if drive_results:
        all_context.extend([result["content"] for result in drive_results])
    if web_context:
        all_context.append(web_context)
    
    combined_context = "\n\n".join(all_context)
    
    # 5. Enhanced prompt with citation instructions
    enhanced_prompt = PromptTemplate(
        template="""You are an advanced AI assistant with access to multiple knowledge sources.

Context from PDF documents:
{pdf_context}

Context from Google Drive:
{drive_context}

Context from web search:
{web_context}

User Question: {question}

Instructions:
1. Provide a comprehensive answer using information from all available sources
2. Include citation numbers [1], [2], [3] etc. in your response to reference sources
3. If you mention specific data, charts, or images, include the citation number
4. Prioritize recent information from Google Drive and web searches for current topics
5. Use PDF content for detailed technical information
6. Be specific about where each piece of information comes from

Answer with citations:""",
        input_variables=["pdf_context", "drive_context", "web_context", "question"]
    )
    
    # Prepare contexts
    pdf_context = "\n".join(rag_context) if rag_context else "No PDF context available"
    drive_context = "\n".join([r["content"] for r in drive_results]) if drive_results else "No Google Drive context available"
    
    # 6. Generate response
    prompt = enhanced_prompt.format(
        pdf_context=pdf_context,
        drive_context=drive_context,
        web_context=web_context if web_context else "No web context available",
        question=user_input
    )
    
    try:
        response = llm.invoke(prompt)
        answer_text = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        print(f"LLM generation failed: {e}")
        answer_text = f"I found relevant information from {len(citations)} sources, but couldn't generate a complete response. Please try rephrasing your question."
    
    # 7. Extract and validate citations in the response
    validated_citations = []
    citation_pattern = r'\[(\d+)\]'
    mentioned_citations = re.findall(citation_pattern, answer_text)
    
    for cited_num in mentioned_citations:
        try:
            idx = int(cited_num) - 1
            if 0 <= idx < len(citations):
                if citations[idx] not in validated_citations:
                    validated_citations.append(citations[idx])
        except (ValueError, IndexError):
            continue
    
    # Add any remaining citations that weren't mentioned
    for citation in citations:
        if citation not in validated_citations:
            validated_citations.append(citation)
    
    return {
        "response": answer_text,
        "citations": validated_citations,
        "sources_used": {
            "pdf_documents": len(rag_docs),
            "google_drive_docs": len(drive_results),
            "web_search": 1 if web_context else 0
        }
    }
