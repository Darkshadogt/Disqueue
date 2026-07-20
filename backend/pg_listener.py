import asyncio
import json
import os
import asyncpg
import db.database as db
from backend.ws_manager import manager

async def start_listener():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    async def handle_preferences(connection, pid, channel, payload):
        try:
            user_id = json.loads(payload)["user_id"]
        except (json.JSONDecodeError, KeyError):
            return
        fresh = await db.get_preferences(user_id)
        if fresh is None:
            return
        await manager.send_to_user(user_id, {"type": "preferences_updated", "data": dict(fresh)})

    async def handle_match_recorded(connection, pid, channel, payload):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return
        # Notify both participants, each fetches their own history on the frontend
        for uid in (data.get("user_id_1"), data.get("user_id_2")):
            if uid:
                await manager.send_to_user(uid, {"type": "match_recorded"})
    
    async def handle_notification_created(connection, pid, channel, payload):
        try:
            user_id = json.loads(payload)["user_id"]
        except (json.JSONDecodeError, KeyError):
            return
        unread_count = await db.get_unread_count(user_id)
        await manager.send_to_user(user_id, {
            "type": "notification_created",
            "unread_count": unread_count,
        })

    async def handle_live_session_change(connection, pid, channel, payload):
        # Global signal — every connected client refetches /live
        await manager.broadcast({"type": "live_session_changed"})

    await conn.add_listener("preferences_updated", handle_preferences)
    await conn.add_listener("match_recorded", handle_match_recorded)
    await conn.add_listener("live_session_changed", handle_live_session_change)
    await conn.add_listener("notification_created", handle_notification_created)

    return conn