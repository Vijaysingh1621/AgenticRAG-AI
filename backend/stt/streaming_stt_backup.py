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
        
        # Check file format first
        with open(file_path, 'rb') as f:
            header = f.read(12)
            print(f"� File header: {header[:4]} | Format: {header[8:12] if len(header) >= 12 else 'Unknown'}")
        
        # Try different approaches for audio loading
        try:
            # First try: Use librosa (most robust for different formats)
            import librosa
            print("🔄 Trying librosa for audio loading...")
            audio, sr = librosa.load(file_path, sr=16000)
            print(f"🎵 Loaded audio: {len(audio)} samples at {sr}Hz")
            
            # Ensure it's not empty
            if len(audio) == 0:
                raise Exception("Audio file appears to be empty")
            
            result = model.transcribe(audio)
            transcription = result["text"].strip()
            print(f"📝 Transcription (librosa): '{transcription}'")
            return transcription
            
        except Exception as librosa_error:
            print(f"⚠️ Librosa failed: {librosa_error}")
            
            # Second try: Use soundfile directly
            try:
                import soundfile as sf
                print("🔄 Trying soundfile for audio loading...")
                audio, sr = sf.read(file_path)
                print(f"🎵 Soundfile loaded: {len(audio)} samples at {sr}Hz")
                
                # Convert to mono if stereo
                if len(audio.shape) > 1:
                    audio = audio.mean(axis=1)
                    print("🔄 Converted stereo to mono")
                
                # Ensure it's not empty
                if len(audio) == 0:
                    raise Exception("Audio file appears to be empty")
                
                # Ensure sample rate is 16kHz for Whisper
                if sr != 16000:
                    import scipy.signal
                    audio = scipy.signal.resample(audio, int(len(audio) * 16000 / sr))
                    print(f"🔄 Resampled from {sr}Hz to 16000Hz")
                
                result = model.transcribe(audio.astype('float32'))
                transcription = result["text"].strip()
                print(f"📝 Transcription (soundfile): '{transcription}'")
                return transcription
                
            except Exception as sf_error:
                print(f"⚠️ Soundfile failed: {sf_error}")
                
                # Third try: Direct Whisper transcription (if FFmpeg available)
                try:
                    print("🔄 Trying direct Whisper transcription...")
                    result = model.transcribe(file_path)
                    transcription = result["text"].strip()
                    print(f"📝 Transcription (direct): '{transcription}'")
                    return transcription
                except Exception as whisper_error:
                    print(f"⚠️ Direct Whisper failed: {whisper_error}")
                    
                    # Fourth try: Convert with pydub (if available)
                    try:
                        print("🔄 Trying pydub conversion...")
                        from pydub import AudioSegment
                        
                        # Try to load with pydub (supports many formats)
                        audio_segment = AudioSegment.from_file(file_path)
                        
                        # Convert to WAV format
                        wav_path = file_path.replace(file_path.split('.')[-1], 'wav')
                        audio_segment.export(wav_path, format="wav")
                        print(f"🔄 Converted to WAV: {wav_path}")
                        
                        # Try librosa again with converted file
                        audio, sr = librosa.load(wav_path, sr=16000)
                        result = model.transcribe(audio)
                        transcription = result["text"].strip()
                        
                        # Clean up converted file
                        import os
                        if os.path.exists(wav_path):
                            os.unlink(wav_path)
                        
                        print(f"📝 Transcription (pydub): '{transcription}'")
                        return transcription
                        
                    except Exception as pydub_error:
                        print(f"⚠️ Pydub conversion failed: {pydub_error}")
                        
                        # Final try: Read as raw audio data
                        try:
                            print("🔄 Trying raw audio reading...")
                            import numpy as np
                            
                            with open(file_path, 'rb') as f:
                                raw_data = f.read()
                            
                            # Skip any headers and try to interpret as 16-bit audio
                            if len(raw_data) > 44:  # Skip typical WAV header
                                audio_data = raw_data[44:]
                            else:
                                audio_data = raw_data
                            
                            # Convert to numpy array (assuming 16-bit)
                            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                            
                            if len(audio_np) == 0:
                                raise Exception("No audio data found")
                            
                            print(f"🎵 Raw audio: {len(audio_np)} samples")
                            
                            result = model.transcribe(audio_np)
                            transcription = result["text"].strip()
                            print(f"📝 Transcription (raw): '{transcription}'")
                            return transcription
                            
                        except Exception as raw_error:
                            print(f"⚠️ Raw audio reading failed: {raw_error}")
                            raise Exception(f"All audio loading methods failed. Please ensure audio file is valid. Final error: {raw_error}")
                        
    except Exception as e:
        print(f"❌ Complete transcription failure: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        # Return a more helpful error message
        if "RIFF" in str(e):
            raise Exception("Audio format not supported. Please try recording again or use a different browser.")
        else:
            raise Exception(f"Audio transcription failed: {str(e)}")
