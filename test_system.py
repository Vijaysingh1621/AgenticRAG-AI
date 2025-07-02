#!/usr/bin/env python3
"""
Test script for Agentic RAG system
Run this to verify all components are working correctly
"""

import os
import sys
import requests
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

def test_environment():
    """Test environment setup"""
    print("🔧 Testing Environment Setup...")
    
    # Check if .env file exists
    env_file = Path("backend/.env")
    if not env_file.exists():
        print("❌ .env file not found in backend directory")
        return False
    
    # Check for Google API key
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key or google_api_key == "your_google_api_key_here":
        print("❌ GOOGLE_API_KEY not properly set in .env file")
        print("   Please get an API key from https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_imports():
    """Test if all required packages can be imported"""
    print("\n📦 Testing Package Imports...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "langchain",
        "langchain_community",
        "langchain_google_genai",
        "chromadb",
        "fitz",  # PyMuPDF
        "pytesseract",
        "PIL",   # Pillow
        "whisper",
        "speech_recognition",
        "google.generativeai",
        "duckduckgo_search"
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All packages imported successfully")
    return True

def test_backend_startup():
    """Test if backend can start without errors"""
    print("\n🚀 Testing Backend Components...")
    
    try:
        # Test individual components
        print("Testing PDF processor...")
        from rag.pdf_processor import extract_text_from_pdf
        
        print("Testing vector store...")
        from rag.chroma_store import load_chroma
        
        print("Testing query engine...")
        from rag.query_engine import query_rag
        
        print("Testing STT...")
        from stt.streaming_stt import transcribe_audio_file
        
        print("Testing web search...")
        from agents.web_search_agent import web_search_tool
        
        print("Testing Google Drive MCP...")
        from mcp.google_drive_client import get_drive_client
        drive_client = get_drive_client()
        
        print("✅ All backend components loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Backend component error: {e}")
        return False

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testing Directory Structure...")
    
    required_dirs = [
        "backend/temp",
        "backend/images", 
        "backend/uploads",
        "frontend/src",
        "frontend/src/components"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"🔄 Creating {dir_path}")
            path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure ready")
    return True

def test_frontend_deps():
    """Test frontend dependencies"""
    print("\n🌐 Testing Frontend Dependencies...")
    
    package_json = Path("frontend/package.json")
    if not package_json.exists():
        print("❌ frontend/package.json not found")
        return False
    
    node_modules = Path("frontend/node_modules")
    if not node_modules.exists():
        print("❌ Node modules not installed")
        print("   Run: cd frontend && npm install")
        return False
    
    print("✅ Frontend dependencies ready")
    return True

def run_quick_test():
    """Run a quick functionality test"""
    print("\n🧪 Running Quick Functionality Test...")
    
    try:
        # Test web search
        print("Testing web search...")
        from agents.web_search_agent import web_search_tool
        result = web_search_tool("artificial intelligence", max_results=1)
        if result and len(result) > 10:
            print("✅ Web search working")
        else:
            print("⚠️ Web search may have issues")
        
        # Test Google Drive MCP (will use mock if not configured)
        print("Testing Google Drive MCP...")
        from mcp.google_drive_client import get_drive_client
        drive_client = get_drive_client()
        mock_results = drive_client.search_and_retrieve("test", max_results=1)
        if mock_results:
            print("✅ Google Drive MCP working (using mock data)")
        
        # Test Whisper (just load model)
        print("Testing Whisper model loading...")
        import whisper
        model = whisper.load_model("base")
        print("✅ Whisper model loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧠 Agentic RAG System Test Suite")
    print("=" * 50)
    
    tests = [
        test_environment,
        test_imports, 
        test_directories,
        test_backend_startup,
        test_frontend_deps,
        run_quick_test
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your Agentic RAG system is ready to use!")
        print("\n🚀 To start the system:")
        print("1. Backend: cd backend && python main.py")
        print("2. Frontend: cd frontend && npm run dev")
        print("3. Open: http://localhost:5173")
    else:
        print("\n❌ Some tests failed. Please check the errors above and follow the setup instructions.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
