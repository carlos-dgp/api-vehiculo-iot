from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # Diccionario para mapear vehiculo_id a una lista de conexiones WebSocket activas
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, vehiculo_id: int, websocket: WebSocket):
        await websocket.accept()
        if vehiculo_id not in self.active_connections:
            self.active_connections[vehiculo_id] = []
        self.active_connections[vehiculo_id].append(websocket)

    def disconnect(self, vehiculo_id: int, websocket: WebSocket):
        if vehiculo_id in self.active_connections:
            if websocket in self.active_connections[vehiculo_id]:
                self.active_connections[vehiculo_id].remove(websocket)
            if not self.active_connections[vehiculo_id]:
                del self.active_connections[vehiculo_id]

    async def broadcast_to_vehicle(self, vehiculo_id: int, message: dict):
        if vehiculo_id in self.active_connections:
            for connection in self.active_connections[vehiculo_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()