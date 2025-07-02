"""Debug script to test external query detection"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.rag.query_engine import is_external_query

# Test queries
test_queries = [
    "What is the weather in Tokyo today?",
    "What is the current Bitcoin price in USD?",
    "What content is in the uploaded document?",
    "Tell me about artificial intelligence",
    "Current temperature in London",
    "Show me the PDF content",
    "Latest news about technology",
    "What does this document say?"
]

print("🔍 Testing External Query Detection")
print("=" * 50)

for query in test_queries:
    is_external = is_external_query(query)
    result = "🌐 EXTERNAL" if is_external else "📄 INTERNAL/MIXED"
    print(f"{result}: '{query}'")

print("\n✅ External query detection test complete")
