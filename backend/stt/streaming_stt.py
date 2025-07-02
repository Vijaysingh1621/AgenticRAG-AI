import speech_recognition as sr
import io
import wave
import threading
import queue
import time
from typing import Callable, Optional
import whisper

class StreamingSTT:
    def __init__(self, model_name="base"):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.callback = None
        self.whisper_model = whisper.load_model(model_name)
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def start_listening(self, callback: Callable[[str], None]):
        """Start continuous listening and call callback with transcribed text"""
        self.callback = callback
        self.is_listening = True
        
        # Start background listening
        self.stop_listening = self.recognizer.listen_in_background(
            self.microphone, 
            self._audio_callback,
            phrase_time_limit=5
        )
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_audio)
        self.processing_thread.start()
    
    def stop_listening_stream(self):
        """Stop the listening stream"""
        self.is_listening = False
        if hasattr(self, 'stop_listening'):
            self.stop_listening(wait_for_stop=False)
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join()
    
    def _audio_callback(self, recognizer, audio):
        """Callback for when audio is captured"""
        if self.is_listening:
            self.audio_queue.put(audio)
    
    def _process_audio(self):
        """Process audio from the queue using Whisper"""
        while self.is_listening:
            try:
                audio = self.audio_queue.get(timeout=1)
                
                # Convert audio to format Whisper expects
                wav_data = io.BytesIO(audio.get_wav_data())
                
                # Use Whisper for transcription
                with wave.open(wav_data, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    sample_rate = wav_file.getframerate()
                    
                    # Convert to numpy array for Whisper
                    import numpy as np
                    audio_np = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # Transcribe with Whisper
                    result = self.whisper_model.transcribe(audio_np)
                    text = result["text"].strip()
                    
                    if text and self.callback:
                        self.callback(text)
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
                continue

def transcribe_audio_file(file_path: str, model_name: str = "base") -> str:
    """Transcribe an uploaded audio file"""
    try:
        print(f"🎵 Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name)
        
        print(f"🎤 Transcribing audio file: {file_path}")
        result = model.transcribe(file_path)
        
        transcription = result["text"].strip()
        print(f"📝 Transcription: '{transcription}'")
        
        return transcription
    except Exception as e:
        print(f"❌ Whisper transcription error: {e}")
        # Try alternative approach for different audio formats
        try:
            import librosa
            print("🔄 Trying librosa for audio loading...")
            audio, sr = librosa.load(file_path, sr=16000)
            result = model.transcribe(audio)
            return result["text"].strip()
        except Exception as librosa_error:
            print(f"❌ Librosa fallback failed: {librosa_error}")
            raise Exception(f"Audio transcription failed. Original error: {e}")
