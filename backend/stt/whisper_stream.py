import asyncio
import websockets
import numpy as np
import io
from faster_whisper import WhisperModel
import soundfile as sf

model = WhisperModel("base")

async def transcribe_audio(websocket):
    buffer = io.BytesIO()
    
    while True:
        data = await websocket.recv()
        buffer.write(data)
        
        if len(data) < 3200:  # silence or pause
            buffer.seek(0)
            audio, sr = sf.read(buffer)
            segments, _ = model.transcribe(audio, beam_size=5)
            text = " ".join([seg.text for seg in segments])
            await websocket.send(text)
            buffer = io.BytesIO()

async def main():
    async with websockets.serve(transcribe_audio, "0.0.0.0", 8001):
        print("STT Server started at ws://localhost:8001")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
