from discord.ext import commands
from discord import app_commands
import discord
import copy

DEFAULT_PREFERENCES = {
    "global": {
        "enabled": False,
        "blocklist": [],
        "max_matches_per_day": 10,
        "recency_cooldown_hours": 2,
        "match_confirmation_required": False
    },
    "matching": {
        "playstyle": None,             # casual, competitive
    },
    "notifications": {
        "dm_enabled": True,
        "channel_ping_enabled": True,
        "friend_online_enabled": False
    },
    "time": {
        "quiet_hours_start": None,
        "quiet_hours_end": None,
        "play_hours_start": None,
        "play_hours_end": None,
        "available_days": ["mon","tue","wed","thu","fri","sat","sun"],
        "timezone": "UTC"
    },
    "profile": {
        "display_name": None,
        "bio": None,
        "language": "en",
        "region": None
    }
}

class Preferences(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.preferences = {}

    async def get_preferences(self, userID):
        if userID not in self.preferences:
            self.preferences[userID] = copy.deepcopy(DEFAULT_PREFERENCES)
        return self.preferences[userID]

    @app_commands.command(name="enable", description="Start receiving match notifications")
    async def enable(self, interaction):
        userID = interaction.user.id
        preferences = await self.get_preferences(userID)
        preferences["global"]["enabled"] = True
        await interaction.response.send_message("Matching enabled — you'll now be notified when someone's playing the same game as you.", ephemeral=True)

    @app_commands.command(name="disable", description="Stop receiving match notifications")
    async def disable(self, interaction):
        userID = interaction.user.id
        preferences = await self.get_preferences(userID)
        preferences["global"]["enabled"] = False
        await interaction.response.send_message("Matching disabled — you won't receive any match notifications.", ephemeral=True)
    
    @app_commands.command(name="block", description="Block a user from being matched with you")
    async def block(self, interaction, user : discord.Member):
        userID = interaction.user.id
        preferences = self.get_preferences(userID)
        
        if user.id == userID:
            await interaction.response.send_message("You can't block yourself.", ephemeral=True)
            return
        
        if user.id in preferences["global"]["blocklist"]:
            await interaction.response.send_message(f"{user.display_name} is already in your blocklist.", ephemeral=True)
            return
        
        preferences["global"]["blocklist"].append(user.id)
        await interaction.response.send_message(f"{user.display_name} has been added to your blocklist.", ephemeral=True)
    
    @app_commands.command(name="unblock", description="Unblock a user so they can be matched with you again")
    async def unblock(self, interaction: discord.Interaction, user: discord.Member):
        userID = interaction.user.id
        preferences = self.get_preferences(userID)

        if user.id not in preferences["global"]["blocklist"]:
            await interaction.response.send_message(f"{user.display_name} is not in your blocklist.", ephemeral=True)
            return

        preferences["global"]["blocklist"].remove(user.id)
        await interaction.response.send_message(f"{user.display_name} has been unblocked and can be matched with you again.", ephemeral=True)
    
    @app_commands.command(name="blockid", description="Block a user by their ID from being matched with you")
    async def blockID(self, interaction: discord.Interaction, ID: int):
        userID = interaction.user.id
        preferences = self.get_preferences(userID)

        if ID == userID:
            await interaction.response.send_message("You can't block yourself.", ephemeral=True)
            return

        if ID in preferences["global"]["blocklist"]:
            await interaction.response.send_message("That user is already blocked.", ephemeral=True)
            return

        try:
            user = await self.bot.fetch_user(ID)
        except discord.NotFound:
            await interaction.response.send_message("No Discord user found with that ID.", ephemeral=True)
            return

        preferences["global"]["blocklist"].append(ID)
        await interaction.response.send_message(f"{user.display_name} has been blocked.", ephemeral=True)


    @app_commands.command(name="unblockid", description="Unblock a user by their ID so they can be matched with you again")
    async def unblockID(self, interaction: discord.Interaction, ID: int):
        userID = interaction.user.id
        preferences = self.get_preferences(userID)

        if ID == userID:
            await interaction.response.send_message("You can't unblock yourself.", ephemeral=True)
            return

        if ID not in preferences["global"]["blocklist"]:
            await interaction.response.send_message("That user is not in your blocklist.", ephemeral=True)
            return

        try:
            user = await self.bot.fetch_user(ID)
        except discord.NotFound:
            # If ID exists in blocklist but user no longer exists on Discord,
            # still remove it from the blocklist
            preferences["global"]["blocklist"].remove(ID)
            await interaction.response.send_message("User removed from your blocklist.", ephemeral=True)
            return

        preferences["global"]["blocklist"].remove(ID)
        await interaction.response.send_message(f"{user.display_name} has been unblocked.", ephemeral=True)

    




        

async def setup(bot):
    await bot.add_cog(Preferences(bot))