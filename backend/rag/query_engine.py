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
    """Enhanced RAG with intelligent source selection based on query relevance"""
    
    # Initialize all sources
    vectorstore = load_chroma()
    drive_client = get_drive_client()
    
    # 1. Local RAG Search (always check first)
    rag_docs = vectorstore.similarity_search(user_input, k=k)
    rag_context = []
    citations = []
    
    # Calculate relevance score based on similarity
    pdf_relevance_score = 0
    if rag_docs:
        # Simple relevance check - if we have good matches from PDF
        for doc in rag_docs:
            # Check if the query terms appear in the retrieved content
            query_terms = user_input.lower().split()
            content_lower = doc.page_content.lower()
            matches = sum(1 for term in query_terms if term in content_lower)
            if matches > 0:
                pdf_relevance_score += matches / len(query_terms)
    
    # Normalize relevance score
    pdf_relevance_score = pdf_relevance_score / len(rag_docs) if rag_docs else 0
    
    print(f"📊 PDF relevance score: {pdf_relevance_score:.2f}")
    
    # Add PDF citations if relevant
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
    
    # 2. Intelligent Source Selection
    use_web_search = False
    use_drive_search = False
    
    # Determine if we need external sources
    if pdf_relevance_score < 0.3:  # Low relevance to PDF content
        print("🔍 Query not well-covered by PDF content, searching external sources...")
        use_web_search = True
        use_drive_search = True
    elif any(word in user_input.lower() for word in ["latest", "current", "recent", "update", "new", "today", "now"]):
        print("🔍 Query asks for current/recent info, checking external sources...")
        use_web_search = True
        use_drive_search = True
    elif any(word in user_input.lower() for word in ["news", "market", "price", "stock", "weather", "event"]):
        print("🔍 Query asks for real-time info, prioritizing web search...")
        use_web_search = True
    elif any(word in user_input.lower() for word in ["document", "file", "report", "my", "our", "company"]):
        print("🔍 Query asks for documents, checking Google Drive...")
        use_drive_search = True
    
    # 3. Google Drive MCP Search
    drive_results = []
    if use_drive_search:
        print("☁️ Searching Google Drive...")
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
    
    # 4. Web Search
    web_context = ""
    if use_web_search:
        print("🌐 Searching the web...")
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
    
    # 5. Combine all contexts
    all_context = []
    if rag_context:
        all_context.extend(rag_context)
    if drive_results:
        all_context.extend([result["content"] for result in drive_results])
    if web_context:
        all_context.append(web_context)
    
    combined_context = "\n\n".join(all_context)
    
    # 6. Enhanced prompt with intelligent source prioritization
    source_priority_note = ""
    if pdf_relevance_score < 0.3:
        source_priority_note = "Note: This query appears to be outside the scope of the uploaded PDF content. Focus on external sources (Google Drive and web search) for the answer."
    elif pdf_relevance_score > 0.7:
        source_priority_note = "Note: This query is well-covered by the PDF content. Use PDF information as the primary source, supplemented by external sources if needed."
    else:
        source_priority_note = "Note: This query partially relates to the PDF content. Combine information from all sources appropriately."
    
    enhanced_prompt = PromptTemplate(
        template="""You are an advanced AI assistant with access to multiple knowledge sources.

{source_priority}

Available Information:

PDF Documents: {pdf_context}

Google Drive: {drive_context}

Web Search: {web_context}

User Question: {question}

Instructions:
1. Answer the question using the most relevant and appropriate sources
2. If the query is NOT well-covered by PDF content, prioritize Google Drive and web search results
3. If the query asks for current/recent information, prioritize web search and Google Drive
4. Include citation numbers [1], [2], [3] etc. in your response to reference sources
5. If you mention specific data, charts, or images, include the citation number
6. Be specific about where each piece of information comes from
7. If information is not available in any source, clearly state this

Answer with citations:""",
        input_variables=["source_priority", "pdf_context", "drive_context", "web_context", "question"]
    )
    
    # Prepare contexts
    pdf_context = "\n".join(rag_context) if rag_context else "No PDF context available"
    drive_context = "\n".join([r["content"] for r in drive_results]) if drive_results else "No Google Drive context available"
    
    # 7. Generate response
    prompt = enhanced_prompt.format(
        source_priority=source_priority_note,
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
