"""
Simple WebSocket endpoint for Deepgram streaming STT
Clean implementation that just works
"""

import asyncio
import json
import logging
import base64
import io
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from .deepgram_stt import DeepgramStreamingSTT, get_deepgram_status

logger = logging.getLogger(__name__)

class SimpleStreamingSTT:
    """Simple WebSocket handler for Deepgram STT"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.stt_instances: Dict[str, DeepgramStreamingSTT] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.connections[client_id] = websocket
        
        # Create STT instance
        stt = DeepgramStreamingSTT()
        self.stt_instances[client_id] = stt
        
        # Send status
        status = get_deepgram_status()
        await websocket.send_json({
            "type": "status",
            "data": status
        })
        
        logger.info(f"🔗 Client {client_id} connected")
    
    async def disconnect(self, client_id: str):
        """Clean up on disconnect"""
        if client_id in self.connections:
            del self.connections[client_id]
        
        if client_id in self.stt_instances:
            del self.stt_instances[client_id]
        
        logger.info(f"🔌 Client {client_id} disconnected")
    
    async def handle_message(self, client_id: str, message: Dict[str, Any]):
        """Handle WebSocket message"""
        try:
            message_type = message.get("type")
            websocket = self.connections.get(client_id)
            stt = self.stt_instances.get(client_id)
            
            if not websocket or not stt:
                return
            
            if message_type == "audio_chunk":
                # Process audio chunk
                audio_data = message.get("data", {}).get("audio")
                if audio_data:
                    try:
                        # Decode base64 audio
                        audio_bytes = base64.b64decode(audio_data)
                        
                        # Process with Deepgram
                        await stt.process_audio_chunk(audio_bytes, lambda text: 
                            asyncio.create_task(websocket.send_json({
                                "type": "transcription",
                                "data": {"text": text}
                            }))
                        )
                    except Exception as e:
                        logger.error(f"Error processing audio chunk: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": str(e)}
                        })
            
            elif message_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "data": {"timestamp": message.get("data", {}).get("timestamp")}
                })
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            if client_id in self.connections:
                try:
                    await self.connections[client_id].send_json({
                        "type": "error",
                        "data": {"message": str(e)}
                    })
                except:
                    pass


# Global instance
streaming_stt = SimpleStreamingSTT()


async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for streaming STT"""
    await streaming_stt.connect(websocket, client_id)
    
    try:
        while True:
            message = await websocket.receive_json()
            await streaming_stt.handle_message(client_id, message)
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await streaming_stt.disconnect(client_id)
