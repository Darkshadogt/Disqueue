from discord.ext import commands
import discord
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import db.database as db


class GuildEvents(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        # Notify the guild owner if they're already a registered Disqueue user
        ownerID = str(guild.ownerID)
        await db.check_user(ownerID)
        await db.create_notification(
            ownerID,
            "server_added",
            "Disqueue added to a server",
            f"Disqueue was added to {guild.name}. It's now part of the cross-server matching pool.",
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        ownerID = str(guild.ownerID)
        # Don't call check_user here. If the owner already has a row this
        # still works, and if they don't, there's nothing meaningful to notify
        existing = await db.get_user_profile(ownerID)
        if existing is not None:
            await db.create_notification(
                ownerID,
                "server_removed",
                "Disqueue removed from a server",
                f"Disqueue was removed from {guild.name}. It's no longer part of the matching pool.",
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GuildEvents(bot))