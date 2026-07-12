from fastapi import APIRouter, HTTPException, Depends
from backend.auth_utils import get_current_user
import db.database as db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    # Returns the logged-in user's profile
    preferences = await db.get_preferences(user["user_id"])
    if preferences is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "display_name": preferences["display_name"],
        "bio": preferences["bio"],
        "language": preferences["language"],
        "region": preferences["region"],
    }


@router.get("/{user_id}")
async def get_user(user_id: int, user=Depends(get_current_user)):
    # Returns a specific user's public profile
    preferences = await db.get_preferences(user_id)
    if preferences is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user_id,
        "display_name": preferences["display_name"],
        "bio": preferences["bio"],
        "language": preferences["language"],
        "region": preferences["region"],
    }