from discord.ext import commands
from discord import app_commands
import discord

class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))