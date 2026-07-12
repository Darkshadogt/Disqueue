import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from backend.config import (
    DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET,
    DISCORD_REDIRECT_URI,
)
from backend.auth_utils import create_access_token
import db.database as db

router = APIRouter(prefix="/auth", tags=["auth"])

DISCORD_OAUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"

@router.get("/login")
async def login():
    # Redirect user to Discord's OAuth2 authorization page
    params = (
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify"
    )
    return RedirectResponse(url=DISCORD_OAUTH_URL + params)


@router.get("/callback")
async def callback(code: str):
    # Exchange the authorization code Discord sent us for an access token
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

    # Use the Discord access token to fetch the user's profile
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            DISCORD_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch Discord user")

    discord_user = user_response.json()
    user_id = int(discord_user["id"])
    username = discord_user["username"]

    # Ensure user exists in our database
    await db.check_user(user_id)

    # Create a JWT session token for this user
    jwt_token = create_access_token(user_id, username)

    # In production this would redirect to the frontend with the token
    # For now return it directly so you can test with curl/Postman
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user_id": user_id,
        "username": username,
    }