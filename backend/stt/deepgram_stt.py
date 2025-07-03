"""
Simple Deepgram real-time streaming STT implementation
Clean and focused on just working with WebSocket
"""

import asyncio
import json
import os
import logging
from typing import Callable, Optional
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepgramStreamingSTT:
    """Simple real-time streaming STT using Deepgram API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        self.client = None
        self.is_connected = False
        self.callback = None
        
        if self.api_key:
            try:
                self.client = DeepgramClient(self.api_key)
                logger.info("✅ Deepgram client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Deepgram client: {e}")
                self.client = None
        else:
            logger.warning("⚠️ No Deepgram API key provided")
    
    def is_available(self) -> bool:
        """Check if Deepgram is available"""
        return self.client is not None and self.api_key is not None
    
    async def process_audio_chunk(self, audio_data: bytes, callback: Callable[[str], None]):
        """Process audio chunk with Deepgram"""
        if not self.is_available():
            logger.error("❌ Deepgram not available")
            return
        
        try:
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            # Use Deepgram prerecorded for chunk processing
            with open(tmp_path, 'rb') as audio_file:
                buffer_data = audio_file.read()
            
            payload = {"buffer": buffer_data}
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=True,
                punctuate=True,
                language="en-US"
            )
            
            response = self.client.listen.prerecorded.v("1").transcribe_file(payload, options)
            
            if response.results and response.results.channels:
                transcript = response.results.channels[0].alternatives[0].transcript
                if transcript and transcript.strip():
                    callback(transcript.strip())
                    logger.info(f"📝 Deepgram transcription: {transcript.strip()}")
            
            # Clean up temp file
            os.unlink(tmp_path)
            
        except Exception as e:
            logger.error(f"❌ Error processing audio chunk: {e}")


async def transcribe_audio_file_deepgram(file_path: str, api_key: Optional[str] = None) -> str:
    """Transcribe an audio file using Deepgram"""
    api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
    
    if not api_key:
        logger.warning("No Deepgram API key provided. Using Whisper fallback.")
        return await _fallback_whisper_transcription(file_path)
    
    try:
        deepgram = DeepgramClient(api_key)
        
        with open(file_path, 'rb') as audio_file:
            buffer_data = audio_file.read()
        
        payload = {"buffer": buffer_data}
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            punctuate=True,
            language="en-US"
        )
        
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        
        if response.results and response.results.channels:
            transcript = response.results.channels[0].alternatives[0].transcript
            logger.info(f"✅ Deepgram transcription: '{transcript}'")
            return transcript.strip()
        else:
            logger.warning("No transcription results from Deepgram")
            return ""
            
    except Exception as e:
        logger.error(f"❌ Deepgram transcription failed: {e}")
        return await _fallback_whisper_transcription(file_path)


async def _fallback_whisper_transcription(file_path: str) -> str:
    """Fallback transcription using Whisper"""
    try:
        import whisper
        from pydub import AudioSegment
        
        logger.info("🔄 Using Whisper fallback transcription")
        
        model = whisper.load_model("base")
        
        # Convert audio if needed
        try:
            audio_segment = AudioSegment.from_file(file_path)
            if audio_segment.channels > 1:
                audio_segment = audio_segment.set_channels(1)
            if audio_segment.frame_rate != 16000:
                audio_segment = audio_segment.set_frame_rate(16000)
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                audio_segment.export(tmp_file.name, format="wav")
                result = model.transcribe(tmp_file.name)
                transcription = result["text"].strip()
                os.unlink(tmp_file.name)
                return transcription
                
        except Exception as e:
            logger.error(f"❌ Whisper fallback failed: {e}")
            return ""
            
    except Exception as e:
        logger.error(f"❌ Whisper fallback transcription failed: {e}")
        return ""


def get_deepgram_status():
    """Get Deepgram service status"""
    api_key = os.getenv("DEEPGRAM_API_KEY")
    
    if not api_key:
        return {
            "available": False,
            "message": "No Deepgram API key found. Set DEEPGRAM_API_KEY environment variable.",
            "streaming_supported": False
        }
    
    try:
        client = DeepgramClient(api_key)
        return {
            "available": True,
            "message": "Deepgram API key is available",
            "streaming_supported": True
        }
    except Exception as e:
        return {
            "available": False,
            "message": f"Deepgram API key invalid: {e}",
            "streaming_supported": False
        }


# Backward compatibility
async def transcribe_audio_file(file_path: str, model_name: str = "nova-2") -> str:
    """Main transcription function"""
    return await transcribe_audio_file_deepgram(file_path)
