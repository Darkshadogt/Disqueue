from fastapi import APIRouter, HTTPException, Depends
from backend.auth_utils import get_current_user
import db.database as db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    user_id = user["user_id"]

    preferences = await db.get_preferences(user_id)
    userProfile = await db.get_user_profile(user_id)

    if preferences is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user_id,
        "username": user["username"],
        "display_name": preferences["display_name"],
        "avatar": userProfile["avatar"],
        "bio": preferences["bio"],
        "language": preferences["language"],
        "region": preferences["region"],
    }


@router.get("/{user_id}")
async def get_user(user_id: str, user=Depends(get_current_user)):
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
