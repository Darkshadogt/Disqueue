from datetime import datetime, timedelta, timezone

import db.database as db
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from backend.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET

security = HTTPBearer()


def create_access_token(user_id: str, discord_username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,  # keep as string as Discord snowflakes exceed JS safe-integer range
        "username": discord_username,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_access_token(credentials.credentials)
    user_id = payload["sub"]
    user_profile = await db.get_user_profile(user_id)

    return {
        "user_id": user_id,
        "username": payload["username"],
        "avatar": user_profile["avatar"],
    }