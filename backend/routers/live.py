from fastapi import APIRouter, Depends
from backend.auth_utils import get_current_user
import db.database as db

router = APIRouter(prefix="/live", tags=["live"])


@router.get("")
async def get_live_sessions(user=Depends(get_current_user)):
    sessions = await db.get_all_active_sessions()
    return [
        {
            "user_id": session["user_id"],
            "game_name": session["game_name"],
            "started_at": session["started_at"].isoformat(),
        }
        for session in sessions
    ]