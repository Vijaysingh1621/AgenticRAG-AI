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

def is_external_query(query: str) -> bool:
    """Determine if query is asking for external information not related to documents"""
    
    external_keywords = [
        # Weather
        "weather", "temperature", "climate", "rain", "snow", "sunny", "cloudy", "forecast",
        # Current events & news
        "news", "today", "current", "latest", "recent", "now", "happening",
        # Financial/Market
        "price", "stock", "market", "bitcoin", "cryptocurrency", "exchange", "trading", "usd", "eur", "dollar",
        # Geographic/Location
        "city", "country", "location", "map", "directions", "distance", "tokyo", "london", "paris", "new york",
        # Time-sensitive
        "time", "date", "schedule", "calendar", "when",
        # General knowledge
        "what is", "who is", "how to", "define", "meaning",
        # Real-time data
        "live", "real-time", "updates", "status", "current status"
    ]
    
    # Document-related keywords that suggest PDF relevance
    document_keywords = [
        "document", "pdf", "file", "page", "section", "chapter", "report",
        "uploaded", "this document", "the document", "according to", "mentioned",
        "content", "text", "written", "shows", "describes", "analysis"
    ]
    
    query_lower = query.lower()
    
    # Check for document keywords first - if found, it's likely document-related
    has_document_keywords = any(keyword in query_lower for keyword in document_keywords)
    if has_document_keywords:
        return False  # Likely document-related
    
    # Check for external keywords - if found and no document keywords, it's external
    has_external_keywords = any(keyword in query_lower for keyword in external_keywords)
    
    # Special check for very obvious external queries
    obvious_external_patterns = [
        "weather in", "temperature in", "price of", "cost of", "bitcoin", "cryptocurrency",
        "current", "today", "latest", "news about", "what happened", "live"
    ]
    
    is_obvious_external = any(pattern in query_lower for pattern in obvious_external_patterns)
    
    return has_external_keywords or is_obvious_external

def calculate_text_relevance(query: str, text: str, threshold: float = 0.2) -> float:
    """Calculate relevance score between query and text"""
    query_terms = query.lower().split()
    text_lower = text.lower()
    
    # Count matching terms
    matches = sum(1 for term in query_terms if term in text_lower)
    relevance = matches / len(query_terms) if query_terms else 0
    
    return relevance

def query_rag(user_input, k=5):
    """Enhanced RAG with intelligent source selection and relevance filtering"""
    
    # Initialize all sources
    vectorstore = load_chroma()
    drive_client = get_drive_client()
    
    # Pre-check: Is this an external query?
    is_external = is_external_query(user_input)
    print(f"🔍 Query type: {'External' if is_external else 'Mixed/Document'}")
    
    # 1. Local RAG Search with smart filtering
    rag_docs = []
    rag_context = []
    citations = []
    pdf_relevance_score = 0
    relevant_docs = []
    
    # Only search PDF if it's potentially relevant
    if not is_external:
        print("📄 Searching PDF documents...")
        rag_docs = vectorstore.similarity_search(user_input, k=k)
        
        if rag_docs:
            for doc in rag_docs:
                relevance = calculate_text_relevance(user_input, doc.page_content)
                if relevance > 0.2:  # Stricter threshold for mixed queries
                    relevant_docs.append((doc, relevance))
                    pdf_relevance_score += relevance
        
        # Normalize relevance score
        pdf_relevance_score = pdf_relevance_score / len(relevant_docs) if relevant_docs else 0
        
        print(f"📊 PDF relevance score: {pdf_relevance_score:.2f}")
        print(f"📄 Relevant PDF chunks: {len(relevant_docs)}/{len(rag_docs)}")
        
        # Add only relevant PDF citations
        for doc, relevance in relevant_docs:
            rag_context.append(doc.page_content)
            citation_num = len(citations) + 1
            citations.append({
                "citation": f"[{citation_num}]",
                "page": doc.metadata.get("page", "Unknown"),
                "image": doc.metadata.get("image_path", None),
                "type": "pdf",
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "relevance": relevance
            })
    else:
        print("📄 Skipping PDF search - query identified as external")
        pdf_relevance_score = 0
    
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
    
    # 3. Google Drive MCP Search with relevance filtering
    drive_results = []
    if use_drive_search:
        print("☁️ Searching Google Drive...")
        try:
            raw_drive_results = drive_client.search_and_retrieve(user_input, max_results=5)
            # Filter relevant Google Drive results
            for result in raw_drive_results:
                content = result.get("content", "")
                name = result.get("name", "")
                combined_text = f"{name} {content}"
                
                relevance = calculate_text_relevance(user_input, combined_text)
                if relevance > 0.1:  # Only include if at least 10% relevance
                    drive_results.append(result)
                    citation_num = len(citations) + 1
                    citations.append({
                        "citation": f"[{citation_num}]",
                        "page": "N/A",
                        "image": None,
                        "type": "google_drive",
                        "url": result.get("url", ""),
                        "content": content[:200] + "..." if len(content) > 200 else content,
                        "name": name,
                        "relevance": relevance
                    })
            print(f"☁️ Relevant Google Drive docs: {len(drive_results)}/{len(raw_drive_results)}")
        except Exception as e:
            print(f"Google Drive search failed: {e}")
    
    # 4. Web Search with relevance filtering
    web_context = ""
    if use_web_search:
        print("🌐 Searching the web...")
        try:
            web_results = web_search_tool(user_input)
            
            # Check if web results are relevant
            if web_results:
                web_relevance = calculate_text_relevance(user_input, web_results)
                if web_relevance > 0.1:  # Only include if relevant
                    web_context = web_results
                    citation_num = len(citations) + 1
                    citations.append({
                        "citation": f"[{citation_num}]",
                        "page": "N/A",
                        "image": None,
                        "type": "web",
                        "url": "https://duckduckgo.com",
                        "content": web_context[:200] + "..." if len(web_context) > 200 else web_context,
                        "relevance": web_relevance
                    })
                    print(f"🌐 Web search relevance: {web_relevance:.2f}")
                else:
                    print(f"🌐 Web results not relevant (score: {web_relevance:.2f})")
                    web_context = ""
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
            "pdf_documents": len(relevant_docs),  # Only count relevant PDF chunks
            "google_drive_docs": len(drive_results),  # Only count relevant Drive docs
            "web_search": 1 if web_context else 0  # Only count if web results are relevant
        },
        "relevance_info": {
            "pdf_relevance_score": pdf_relevance_score,
            "total_pdf_chunks_found": len(rag_docs),
            "relevant_pdf_chunks": len(relevant_docs),
            "relevant_drive_docs": len(drive_results),
            "web_search_used": bool(web_context)
        }
    }
