from fastapi import APIRouter, Depends

import db.database as db
from backend.auth_utils import get_current_user

router = APIRouter(prefix="/users", tags=["notifications"])


@router.get("/me/notifications")
async def get_my_notifications(user=Depends(get_current_user)):
    notifications = await db.get_notifications(user["user_id"])
    unread_count = await db.get_unread_count(user["user_id"])
    return {
        "unread_count": unread_count,
        "notifications": [
            {
                "id": notification["id"],
                "type": notification["type"],
                "title": notification["title"],
                "body": notification["body"],
                "read": notification["read"],
                "created_at": notification["created_at"].isoformat(),
            }
            for notification in notifications
        ],
    }


@router.patch("/me/notifications/{notification_id}/read")
async def mark_read(notification_id: int, user=Depends(get_current_user)):
    await db.mark_notification_read(user["user_id"], notification_id)
    return {"ok": True}


@router.post("/me/notifications/read-all")
async def mark_all_read(user=Depends(get_current_user)):
    await db.mark_all_notifications_read(user["user_id"])
    return {"ok": True}