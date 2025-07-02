"""Direct test of query engine with external queries"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.rag.query_engine import query_rag

# Test external query directly
print("🔍 Testing Query Engine Directly")
print("=" * 50)

print("Test 1: Weather query (should be external)")
result1 = query_rag("What is the weather in Tokyo today?", k=3)
print(f"📊 PDF relevance score: {result1['relevance_info']['pdf_relevance_score']}")
print(f"📄 PDF chunks used: {result1['sources_used']['pdf_documents']}")
print(f"🌐 Web search used: {result1['sources_used']['web_search']}")
print(f"📋 Citation types: {set(c['type'] for c in result1['citations'])}")
print()

print("Test 2: Bitcoin query (should be external)")
result2 = query_rag("What is the current Bitcoin price in USD?", k=3)
print(f"📊 PDF relevance score: {result2['relevance_info']['pdf_relevance_score']}")
print(f"📄 PDF chunks used: {result2['sources_used']['pdf_documents']}")
print(f"🌐 Web search used: {result2['sources_used']['web_search']}")
print(f"📋 Citation types: {set(c['type'] for c in result2['citations'])}")
print()

print("Test 3: Document query (should be internal)")
result3 = query_rag("What content is in the uploaded document?", k=3)
print(f"📊 PDF relevance score: {result3['relevance_info']['pdf_relevance_score']}")
print(f"📄 PDF chunks used: {result3['sources_used']['pdf_documents']}")
print(f"🌐 Web search used: {result3['sources_used']['web_search']}")
print(f"📋 Citation types: {set(c['type'] for c in result3['citations'])}")
