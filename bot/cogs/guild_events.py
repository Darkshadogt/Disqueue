from discord.ext import commands
import discord
import db.database as db


class GuildEvents(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        # Notify the owner if they're already a registered Disqueue user
        ownerID = str(guild.owner_id)
        await db.check_user(ownerID)
        await db.create_notification(
            ownerID,
            "server_added",
            "Disqueue added to a server",
            f"Disqueue was added to {guild.name}. It's now part of the cross-server matching pool.",
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        # Don't call check_user here if the owner has no existing profile
        # there's nothing meaningful to notify them about
        ownerID = str(guild.owner_id)
        existingProfile = await db.get_user_profile(ownerID)
        if existingProfile is None:
            return

        await db.create_notification(
            ownerID,
            "server_removed",
            "Disqueue removed from a server",
            f"Disqueue was removed from {guild.name}. It's no longer part of the matching pool.",
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GuildEvents(bot))