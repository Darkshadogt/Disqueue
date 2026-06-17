import discord
from discord.ext import commands
from config import token

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

bot.run(token)