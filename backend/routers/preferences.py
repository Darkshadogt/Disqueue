from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.auth_utils import get_current_user
import db.database as db

router = APIRouter(prefix="/users", tags=["preferences"])


@router.get("/me/preferences")
async def get_preferences(user=Depends(get_current_user)):
    preferences = await db.get_preferences(user["user_id"])
    if preferences is None:
        raise HTTPException(status_code=404, detail="User not found")
    blocklist = await db.get_blocklist(user["user_id"])
    return {
        "enabled": preferences["enabled"],
        "match_limit": preferences["match_limit"],
        "match_cooldown": preferences["match_cooldown"],
        "match_confirmation_required": preferences["match_confirmation_required"],
        "game_mode": preferences["game_mode"],
        "dm_enabled": preferences["dm_enabled"],
        "friend_online_enabled": preferences["friend_online_enabled"],
        "dnd_start": preferences["dnd_start"],
        "dnd_end": preferences["dnd_end"],
        "timezone": preferences["timezone"],
        "display_name": preferences["display_name"],
        "bio": preferences["bio"],
        "language": preferences["language"],
        "region": preferences["region"],
        "blocked_user_count": len(blocklist),
    }


class PreferencesUpdate(BaseModel):
    enabled: Optional[bool] = None
    match_limit: Optional[int] = None
    match_cooldown: Optional[int] = None
    match_confirmation_required: Optional[bool] = None
    game_mode: Optional[str] = None
    dm_enabled: Optional[bool] = None
    friend_online_enabled: Optional[bool] = None
    dnd_start: Optional[int] = None
    dnd_end: Optional[int] = None
    timezone: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None


@router.patch("/me/preferences")
async def update_preferences(
    body: PreferencesUpdate,
    user=Depends(get_current_user)
):
    # Only update fields that were actually provided in the request
    updates = body.model_dump(exclude_none=True)
    for column, value in updates.items():
        await db.update_preference(user["user_id"], column, value)
    return {"updated": list(updates.keys())}