from discord.ext import commands
from discord import app_commands
import discord

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        print(f"{after.name} updated their presence")

async def setup(bot):
    await bot.add_cog(Presence(bot))