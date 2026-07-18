# backend/routers/servers.py
import httpx
from fastapi import APIRouter, Depends, HTTPException
from backend.auth_utils import get_current_user
import os

router = APIRouter(prefix="/users", tags=["servers"])

DISCORD_API = "https://discord.com/api/v10"
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

MANAGE_GUILD = 0x20  # permission bit for "Manage Server"


@router.get("/me/servers")
async def get_my_linked_servers(user=Depends(get_current_user)):
    user_access_token = user["discord_access_token"]  # from your OAuth session

    async with httpx.AsyncClient() as client:
        # Guilds the bot is currently in
        bot_guilds_res = await client.get(
            f"{DISCORD_API}/users/@me/guilds",
            headers={"Authorization": f"Bot {BOT_TOKEN}"},
        )
        bot_guilds_res.raise_for_status()
        bot_guild_ids = {g["id"] for g in bot_guilds_res.json()}

        # Guilds this user belongs to, with their permission flags
        user_guilds_res = await client.get(
            f"{DISCORD_API}/users/@me/guilds",
            headers={"Authorization": f"Bearer {user_access_token}"},
        )
        user_guilds_res.raise_for_status()
        user_guilds = user_guilds_res.json()

    linked = [
        {
            "id": g["id"],
            "name": g["name"],
            "icon": g["icon"],
            "is_admin": (int(g["permissions"]) & MANAGE_GUILD) == MANAGE_GUILD,
        }
        for g in user_guilds
        if g["id"] in bot_guild_ids and (int(g["permissions"]) & MANAGE_GUILD) == MANAGE_GUILD
    ]

    return linked