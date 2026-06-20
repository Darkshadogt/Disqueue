from discord.ext import commands
from discord import app_commands
import discord

class General(commands.cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Checks if bot online")
    async def ping(self, interaction):
        await interaction.response.send_message("Pong!")
    

async def setup(bot):
    await bot.add_cog(General(bot))