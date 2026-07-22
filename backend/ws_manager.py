import json
from datetime import date, datetime
from typing import Dict, Set

from fastapi import WebSocket


def _json_default(obj):
    """json.dumps() doesn't know how to serialize datetime/date objects
    that come straight out of asyncpg rows — this teaches it to"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


class ConnectionManager:
    """
    Tracks active websocket connections per user. A user can have more
    than one open connection (multiple tabs/devices), so each user_id
    maps to a set of sockets rather than a single one
    """

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
        # Every connected user, across all user IDs, used for global
        # state like live queue counts that every client needs to refresh
        for conns in list(self.active.values()):
            await self._send(conns, message)

    async def _send(self, conns: Set[WebSocket], message: dict):
        payload = json.dumps(message, default=_json_default)
        dead = []
        for ws in conns:
            try:
                await ws.send_text(payload)
            except Exception:
                # Connection is gone but hasn't triggered onclose yet
                # drop it here instead of waiting for the next disconnect
                dead.append(ws)
        for ws in dead:
            conns.discard(ws)


manager = ConnectionManager()