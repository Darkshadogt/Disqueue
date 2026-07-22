import os
from datetime import datetime, timedelta, timezone

import httpx
import db.database as db

DISCORD_API = "https://discord.com/api/v10"
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

# Refresh a bit before actual expiry to avoid a token dying mid-request
REFRESH_BUFFER_SECONDS = 60


async def get_valid_discord_token(user_id: str) -> str | None:
    """
    Returns a currently-valid Discord OAuth access token for this user,
    refreshing it first if it's expired or about to expire. Returns None
    if the user has no stored tokens or the refresh token itself is invalid
    (in which case they need to log in again via /auth/login).
    """
    tokens = await db.get_discord_tokens(user_id)
    if tokens is None or tokens["discord_access_token"] is None:
        return None

    if tokens["discord_token_expires_at"] > datetime.now(timezone.utc) + timedelta(seconds=REFRESH_BUFFER_SECONDS):
        return tokens["discord_access_token"]

    if tokens["discord_refresh_token"] is None:
        return None

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{DISCORD_API}/oauth2/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": tokens["discord_refresh_token"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if res.status_code != 200:
        # Refresh token itself is invalid or expired so user needs to re-login
        return None

    data = res.json()
    new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])

    await db.store_discord_tokens(
        user_id,
        access_token=data["access_token"],
        # Discord doesn't always rotate the refresh token on refresh
        # so fall back to the existing one if a new one isn't returned
        refresh_token=data.get("refresh_token", tokens["discord_refresh_token"]),
        expires_at=new_expires_at,
    )

    return data["access_token"]