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
    "cogs.preferences",
]


async def setup_hook():
    for cog in cogs:
        await bot.load_extension(cog)

    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash commands")


bot.setup_hook = setup_hook


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    for guild in bot.guilds:
        print(f"Connected to: {guild.name}")

async def main():
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())