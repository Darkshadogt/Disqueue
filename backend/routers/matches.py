from fastapi import APIRouter, Depends
from backend.auth_utils import get_current_user
import db.database as db

router = APIRouter(prefix="/users", tags=["matches"])


@router.get("/me/matches")
async def get_match_history(user=Depends(get_current_user)):
    matches = await db.get_match_history(user["user_id"])
    return [
        {
            "user_id_1": match["user_id_1"],
            "user_id_2": match["user_id_2"],
            "game_name": match["game_name"],
            "matched_at": match["matched_at"].isoformat(),
        }
        for match in matches
    ]