from discord.ext import commands
from discord import app_commands
import discord
import copy
from typing import Optional, Literal

DEFAULT_PREFERENCES = {
    "global": {
        "enabled": False,
        "blocklist": [],
        "match_limit": None,
        "match_cooldown": 2, # in minutes
        "match_confirmation_required": True
    },
    "matching": {
        "game_mode": "any", # casual, ranked, any
    },
    "notifications": {
        "dm_enabled": False,
        "friend_online_enabled": False
    },
    "time": {
        "dnd_start": None,
        "dnd_end": None,
        "timezone": "UTC"
    },
    "profile": {
        "display_name": None,
        "bio": None,
        "language": None,
        "region": None
    }
}

TIMEZONES = [
    app_commands.Choice(name="UTC", value="utc"),
    app_commands.Choice(name="EST", value="est"),
    app_commands.Choice(name="CST", value="cst"),
    app_commands.Choice(name="MST", value="mst"),
    app_commands.Choice(name="PST", value="pst"),
    app_commands.Choice(name="AKST", value="akst"),
    app_commands.Choice(name="HST", value="hst"),
    app_commands.Choice(name="GMT", value="gmt"),
    app_commands.Choice(name="CET", value="cet"),
    app_commands.Choice(name="IST", value="ist"),
    app_commands.Choice(name="JST", value="jst"),
    app_commands.Choice(name="AEST", value="aest"),
]

MODES = [
    app_commands.Choice(name="Casual", value="casual"),
    app_commands.Choice(name="Ranked", value="ranked"),
    app_commands.Choice(name="Any", value="any"),
]

HOURS = [
    app_commands.Choice(name=f"{h:02d}:00", value=str(h))
    for h in range(24)
]

LANGUAGES = [
    app_commands.Choice(name="English", value="en"),
    app_commands.Choice(name="Spanish", value="es"),
    app_commands.Choice(name="French", value="fr"),
    app_commands.Choice(name="German", value="de"),
    app_commands.Choice(name="Japanese", value="ja"),
    app_commands.Choice(name="Korean", value="ko"),
    app_commands.Choice(name="Portuguese", value="pt"),
    app_commands.Choice(name="Chinese", value="zh"),
]

REGIONS = [
    app_commands.Choice(name="North America", value="na"),
    app_commands.Choice(name="Europe", value="eu"),
    app_commands.Choice(name="Asia", value="asia"),
    app_commands.Choice(name="South America", value="sa"),
    app_commands.Choice(name="Oceania", value="oce"),
    app_commands.Choice(name="Middle East", value="me"),
]

class Preferences(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.preferences = {}

    def get_preferences(self, userID: int) -> dict:
        if userID not in self.preferences:
            self.preferences[userID] = copy.deepcopy(DEFAULT_PREFERENCES)
        return self.preferences[userID]

    @app_commands.command(name="reset", description="Reset your user preferences")
    async def reset(self, interaction: discord.Interaction) -> None:
        userID = interaction.user.id
        self.preferences[userID] = copy.deepcopy(DEFAULT_PREFERENCES)
        await interaction.response.send_message("Your preferences has been reset.", ephemeral=True)

    @app_commands.command(name="preferences", description="View your current preferences")
    async def viewPreferences(self, interaction: discord.Interaction) -> None:
        userID = interaction.user.id
        preferences = self.get_preferences(userID)
        dndStart = preferences['time']['dnd_start']
        dndEnd = preferences['time']['dnd_end']
        dndDisplay = f"{int(dndStart):02d}:00 - {int(dndEnd):02d}:00" if dndStart and dndEnd else "Not set"
        
        embed = discord.Embed(title="Your Preferences", color=discord.Color.blue())
        
        embed.add_field(name="Global", value=
            f"Enabled: {preferences['global']['enabled']}\n"
            f"Match Limit: {preferences['global']['match_limit'] or 'None'}\n"
            f"Cooldown: {preferences['global']['match_cooldown']} min\n"
            f"Confirmation: {preferences['global']['match_confirmation_required']}\n"
            f"Blocked Users: {len(preferences['global']['blocklist'])}",
            inline=True)
        
        embed.add_field(name="Notifications", value=
            f"DMs: {preferences['notifications']['dm_enabled']}\n"
            f"Friend Pings: {preferences['notifications']['friend_online_enabled']}",
            inline=True)
        
        embed.add_field(
            name="Time",
            value=(
                f"Timezone: {preferences['time']['timezone'].upper()}\n"
                f"DND: {dndDisplay}"
            )
        )

        embed.add_field(name="Profile", value=
            f"Name: {preferences['profile']['display_name'] or 'Not set'}\n"
            f"Bio: {preferences['profile']['bio'] or 'Not set'}\n"
            f"Language: {preferences['profile']['language'] or 'Not set'}\n"
            f"Region: {preferences['profile']['region'] or 'Not set'}",
            inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="enable", description="Start receiving match notifications")
    async def enable(self, interaction: discord.Interaction) -> None:
         userID = interaction.user.id
         preferences = self.get_preferences(userID)

         await interaction.response.defer(ephemeral=True)

         # Try sending a test DM to verify user can receive messages
         try:
            user = await self.bot.fetch_user(userID)
            await user.send("Your DMs are open — you're all set to receive match notifications from Disqueue!")
         except discord.Forbidden:
            await interaction.followup.send(
                "Error: Could not enable matching — your DMs are closed. Please open your DMs and try again.\n"
                "To open DMs: **User Settings → Privacy & Safety → Allow direct messages from server members**",
                ephemeral=True
            )
            return

         preferences["global"]["enabled"] = True
         preferences["notifications"]["dm_enabled"] = True
         await interaction.followup.send(
            "Matching enabled — we sent you a DM to confirm everything is working.",
            ephemeral=True
         )

    @app_commands.command(name="disable", description="Stop receiving match notifications")
    async def disable(self, interaction: discord.Interaction) -> None:
        userID = interaction.user.id
        preferences = self.get_preferences(userID)
        preferences["global"]["enabled"] = False
        preferences["notifications"]["dm_enabled"] = False
        await interaction.response.send_message("Matching disabled — you won't receive any match notifications.", ephemeral=True)
    
    @app_commands.command(name="block", description="Block a user from being matched with you")
    async def block(self, interaction: discord.Interaction, user: discord.Member) -> None:
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
    async def unblock(self, interaction: discord.Interaction, user: discord.Member) -> None:
        userID = interaction.user.id
        preferences = self.get_preferences(userID)

        if user.id not in preferences["global"]["blocklist"]:
            await interaction.response.send_message(f"{user.display_name} is not in your blocklist.", ephemeral=True)
            return

        preferences["global"]["blocklist"].remove(user.id)
        await interaction.response.send_message(f"{user.display_name} has been unblocked and can be matched with you again.", ephemeral=True)
    
    @app_commands.command(name="blockid", description="Block a user by their ID from being matched with you")
    async def blockID(self, interaction: discord.Interaction, user_id: int) -> None:
        userID = interaction.user.id
        preferences = self.get_preferences(userID)

        if user_id == userID:
            await interaction.response.send_message("You can't block yourself.", ephemeral=True)
            return

        if user_id in preferences["global"]["blocklist"]:
            await interaction.response.send_message("That user is already blocked.", ephemeral=True)
            return

        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await interaction.response.send_message("No Discord user found with that ID.", ephemeral=True)
            return

        preferences["global"]["blocklist"].append(user_id)
        await interaction.response.send_message(f"{user.display_name} has been blocked.", ephemeral=True)


    @app_commands.command(name="unblockid", description="Unblock a user by their ID so they can be matched with you again")
    async def unblockID(self, interaction: discord.Interaction, user_id: int) -> None:
        userID = interaction.user.id
        preferences = self.get_preferences(userID)

        if user_id == userID:
            await interaction.response.send_message("You can't unblock yourself.", ephemeral=True)
            return

        if user_id not in preferences["global"]["blocklist"]:
            await interaction.response.send_message("That user is not in your blocklist.", ephemeral=True)
            return

        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            # If ID exists in blocklist but user no longer exists on Discord,
            # still remove it from the blocklist
            preferences["global"]["blocklist"].remove(user_id)
            await interaction.response.send_message("User removed from your blocklist.", ephemeral=True)
            return

        preferences["global"]["blocklist"].remove(user_id)
        await interaction.response.send_message(f"{user.display_name} has been unblocked.", ephemeral=True)

    @app_commands.command(name="set-match-limit", description="Sets the number of matches a user can be matched in a day (Leave matches blank to remove limit)")
    async def setMatchLimit(self, interaction: discord.Interaction, limit: Optional[int] = None) -> None:
        userID = interaction.user.id
        preferences = self.get_preferences(userID)

        if limit is not None and limit <= 0:
            await interaction.response.send_message("Limit must be a positive number.", ephemeral=True)
            return

        preferences["global"]["match_limit"] = limit

        if limit is None:
            await interaction.response.send_message("Match limit removed — no daily limit set.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Match limit set to {limit} per day.", ephemeral=True)
    
    @app_commands.command(name="set-match-cooldown", description="Sets the cooldown time before a user can be matched again")
    async def setMatchCooldown(self, interaction: discord.Interaction, time: Optional[int] = None) -> None:
        userID = interaction.user.id
        preferences = self.get_preferences(userID)

        if time is not None and time <= 2:
            await interaction.response.send_message("Cooldown must be at least default cooldown time.", ephemeral=True)
            return

        if time is None:
            preferences["global"]["match_cooldown"] = DEFAULT_PREFERENCES["global"]["match_cooldown"]
            await interaction.response.send_message("Match cooldown reset to the default value.", ephemeral=True)
            return

        preferences["global"]["match_cooldown"] = time
        await interaction.response.send_message(f"Match cooldown set to {time} minutes.", ephemeral=True)

    @app_commands.command(name="match-confirmation", description="Toggle whether you confirm or auto-accept matches")
    async def matchConfirmation(self, interaction: discord.Interaction, setting: Literal["on", "off"]) -> None:
        userID = interaction.user.id
        preferences = self.get_preferences(userID)
        preferences["global"]["match_confirmation_required"] = setting == "on"
        if setting == "on":
            await interaction.response.send_message("Confirmation enabled — you'll be asked to accept or decline each match.", ephemeral=True)
        else:
            await interaction.response.send_message("Confirmation disabled — you'll be automatically matched.", ephemeral=True)
    
    @app_commands.command(name="set-game-mode", description="Selects which mode you want to be matched for")
    @app_commands.choices(mode=MODES)
    async def setGameMode(self, interaction: discord.Interaction, mode: app_commands.Choice[str]) -> None:
        user_id = interaction.user.id
        preferences = self.get_preferences(user_id)
        preferences["matching"]["game_mode"] = mode.value
        await interaction.response.send_message(f"Your preferred mode has been set to {mode.name}.", ephemeral=True)

    @app_commands.command(name="friend-notifications", description="Toggle notifications when friends start playing the same game")
    async def friendPing(self, interaction: discord.Interaction, setting: Literal["on", "off"]) -> None:
        userID = interaction.user.id
        preferences = self.get_preferences(userID)
        preferences["notifications"]["friend_online_enabled"] = setting == "on"
        await interaction.response.send_message(f"Friend notifications turned {setting}.", ephemeral=True)
    
    @app_commands.command(name="set-timezone", description="Sets your timezone for better matching")
    @app_commands.choices(timezone=TIMEZONES)
    async def setTimezone(self, interaction: discord.Interaction, timezone: app_commands.Choice[str]) -> None:
        user_id = interaction.user.id
        preferences = self.get_preferences(user_id)
        preferences["time"]["timezone"] = timezone.value
        await interaction.response.send_message(f"Your preferred timezone has been set to {timezone.name}.", ephemeral=True)

    @app_commands.command(name="set-dnd", description="Sets what time you would like to stop being matched")
    @app_commands.choices(start_time = HOURS, end_time = HOURS)
    async def setDND(self, interaction: discord.Interaction, start_time: app_commands.Choice[str], end_time: app_commands.Choice[str]) -> None:
        user_id = interaction.user.id
        preferences = self.get_preferences(user_id)

        if start_time.value == end_time.value:
            await interaction.response.send_message("Start and end time can't be the same.", ephemeral=True)
            return
        
        preferences["time"]["dnd_start"] = start_time.value
        preferences["time"]["dnd_end"] = end_time.value
        await interaction.response.send_message(f"Your preferred DND time has been set from {start_time.name} to {end_time.name}.", ephemeral=True)
    
    @app_commands.command(name="unset-dnd", description="Unsets your DND time")
    async def unsetDND(self, interaction: discord.Interaction) -> None:
        user_id = interaction.user.id
        preferences = self.get_preferences(user_id)

        preferences["time"]["dnd_start"] = None
        preferences["time"]["dnd_end"] = None
        await interaction.response.send_message("Your DND time has been unset.", ephemeral=True)
        
    @app_commands.command(name="set-bio", description="Set a short bio visible to matched players")
    async def setBio(self, interaction: discord.Interaction, bio: str) -> None:
        if len(bio) > 150:
            await interaction.response.send_message("Bio must be 150 characters or less.", ephemeral=True)
            return
        preferences = self.get_preferences(interaction.user.id)
        preferences["profile"]["bio"] = bio
        await interaction.response.send_message(f"Bio updated: {bio}", ephemeral=True)

    @app_commands.command(name="set-name", description="Set a display name for your matching profile")
    async def setName(self, interaction: discord.Interaction, name: str) -> None:
        if len(name) > 32:
            await interaction.response.send_message("Name must be 32 characters or less.", ephemeral=True)
            return
        preferences = self.get_preferences(interaction.user.id)
        preferences["profile"]["display_name"] = name
        await interaction.response.send_message(f"Display name set to: {name}", ephemeral=True)

    @app_commands.command(name="set-region", description="Set your region for ranked matching (leave empty to clear)")
    @app_commands.choices(region=REGIONS)
    async def setRegion(self, interaction: discord.Interaction, region: Optional[app_commands.Choice[str]] = None) -> None:
        preferences = self.get_preferences(interaction.user.id)
        if region is None:
            preferences["profile"]["region"] = None
            await interaction.response.send_message("Region preference cleared — you'll be matched with anyone.", ephemeral=True)
        else:
            preferences["profile"]["region"] = region.value
            await interaction.response.send_message(f"Region set to: {region.name}", ephemeral=True)
    
    @app_commands.command(name="set-language", description="Set your preferred language for matching (leave empty to clear)")
    @app_commands.choices(language=LANGUAGES)
    async def setLanguage(self, interaction: discord.Interaction, language: Optional[app_commands.Choice[str]] = None) -> None:
        preferences = self.get_preferences(interaction.user.id)
        if language is None:
            preferences["profile"]["language"] = None
            await interaction.response.send_message("Language preference cleared — you'll be matched with anyone.", ephemeral=True)
        else:
            preferences["profile"]["language"] = language.value
            await interaction.response.send_message(f"Language set to: {language.name}", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Preferences(bot))