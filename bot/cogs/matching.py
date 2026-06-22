from discord.ext import commands
import discord

class Matching(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    


async def setup(bot):
    await bot.add_cog(Matching(bot))