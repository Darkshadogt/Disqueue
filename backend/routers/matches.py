from fastapi import APIRouter, Depends
from backend.auth_utils import get_current_user
import db.database as db

router = APIRouter(prefix="/users", tags=["matches"])


@router.get("/me/matches")
async def get_match_history(user=Depends(get_current_user)):
    user_id = user["user_id"]
    matches = await db.get_match_history(user_id)

    return [
        {
            "id": match["id"],
            "game_name": match["game_name"],
            "matched_at": match["matched_at"].isoformat(),
            "cross_server": match["cross_server"],
            "wait_time": match["my_wait_time"],
            "user_display_name": match["other_display_name"],
            "user_avatar": match["other_avatar"],
        }
        for match in matches
    ]