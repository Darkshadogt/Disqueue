import asyncio
import discord
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

async def main():
    async with bot:
        await db.create_pool()
        for cog in cogs:
            await bot.load_extension(cog)
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
