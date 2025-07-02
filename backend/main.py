from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from rag.pdf_processor import extract_text_from_pdf, extract_images_from_pdf
from rag.chroma_store import build_chroma
from rag.query_engine import query_rag
from stt.streaming_stt import transcribe_audio_file
import os
from pathlib import Path
import tempfile
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Agentic RAG Chatbot", description="Advanced RAG with STT, MultiModal, Web Search, and MCP")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
Path("temp").mkdir(exist_ok=True)
Path("images").mkdir(exist_ok=True)
Path("uploads").mkdir(exist_ok=True)

# Serve static files (images)
app.mount("/images", StaticFiles(directory="images"), name="images")

@app.get("/")
async def root():
    return {"message": "Agentic RAG Chatbot API", "features": ["STT", "MultiModal RAG", "Web Search", "MCP Google Drive"]}

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF with text and image extraction"""
    print(f"📄 Received PDF upload: {file.filename}")
    try:
        contents = await file.read()
        print(f"📄 Read {len(contents)} bytes from {file.filename}")
        
        # Ensure temp directory exists
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        pdf_path = f"temp/{file.filename}"
        with open(pdf_path, "wb") as f:
            f.write(contents)
        print(f"📄 Saved PDF to {pdf_path}")

        # Extract text and images
        print("📄 Starting text extraction...")
        text_chunks = extract_text_from_pdf(pdf_path)
        print(f"📄 Extracted {len(text_chunks)} text chunks")
        
        print("📄 Starting image extraction...")
        image_chunks = extract_images_from_pdf(pdf_path)
        print(f"📄 Extracted {len(image_chunks)} image chunks")
        
        # Merge OCR with text
        print("📄 Merging OCR with text...")
        for img in image_chunks:
            for txt in text_chunks:
                if img["page"] == txt["page"]:
                    txt["text"] += "\n" + img["ocr_text"]
                    txt["image"] = img["image_path"]
        
        # Build vector store
        print("📄 Building vector store...")
        build_chroma(text_chunks)
        print("📄 Vector store built successfully")
        
        return {
            "message": "PDF processed and embedded successfully",
            "pages_processed": len(text_chunks),
            "images_extracted": sum(len(img.get("extracted_images", [])) for img in image_chunks),
            "filename": file.filename
        }
    except Exception as e:
        import traceback
        print(f"❌ Error processing PDF: {str(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    """Upload audio file and transcribe using Whisper STT"""
    try:
        # Save uploaded audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        # Transcribe audio
        transcription = transcribe_audio_file(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return {
            "transcription": transcription,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

@app.post("/query/")
async def query_endpoint(query: str = Form(...)):
    """Query the enhanced RAG system with multiple knowledge sources"""
    try:
        result = query_rag(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/voice-query/")
async def voice_query(audio_file: UploadFile = File(...)):
    """Process voice query: transcribe audio then query RAG"""
    try:
        print(f"📁 Received audio file: {audio_file.filename}, size: {audio_file.size}, type: {audio_file.content_type}")
        
        # Validate audio file
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        # Save uploaded audio file with proper extension
        file_extension = ".wav"  # Default to wav
        if audio_file.content_type:
            if "webm" in audio_file.content_type:
                file_extension = ".webm"
            elif "mp4" in audio_file.content_type:
                file_extension = ".mp4"
            elif "ogg" in audio_file.content_type:
                file_extension = ".ogg"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        print(f"🎵 Audio saved to: {tmp_path}, size: {len(content)} bytes")
        
        # Transcribe audio
        try:
            transcription = transcribe_audio_file(tmp_path)
            print(f"📝 Transcription result: '{transcription}'")
        except Exception as transcribe_error:
            print(f"❌ Transcription failed: {transcribe_error}")
            os.unlink(tmp_path)
            raise HTTPException(status_code=500, detail=f"Audio transcription failed: {str(transcribe_error)}")
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Query RAG with transcription
        if transcription and transcription.strip():
            try:
                result = query_rag(transcription)
                result["transcription"] = transcription
                print(f"✅ Voice query completed successfully")
                return result
            except Exception as rag_error:
                print(f"❌ RAG query failed: {rag_error}")
                raise HTTPException(status_code=500, detail=f"Query processing failed: {str(rag_error)}")
        else:
            print("⚠️ No speech detected in audio file")
            return {
                "response": "No speech was detected in the audio file. Please try speaking more clearly or check your microphone.",
                "transcription": "",
                "citations": []
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Voice query error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing voice query: {str(e)}")

@app.get("/image/{filename}")
async def get_image(filename: str):
    """Serve images for citations"""
    image_path = Path("images") / filename
    if image_path.exists():
        return FileResponse(image_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")

@app.get("/health")
async def health_check():
    """Health check endpoint with service status"""
    
    # Check Google API key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    gemini_status = "✓" if google_api_key and google_api_key != "your_google_api_key_here" else "❌ Need API key"
    
    # Check Google Drive credentials
    drive_creds_exist = os.path.exists("credentials.json")
    drive_status = "✓ Real" if drive_creds_exist else "✓ Mock"
    
    # Check SerpAPI key
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    web_search_status = "✓ SerpAPI" if serpapi_key else "✓ DuckDuckGo"
    
    return {
        "status": "healthy" if gemini_status == "✓" else "needs_setup",
        "services": {
            "gemini_llm": gemini_status,
            "pdf_processing": "✓",
            "vector_store": "✓",
            "web_search": web_search_status,
            "google_drive_mcp": drive_status,
            "speech_to_text": "✓"
        },
        "setup_needed": [] if gemini_status == "✓" else ["Add GOOGLE_API_KEY to .env file"],
        "optional_enhancements": [
            "Google Drive credentials for real file access" if not drive_creds_exist else None,
            "SerpAPI key for enhanced web search" if not serpapi_key else None
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
