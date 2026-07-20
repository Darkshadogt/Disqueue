import asyncio
import os
import sys
import discord
from discord.ext import commands
from config import token

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db.database as db

APPLICATION_ID = 1515863311307112558

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
    global synced

    # Prevent repeated syncs on reconnects
    if not synced:
        try:
            await bot.tree.sync()
            print("Commands synced.")
        except Exception as e:
            print(f"Sync failed: {e}")

        synced = True

    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

cogs = [
    "cogs.general",
    "cogs.presence",
    "cogs.preferences",
    "cogs.matching",
    "cogs.guild_events",
]

async def main():
    async with bot:
        await db.create_pool()
        for cog in cogs:
            await bot.load_extension(cog)
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
