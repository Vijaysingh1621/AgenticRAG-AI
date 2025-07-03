import speech_recognition as sr
import io
import wave
import threading
import queue
import time
from typing import Callable, Optional
import whisper
import tempfile
import os

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
        """Process audio from the queue"""
        while self.is_listening:
            try:
                # Get audio from queue with timeout
                audio = self.audio_queue.get(timeout=1)
                
                # Convert audio to numpy array
                audio_data = audio.get_wav_data()
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name
                
                # Transcribe
                result = self.whisper_model.transcribe(tmp_path)
                text = result['text'].strip()
                
                # Clean up
                os.unlink(tmp_path)
                
                # Call callback if we have text
                if text and self.callback:
                    self.callback(text)
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
                continue

def transcribe_audio_file(file_path: str, model_name: str = "base") -> str:
    """Transcribe an uploaded audio file with robust WebM/format handling"""
    try:
        print(f"🎵 Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name)
        
        print(f"🎤 Transcribing audio file: {file_path}")
        
        # Check file format first
        with open(file_path, 'rb') as f:
            header = f.read(12)
            print(f"🔍 File header: {header[:4]} | Format: {header[8:12] if len(header) >= 12 else 'Unknown'}")
        
        # Keep track of converted files for cleanup
        converted_files = []
        
        try:
            # First try: Convert with pydub (supports most formats including WebM)
            print("🔄 Trying pydub conversion...")
            from pydub import AudioSegment
            
            # Try to load with pydub (supports many formats including WebM)
            audio_segment = AudioSegment.from_file(file_path)
            print(f"🎵 Loaded with pydub: {len(audio_segment)}ms, channels={audio_segment.channels}, frame_rate={audio_segment.frame_rate}")
            
            # Convert to mono if stereo
            if audio_segment.channels > 1:
                audio_segment = audio_segment.set_channels(1)
                print("🔄 Converted to mono")
            
            # Convert to 16kHz
            if audio_segment.frame_rate != 16000:
                audio_segment = audio_segment.set_frame_rate(16000)
                print("🔄 Converted to 16kHz")
            
            # Create a temporary WAV file with proper cleanup
            wav_fd, wav_path = tempfile.mkstemp(suffix='.wav')
            converted_files.append(wav_path)
            
            # Export to WAV
            audio_segment.export(wav_path, format="wav")
            os.close(wav_fd)  # Close the file descriptor immediately
            print(f"🔄 Converted to WAV: {wav_path}")
            
            # Use Whisper to transcribe the converted file
            result = model.transcribe(wav_path)
            transcription = result["text"].strip()
            print(f"📝 Transcription (pydub): '{transcription}'")
            
            # Clean up converted files
            for temp_file in converted_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        print(f"🗑️ Cleaned up: {temp_file}")
                except Exception as cleanup_error:
                    print(f"⚠️ Cleanup failed for {temp_file}: {cleanup_error}")
            
            return transcription
            
        except Exception as pydub_error:
            print(f"⚠️ Pydub conversion failed: {pydub_error}")
            
            # Clean up any converted files
            for temp_file in converted_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception:
                    pass
            converted_files.clear()
            
            # Second try: Use librosa (good for various formats)
            try:
                print("🔄 Trying librosa...")
                import librosa
                audio, sr = librosa.load(file_path, sr=16000)
                print(f"🎵 Loaded with librosa: {len(audio)} samples, sr={sr}")
                
                # Ensure it's not empty
                if len(audio) == 0:
                    raise Exception("Audio file appears to be empty")
                
                result = model.transcribe(audio)
                transcription = result["text"].strip()
                print(f"📝 Transcription (librosa): '{transcription}'")
                return transcription
                
            except Exception as librosa_error:
                print(f"⚠️ Librosa failed: {librosa_error}")
                
                # Third try: Use soundfile
                try:
                    print("🔄 Trying soundfile...")
                    import soundfile as sf
                    audio, sr = sf.read(file_path)
                    print(f"🎵 Loaded with soundfile: {len(audio)} samples, sr={sr}")
                    
                    # Convert to mono if stereo
                    if len(audio.shape) > 1:
                        audio = audio.mean(axis=1)
                        print("🔄 Converted to mono")
                    
                    # Resample if needed
                    if sr != 16000:
                        import librosa
                        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
                        print(f"🔄 Resampled to 16kHz")
                    
                    result = model.transcribe(audio)
                    transcription = result["text"].strip()
                    print(f"📝 Transcription (soundfile): '{transcription}'")
                    return transcription
                    
                except Exception as soundfile_error:
                    print(f"⚠️ Soundfile failed: {soundfile_error}")
                    
                    # Fourth try: Direct Whisper loading
                    try:
                        print("🔄 Trying direct Whisper...")
                        result = model.transcribe(file_path)
                        transcription = result["text"].strip()
                        print(f"📝 Transcription (direct): '{transcription}'")
                        return transcription
                    except Exception as whisper_error:
                        print(f"⚠️ Direct Whisper failed: {whisper_error}")
                        
                        # Final try: FFmpeg conversion via pydub
                        try:
                            print("🔄 Trying FFmpeg conversion...")
                            from pydub import AudioSegment
                            from pydub.utils import which
                            
                            # Check if FFmpeg is available
                            if which("ffmpeg") is None:
                                raise Exception("FFmpeg not found")
                            
                            # Force pydub to use FFmpeg for WebM conversion
                            audio_segment = AudioSegment.from_file(file_path, format="webm")
                            
                            # Convert to WAV format
                            wav_fd, wav_path = tempfile.mkstemp(suffix='.wav')
                            converted_files.append(wav_path)
                            
                            # Export to WAV
                            audio_segment.export(wav_path, format="wav")
                            os.close(wav_fd)  # Close the file descriptor immediately
                            print(f"🔄 FFmpeg converted to WAV: {wav_path}")
                            
                            # Use Whisper to transcribe the converted file
                            result = model.transcribe(wav_path)
                            transcription = result["text"].strip()
                            print(f"📝 Transcription (FFmpeg): '{transcription}'")
                            
                            # Clean up converted files
                            for temp_file in converted_files:
                                try:
                                    if os.path.exists(temp_file):
                                        os.unlink(temp_file)
                                except Exception:
                                    pass
                            
                            return transcription
                            
                        except Exception as ffmpeg_error:
                            print(f"⚠️ FFmpeg conversion failed: {ffmpeg_error}")
                            raise Exception(f"All audio loading methods failed. Please ensure audio file is valid. Final error: {ffmpeg_error}")
                        
    except Exception as e:
        # Clean up any converted files
        for temp_file in converted_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass
        
        print(f"❌ Complete transcription failure: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        # Return a more helpful error message
        if "RIFF" in str(e):
            raise Exception("Audio format not supported. Please try recording again or use a different browser.")
        elif "buffer size" in str(e):
            raise Exception("Audio format conversion failed. Please try recording in a different format (WAV recommended).")
        else:
            raise Exception(f"Audio transcription failed: {str(e)}")

def transcribe_audio_stream(audio_data: bytes, model_name: str = "base") -> str:
    """Transcribe audio data from a stream"""
    try:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        # Transcribe using file method
        result = transcribe_audio_file(tmp_path, model_name)
        
        # Clean up
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        print(f"❌ Stream transcription failed: {e}")
        raise Exception(f"Stream transcription failed: {str(e)}")
