# Agentic RAG Chatbot Setup Instructions

## Features Included ✅

This system implements all the requested features:

1. **🎙️ Streaming Speech-to-Text (STT)** - Voice queries using OpenAI Whisper
2. **📄 MultiModal RAG** - Extract text and images from PDFs with OCR
3. **🤖 Agentic Query Processing** with:
   - a) RAG + Web Search Agent + MCP (Google Drive integration)
   - b) Citation/grounding showing source of answers
   - c) Click-to-view images from slides and website content

## Setup Steps

### 1. Get Google API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 2. Configure Environment Variables
Edit `backend/.env` file and replace `your_google_api_key_here` with your actual API key:
```
GOOGLE_API_KEY=your_actual_google_api_key_here
```

### 3. (Optional) Setup Google Drive MCP
To enable real Google Drive integration:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API
4. Create credentials (OAuth 2.0 client ID)
5. Download the JSON file and save as `backend/credentials.json`

**Note**: If you skip this step, the system will use a mock Google Drive client that simulates responses.

### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 5. Start the Backend Server
```bash
cd backend
python main.py
```
The backend will start on http://localhost:8001

### 6. Start the Frontend Server
```bash
cd frontend
npm run dev
```
The frontend will start on http://localhost:5173

## How to Use

### 1. Upload PDF Documents
- Click "Choose File" and select a PDF with text and images
- The system will extract text and images, perform OCR on images
- Wait for "PDF processed successfully" message

### 2. Query the System
You can query in three ways:

**A. Text Query**: Type your question and click "Ask"

**B. Voice Query**: Click "🎙️ Voice Query" button, speak for up to 10 seconds

**C. Voice File Upload**: Upload an audio file for transcription

### 3. View Results
The system will show:
- **Answer**: Generated response with citations [1], [2], etc.
- **Sources Used**: Summary of PDF documents, Google Drive docs, and web search
- **Citations**: Clickable source references with:
  - PDF pages with preview images
  - Google Drive documents with links
  - Web search results with URLs

### 4. Click Citations
- Click on citation images to view full-size PDF page screenshots
- Click on source links to open Google Drive docs or web pages

## System Architecture

### Backend (`/backend`)
- **FastAPI Server** (`main.py`) - REST API with CORS
- **RAG System** (`/rag`) - PDF processing, vector store, query engine
- **Speech-to-Text** (`/stt`) - Whisper-based audio transcription
- **Web Search Agent** (`/agents`) - DuckDuckGo search integration
- **Google Drive MCP** (`/mcp`) - Model Context Protocol for Google Drive

### Frontend (`/frontend`)
- **React + TypeScript** - Modern web interface
- **Components**:
  - `ChatBox.tsx` - Main chat interface with citations and image modals
  - `UploadPDF.tsx` - PDF upload with progress feedback
  - `VoiceMic.tsx` - Voice recording and query submission

## API Endpoints

- `POST /upload-pdf/` - Upload and process PDF documents
- `POST /query/` - Text-based queries
- `POST /voice-query/` - Voice-based queries (audio file)
- `POST /upload-audio/` - Audio transcription only
- `GET /image/{filename}` - Serve citation preview images
- `GET /health` - System health check

## Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY not found"**
   - Make sure you've set the API key in `backend/.env`

2. **Voice recording not working**
   - Check browser microphone permissions
   - Ensure you're using HTTPS or localhost

3. **PDF images not showing**
   - Check that `backend/images/` directory exists
   - Verify PDF was processed successfully

4. **Web search failing**
   - This is normal occasionally due to rate limiting
   - The system will still work with RAG and Google Drive

### Performance Notes

- First query after startup may be slow (loading AI models)
- Large PDFs (>50 pages) may take longer to process
- Voice queries require internet for Whisper processing

## Advanced Configuration

### Custom Whisper Model
In `backend/stt/streaming_stt.py`, change model size:
```python
# Options: tiny, base, small, medium, large
model = whisper.load_model("small")  # Better accuracy, slower
```

### Adjust Search Results
In `backend/rag/query_engine.py`, modify:
```python
# More RAG results
rag_docs = vectorstore.similarity_search(user_input, k=10)

# More web search results  
web_results = web_search_tool(user_input, max_results=5)
```

Your Agentic RAG system is now ready to use! 🚀
