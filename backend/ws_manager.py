from typing import Dict, Set
import json
from datetime import datetime, date
from fastapi import WebSocket

def _json_default(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(user_id, set()).add(ws)

    def disconnect(self, user_id: str, ws: WebSocket):
        conns = self.active.get(user_id)
        if conns:
            conns.discard(ws)
            if not conns:
                del self.active[user_id]

    async def send_to_user(self, user_id: str, message: dict):
        conns = self.active.get(user_id)
        if not conns:
            return
        await self._send(conns, message)

    async def broadcast(self, message: dict):
        # Every connected user, across all user IDs used for global state like live queue counts
        for conns in list(self.active.values()):
            await self._send(conns, message)

    async def _send(self, conns: Set[WebSocket], message: dict):
        payload = json.dumps(message, default=_json_default)
        dead = []
        for ws in conns:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            conns.discard(ws)

manager = ConnectionManager()