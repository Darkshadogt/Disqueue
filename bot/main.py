import asyncio
import discord
from discord.ext import commands
from config import token

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.guild_commands_synced = False

cogs = [
    "cogs.general",
    "cogs.presence",
    "cogs.preferences",
    "cogs.matching",
]


async def setup_hook() -> None:
    for cog in cogs:
        await bot.load_extension(cog)

    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash commands")


bot.setup_hook = setup_hook


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")
    for guild in bot.guilds:
        print(f"Connected to: {guild.name}")

    if bot.guild_commands_synced:
        return

    for guild in bot.guilds:
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)

    bot.guild_commands_synced = True


@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)

async def main() -> None:
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())