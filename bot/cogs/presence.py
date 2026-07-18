from discord.ext import commands
import discord
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import db.database as db

GAME_START_GRACE_PERIOD = 90
GAME_STOP_GRACE_PERIOD = 120


class Presence(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # In-memory session for fast lookups during matching and stop detection
        # Mirrors what is persisted in the database where both are kept in sync
        self.session: dict[int, dict[str, dict[str, object]]] = {}

    # Confirms a game session is genuine before recording it
    # Waits before adding to session to filter out accidental launches
    # and focus-detection noise from Discord's activity tracking
    async def verify_session_start(
        self,
        update: list[tuple[str, object, object]],
        userID: int,
        gameName: str,
        startTime: object,
        partySize: int,
        maxPartySize: int | None,
        guildID: int,
    ) -> None:
        await asyncio.sleep(GAME_START_GRACE_PERIOD)

        # Confirm the game is still in the update snapshot after the grace period which
        # prevents recording a session if the user stopped playing during the wait
        if not any(gameName == game[0] for game in update):
            return

        matching = self.bot.get_cog("Matching")

        # Ensure the user exists in the database before writing session data
        await db.check_user(userID)

        if userID not in self.session:
            self.session[userID] = {}

        existing = self.session[userID].get(gameName)

        if existing is not None:
            if guildID >= existing["guild_id"]:
                return
            # Same game already recorded for this user and only let a lower guild ID
            # to be recorded for a deterministic cross-server attribution. Higher or
            # equal IDs are a duplicate event from the same guild
            await db.end_game_session(userID, gameName)

        self.session[userID][gameName] = {
            "start_time": startTime,
            "party_size": partySize,
            "max_party_size": maxPartySize,
            "guild_id": guildID,
        }
        await db.start_game_session(userID, gameName, partySize, maxPartySize, startTime, str(guildID))
        if matching:
            await matching.check_for_match(userID, gameName)

    # Confirms a game session has genuinely ended before removing it
    # Waits before removing from session to account for brief focus switches
    # where Discord temporarily drops the activity before restoring it
    async def verify_session_end(self, userID: int, gameName: str) -> None:
        await asyncio.sleep(GAME_STOP_GRACE_PERIOD)

        if userID in self.session and gameName in self.session[userID]:
            self.session[userID].pop(gameName)

            # Persist the session end to the database
            await db.end_game_session(userID, gameName)

            # Notify matching that this user left so remaining players
            # can be re-queued for a new match after their cooldown expires
            matching = self.bot.get_cog("Matching")
            if matching:
                await matching.on_session_ended(userID, gameName)

            # Remove the user entry entirely once no active games remain,
            # to prevent stale empty records accumulating in memory
            if userID in self.session and len(self.session[userID]) == 0:
                del self.session[userID]

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member) -> None:
        userID = before.id
        guildID = after.guild.id
        update: list[tuple[str, object, object]] = [
            (game.name, game.start, game.party)
            for game in after.activities
            if game.type == discord.ActivityType.playing
        ]

        # Schedule grace period tasks for games that appeared in this update
        for currentGame in update:
            gameName = currentGame[0]
            startTime = currentGame[1]
            party = currentGame[2]
            partySize = party.get("current", 1) if party else 1
            maxPartySize = party.get("max", None) if party else None
            asyncio.create_task(
                self.verify_session_start(update, userID, gameName, startTime, partySize, maxPartySize, guildID)
            )

        # Schedule grace period tasks for games that disappeared from this update
        if userID in self.session:
            gamesToRemove = [
                currentGame for currentGame in self.session[userID]
                if not any(currentGame == game[0] for game in update)
            ]
            for gameName in gamesToRemove:
                asyncio.create_task(self.verify_session_end(userID, gameName))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Presence(bot))