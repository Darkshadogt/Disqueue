from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
from ..ws_manager import manager
from ..config import JWT_SECRET, JWT_ALGORITHM

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """
    Single realtime channel per authenticated user. The frontend never
    sends anything meaningful over this socket — it's push-only, used to
    notify the client of preference changes, new matches, and notification
    counts as they happen server-side. We still read incoming frames in a
    loop purely to detect disconnects (see WebSocketDisconnect below)
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload["sub"]
    except JWTError:
        await websocket.close(code=4001)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)