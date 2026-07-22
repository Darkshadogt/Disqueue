import urllib.parse
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

import db.database as db
from backend.auth_utils import create_access_token
from backend.config import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_REDIRECT_URI, FRONTEND_CALLBACK_URL

router = APIRouter(prefix="/auth", tags=["auth"])

DISCORD_OAUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"

def build_authorize_url(prompt: str | None = "none") -> str:
    encoded_redirect = urllib.parse.quote(DISCORD_REDIRECT_URI, safe="")
    params = (
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={encoded_redirect}"
        f"&response_type=code"
        f"&scope=identify+guilds"
    )
    if prompt:
        params += f"&prompt={prompt}"
    return DISCORD_OAUTH_URL + params


@router.get("/login")
async def login():
    # prompt=none: skip the consent screen for users who already authorized
    # Discord shows it on every login otherwise, which gets old fast
    return RedirectResponse(url=build_authorize_url(prompt="none"))


@router.get("/callback")
async def callback(code: str = None, error: str = None):
    if error:
        # prompt=none couldn't silently skip (first-time user, or the
        # user revoked access), fall back to a normal login that shows
        # the consent screen instead of failing outright
        return RedirectResponse(url=build_authorize_url(prompt=None))

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            DISCORD_TOKEN_URL,
            data={
                "client_id": DISCORD_CLIENT_ID,
                "client_secret": DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": DISCORD_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")

    token_data = token_response.json()
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_in = token_data["expires_in"]

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            DISCORD_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch Discord user")

    discord_user = user_response.json()
    user_id = discord_user["id"]
    username = discord_user["username"]
    avatar = discord_user["avatar"]

    await db.check_user(user_id)
    await db.update_user_profile(user_id, avatar)

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    await db.store_discord_tokens(user_id, access_token, refresh_token, expires_at)

    jwt_token = create_access_token(user_id, username)

    # Discord usernames can contain non-ASCII characters or symbols that
    # are unsafe in a raw query string (e.g. "&", "#", accented/CJK
    # characters), url-encode both before interpolating
    query = urllib.parse.urlencode({
        "access_token": jwt_token,
        "user_id": user_id,
        "username": username,
    })
    frontend_url = f"{FRONTEND_CALLBACK_URL}?{query}"

    return RedirectResponse(url=frontend_url)