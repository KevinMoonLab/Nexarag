from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    def disconnect_all(self):
        for connection in self.active_connections:
            connection.close()

    async def broadcast(self, event_type: str, data: Dict):
        message = {"type": event_type, "body": data}
        for connection in self.active_connections:
            await connection.send_json(message)