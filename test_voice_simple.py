#!/usr/bin/env python3
"""
Test voice functionality with a simple synthetic audio file
"""

import os
import requests
import numpy as np
import wave
import tempfile

def create_test_audio():
    """Create a simple test audio file with tone"""
    # Generate a simple sine wave
    duration = 2  # seconds
    sample_rate = 16000
    frequency = 440  # A note
    
    t = np.linspace(0, duration, duration * sample_rate, False)
    audio = np.sin(frequency * 2 * np.pi * t)
    
    # Convert to 16-bit integers
    audio = (audio * 32767).astype(np.int16)
    
    # Save as WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        with wave.open(temp_file.name, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio.tobytes())
        
        return temp_file.name

def test_voice_endpoint():
    """Test the voice query endpoint"""
    print("🎵 Creating test audio file...")
    audio_file = create_test_audio()
    
    try:
        print("📤 Sending test audio to /voice-query/...")
        with open(audio_file, 'rb') as f:
            files = {'audio_file': ('test_audio.wav', f, 'audio/wav')}
            response = requests.post('http://localhost:8001/voice-query/', files=files, timeout=30)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Voice query successful!")
            print(f"   Transcription: '{result.get('transcription', 'None')}'")
            print(f"   Response length: {len(result.get('response', ''))}")
            return True
        else:
            print(f"❌ Voice query failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(audio_file):
            os.unlink(audio_file)

if __name__ == "__main__":
    success = test_voice_endpoint()
    if success:
        print("\n🎉 Voice functionality is working!")
    else:
        print("\n❌ Voice functionality needs attention.")
