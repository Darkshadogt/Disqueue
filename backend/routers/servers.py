import httpx
from fastapi import APIRouter, Depends, HTTPException
from backend.auth_utils import get_current_user
from backend.discord_oauth import get_valid_discord_token
from backend.config import DISCORD_TOKEN

router = APIRouter(prefix="/users", tags=["servers"])

DISCORD_API = "https://discord.com/api/v10"

MANAGE_GUILD = 0x20  # permission bit for "Manage Server"


def _raise_for_status_with_rate_limit(res: httpx.Response) -> None:
    # Discord's 429 has a JSON body with retry_after; surface that to the
    # client as a 503 instead of letting raise_for_status() turn a transient
    # rate limit into an opaque 500.
    if res.status_code == 429:
        retry_after = res.json().get("retry_after", 1)
        raise HTTPException(
            status_code=503,
            detail=f"Discord rate limit hit, try again in {retry_after:.1f}s",
        )
    res.raise_for_status()


@router.get("/me/servers")
async def get_my_linked_servers(user=Depends(get_current_user)):
    user_access_token = await get_valid_discord_token(user["user_id"])
    if user_access_token is None:
        raise HTTPException(status_code=401, detail="Discord session expired, please re-login.")

    async with httpx.AsyncClient() as client:
        # Guilds the bot is currently in
        bot_guilds_res = await client.get(
            f"{DISCORD_API}/users/@me/guilds",
            headers={"Authorization": f"Bot {DISCORD_TOKEN}"},
        )
        _raise_for_status_with_rate_limit(bot_guilds_res)
        bot_guild_ids = {guild["id"] for guild in bot_guilds_res.json()}

        # Guilds this user belongs to, with their permission flags
        user_guilds_res = await client.get(
            f"{DISCORD_API}/users/@me/guilds",
            headers={"Authorization": f"Bearer {user_access_token}"},
        )
        _raise_for_status_with_rate_limit(user_guilds_res)
        user_guilds = user_guilds_res.json()

    linked = [
        {
            "id": guild["id"],
            "name": guild["name"],
            "icon": guild["icon"],
            "is_admin": (int(guild["permissions"]) & MANAGE_GUILD) == MANAGE_GUILD,
        }
        for guild in user_guilds
        if guild["id"] in bot_guild_ids and (int(guild["permissions"]) & MANAGE_GUILD) == MANAGE_GUILD
    ]

    return linked