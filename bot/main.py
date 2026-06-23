import asyncio
import discord
from discord.ext import commands
from config import token

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
cogs = [
    "cogs.general",
    "cogs.presence",
    "cogs.matching",
    "cogs.preferences"
]

async def main():
    async with bot:
        for cog in cogs:
            await bot.load_extension(cog)
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())