import asyncio
import os
import sys
import discord
from discord.ext import commands
from config import token

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db.database as db

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

cogs = [
    "cogs.general",
    "cogs.presence",
    "cogs.preferences",
    "cogs.matching",
]

async def main():
    async with bot:
        await db.create_pool()
        for cog in cogs:
            await bot.load_extension(cog)
        await bot.tree.sync()
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())