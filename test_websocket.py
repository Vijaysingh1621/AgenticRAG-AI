import asyncio
import websockets
import json
import base64

async def test_websocket():
    uri = "ws://localhost:8000/ws/streaming-stt/test-client"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("🔗 Connected to WebSocket")
            
            # Wait for status message
            response = await websocket.recv()
            print(f"📩 Received: {response}")
            
            # Send a ping
            ping_message = {
                "type": "ping",
                "data": {"timestamp": "test"}
            }
            await websocket.send(json.dumps(ping_message))
            print("📤 Sent ping")
            
            # Wait for pong
            response = await websocket.recv()
            print(f"📩 Received: {response}")
            
            print("✅ WebSocket test successful")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
