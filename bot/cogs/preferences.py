from discord.ext import commands
from discord import app_commands
import discord
import sys
import os
from typing import Optional, Literal

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import db.database as db

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

    @app_commands.command(name="reset", description="Reset your user preferences")
    async def reset(self, interaction: discord.Interaction) -> None:
        userID = str(interaction.user.id)
        await db.reset_preferences(userID)
        await interaction.response.send_message("Your preferences have been reset.", ephemeral=True)

    @app_commands.command(name="preferences", description="View your current preferences")
    async def viewPreferences(self, interaction: discord.Interaction) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)

        prefs = await db.get_preferences(userID)
        blocklist = await db.get_blocklist(userID)

        dndStart = prefs["dnd_start"]
        dndEnd = prefs["dnd_end"]
        dndDisplay = f"{int(dndStart):02d}:00 - {int(dndEnd):02d}:00" if dndStart and dndEnd else "Not set"

        embed = discord.Embed(title="Your Preferences", color=discord.Color.blue())

        embed.add_field(name="Global", value=
            f"Enabled: {prefs['enabled']}\n"
            f"Match Limit: {prefs['match_limit'] or 'None'}\n"
            f"Cooldown: {prefs['match_cooldown']} min\n"
            f"Confirmation: {prefs['match_confirmation_required']}\n"
            f"Blocked Users: {len(blocklist)}",
            inline=True)

        embed.add_field(name="Notifications", value=
            f"DMs: {prefs['dm_enabled']}\n"
            f"Friend Pings: {prefs['friend_online_enabled']}",
            inline=True)

        embed.add_field(name="Time", value=
            f"Timezone: {prefs['timezone'].upper()}\n"
            f"DND: {dndDisplay}",
            inline=True)

        embed.add_field(name="Profile", value=
            f"Name: {prefs['display_name'] or 'Not set'}\n"
            f"Bio: {prefs['bio'] or 'Not set'}\n"
            f"Language: {prefs['language'] or 'Not set'}\n"
            f"Region: {prefs['region'] or 'Not set'}",
            inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="enable", description="Start receiving match notifications")
    async def enable(self, interaction: discord.Interaction) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await interaction.response.defer(ephemeral=True)

        # Try sending a test DM to verify user can receive messages
        try:
            user = await self.bot.fetch_user(userID)
            await user.send("Your DMs are open — you're all set to receive match notifications from Disqueue!")
        except discord.Forbidden:
            await interaction.followup.send(
                "Could not enable matching — your DMs are closed. Please open your DMs and try again.\n"
                "To open DMs: **User Settings → Privacy & Safety → Allow direct messages from server members**",
                ephemeral=True
            )
            return

        await db.update_preference(userID, "enabled", True)
        await db.update_preference(userID, "dm_enabled", True)
        await interaction.followup.send(
            "Matching enabled — we sent you a DM to confirm everything is working.",
            ephemeral=True
        )

    @app_commands.command(name="disable", description="Stop receiving match notifications")
    async def disable(self, interaction: discord.Interaction) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await db.update_preference(userID, "enabled", False)
        await db.update_preference(userID, "dm_enabled", False)
        await interaction.response.send_message(
            "Matching disabled — you won't receive any match notifications.",
            ephemeral=True
        )

    @app_commands.command(name="block", description="Block a user from being matched with you")
    async def block(self, interaction: discord.Interaction, user: discord.Member) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)

        if user.id == userID:
            await interaction.response.send_message("You can't block yourself.", ephemeral=True)
            return

        blocklist = await db.get_blocklist(userID)
        if user.id in blocklist:
            await interaction.response.send_message(f"{user.display_name} is already in your blocklist.", ephemeral=True)
            return

        await db.add_to_blocklist(userID, user.id)
        await interaction.response.send_message(f"{user.display_name} has been added to your blocklist.", ephemeral=True)

    @app_commands.command(name="unblock", description="Unblock a user so they can be matched with you again")
    async def unblock(self, interaction: discord.Interaction, user: discord.Member) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)

        blocklist = await db.get_blocklist(userID)
        if user.id not in blocklist:
            await interaction.response.send_message(f"{user.display_name} is not in your blocklist.", ephemeral=True)
            return

        await db.remove_from_blocklist(userID, user.id)
        await interaction.response.send_message(
            f"{user.display_name} has been unblocked and can be matched with you again.",
            ephemeral=True
        )

    @app_commands.command(name="blockid", description="Block a user by their ID from being matched with you")
    async def blockID(self, interaction: discord.Interaction, user_id: int) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)

        if user_id == userID:
            await interaction.response.send_message("You can't block yourself.", ephemeral=True)
            return

        blocklist = await db.get_blocklist(userID)
        if user_id in blocklist:
            await interaction.response.send_message("That user is already blocked.", ephemeral=True)
            return

        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await interaction.response.send_message("No Discord user found with that ID.", ephemeral=True)
            return

        await db.add_to_blocklist(userID, user_id)
        await interaction.response.send_message(f"{user.display_name} has been blocked.", ephemeral=True)

    @app_commands.command(name="unblockid", description="Unblock a user by their ID so they can be matched with you again")
    async def unblockID(self, interaction: discord.Interaction, user_id: int) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)

        if user_id == userID:
            await interaction.response.send_message("You can't unblock yourself.", ephemeral=True)
            return

        blocklist = await db.get_blocklist(userID)
        if user_id not in blocklist:
            await interaction.response.send_message("That user is not in your blocklist.", ephemeral=True)
            return

        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            # User no longer exists on Discord — still remove from blocklist
            await db.remove_from_blocklist(userID, user_id)
            await interaction.response.send_message("User removed from your blocklist.", ephemeral=True)
            return

        await db.remove_from_blocklist(userID, user_id)
        await interaction.response.send_message(f"{user.display_name} has been unblocked.", ephemeral=True)

    @app_commands.command(name="set-match-limit", description="Sets the number of matches a user can be matched in a day (leave blank to remove limit)")
    async def setMatchLimit(self, interaction: discord.Interaction, limit: Optional[int] = None) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)

        if limit is not None and limit <= 0:
            await interaction.response.send_message("Limit must be a positive number.", ephemeral=True)
            return

        await db.update_preference(userID, "match_limit", limit)

        if limit is None:
            await interaction.response.send_message("Match limit removed — no daily limit set.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Match limit set to {limit} per day.", ephemeral=True)

    @app_commands.command(name="set-match-cooldown", description="Sets the cooldown time before a user can be matched again (leave blank to reset to default)")
    async def setMatchCooldown(self, interaction: discord.Interaction, time: Optional[int] = None) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)

        if time is not None and time <= 0:
            await interaction.response.send_message("Cooldown must be a positive number.", ephemeral=True)
            return

        # Default cooldown is 2 minutes — reset to this if no value provided
        cooldown = time if time is not None else 2
        await db.update_preference(userID, "match_cooldown", cooldown)

        if time is None:
            await interaction.response.send_message("Match cooldown reset to the default (2 minutes).", ephemeral=True)
        else:
            await interaction.response.send_message(f"Match cooldown set to {time} minutes.", ephemeral=True)

    @app_commands.command(name="match-confirmation", description="Toggle whether you confirm or auto-accept matches")
    async def matchConfirmation(self, interaction: discord.Interaction, setting: Literal["on", "off"]) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await db.update_preference(userID, "match_confirmation_required", setting == "on")

        if setting == "on":
            await interaction.response.send_message(
                "Confirmation enabled — you'll be asked to accept or decline each match.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Confirmation disabled — you'll be automatically matched.",
                ephemeral=True
            )

    @app_commands.command(name="set-game-mode", description="Selects which mode you want to be matched for")
    @app_commands.choices(mode=MODES)
    async def setGameMode(self, interaction: discord.Interaction, mode: app_commands.Choice[str]) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await db.update_preference(userID, "game_mode", mode.value)
        await interaction.response.send_message(f"Your preferred mode has been set to {mode.name}.", ephemeral=True)

    @app_commands.command(name="friend-notifications", description="Toggle notifications when friends start playing the same game")
    async def friendPing(self, interaction: discord.Interaction, setting: Literal["on", "off"]) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await db.update_preference(userID, "friend_online_enabled", setting == "on")
        await interaction.response.send_message(f"Friend notifications turned {setting}.", ephemeral=True)

    @app_commands.command(name="set-timezone", description="Sets your timezone for better matching")
    @app_commands.choices(timezone=TIMEZONES)
    async def setTimezone(self, interaction: discord.Interaction, timezone: app_commands.Choice[str]) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await db.update_preference(userID, "timezone", timezone.value)
        await interaction.response.send_message(f"Your preferred timezone has been set to {timezone.name}.", ephemeral=True)

    @app_commands.command(name="set-dnd", description="Sets what time you would like to stop being matched")
    @app_commands.choices(start_time=HOURS, end_time=HOURS)
    async def setDND(self, interaction: discord.Interaction, start_time: app_commands.Choice[str], end_time: app_commands.Choice[str]) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)

        if start_time.value == end_time.value:
            await interaction.response.send_message("Start and end time can't be the same.", ephemeral=True)
            return

        await db.update_preference(userID, "dnd_start", int(start_time.value))
        await db.update_preference(userID, "dnd_end", int(end_time.value))
        await interaction.response.send_message(
            f"DND time set from {start_time.name} to {end_time.name}.",
            ephemeral=True
        )

    @app_commands.command(name="unset-dnd", description="Unsets your DND time")
    async def unsetDND(self, interaction: discord.Interaction) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await db.update_preference(userID, "dnd_start", None)
        await db.update_preference(userID, "dnd_end", None)
        await interaction.response.send_message("Your DND time has been cleared.", ephemeral=True)

    @app_commands.command(name="set-bio", description="Set a short bio visible to matched players")
    async def setBio(self, interaction: discord.Interaction, bio: str) -> None:
        if len(bio) > 150:
            await interaction.response.send_message("Bio must be 150 characters or less.", ephemeral=True)
            return
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await db.update_preference(userID, "bio", bio)
        await interaction.response.send_message(f"Bio updated: {bio}", ephemeral=True)

    @app_commands.command(name="set-name", description="Set a display name for your matching profile")
    async def setName(self, interaction: discord.Interaction, name: str) -> None:
        if len(name) > 32:
            await interaction.response.send_message("Name must be 32 characters or less.", ephemeral=True)
            return
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await db.update_preference(userID, "display_name", name)
        await interaction.response.send_message(f"Display name set to: {name}", ephemeral=True)

    @app_commands.command(name="set-region", description="Set your region for ranked matching (leave empty to clear)")
    @app_commands.choices(region=REGIONS)
    async def setRegion(self, interaction: discord.Interaction, region: Optional[app_commands.Choice[str]] = None) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await db.update_preference(userID, "region", region.value if region else None)

        if region is None:
            await interaction.response.send_message("Region preference cleared — you'll be matched with anyone.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Region set to: {region.name}", ephemeral=True)

    @app_commands.command(name="set-language", description="Set your preferred language for matching (leave empty to clear)")
    @app_commands.choices(language=LANGUAGES)
    async def setLanguage(self, interaction: discord.Interaction, language: Optional[app_commands.Choice[str]] = None) -> None:
        userID = str(interaction.user.id)
        await db.check_user(userID)
        await db.update_preference(userID, "language", language.value if language else None)

        if language is None:
            await interaction.response.send_message("Language preference cleared — you'll be matched with anyone.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Language set to: {language.name}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Preferences(bot))