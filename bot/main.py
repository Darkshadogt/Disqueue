import asyncio
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import discord
from aiohttp import web
from discord.ext import commands
from config import token, APPLICATION_ID
import db.database as db


intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(
    command_prefix="/",
    intents=intents,
    application_id=APPLICATION_ID
)

synced = False

@bot.event
async def on_ready():
    await bot.tree.clear_commands(guild=discord.Object(1515864853779054692))
    global synced

    # Prevent repeated syncs on reconnects
    if not synced:
        try:
            await bot.tree.sync()
            print("Commands synced.")
        except Exception as e:
            print(f"Sync failed: {e}")

        synced = True


cogs = [
    "cogs.general",
    "cogs.presence",
    "cogs.preferences",
    "cogs.matching",
    "cogs.guild_events",
]


async def health(request):
    return web.Response(text="ok")


async def start_health_server():
    app = web.Application()
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    async with bot:
        await db.create_pool()
        for cog in cogs:
            await bot.load_extension(cog)
        asyncio.create_task(start_health_server())
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())