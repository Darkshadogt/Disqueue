from discord.ext import commands
import discord
import asyncio
import db.database as db

# Grace periods filter out noise from Discord's activity tracking
# brief focus switches or accidental launches shouldn't register as real sessions
from config import GAME_START_GRACE_PERIOD, GAME_STOP_GRACE_PERIOD

class Presence(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # In-memory mirror of active sessions for fast lookups during matching
        # Kept in sync with what's persisted in the database
        self.session: dict[int, dict[str, dict[str, object]]] = {}

    async def _confirm_session_start(
        self,
        currentActivities: list[tuple[str, object, object]],
        userID: int,
        gameName: str,
        startTime: object,
        partySize: int,
        maxPartySize: int | None,
        guildID: int,
    ) -> None:
        # Wait out the grace period, then confirm the game is still active
        # before recording it as a genuine session
        await asyncio.sleep(GAME_START_GRACE_PERIOD)

        if not any(gameName == activity[0] for activity in currentActivities):
            return

        await db.check_user(str(userID))

        userSessions = self.session.setdefault(userID, {})
        existingSession = userSessions.get(gameName)

        if existingSession is not None:
            # Lower guild ID wins for deterministic cross-server attribution
            # Equal or higher IDs are treated as a duplicate event from the same guild
            if guildID >= existingSession["guild_id"]:
                return
            await db.end_game_session(str(userID), gameName)

        userSessions[gameName] = {
            "start_time": startTime,
            "party_size": partySize,
            "max_party_size": maxPartySize,
            "guild_id": guildID,
        }

        await db.start_game_session(
            str(userID),
            gameName,
            partySize,
            maxPartySize,
            startTime,
            str(guildID),
        )

        matching = self.bot.get_cog("Matching")
        if matching:
            await matching.check_for_match(userID, gameName)

    async def _confirm_session_end(self, userID: int, gameName: str) -> None:
        # Wait out the grace period before treating the session as truly over,
        # to account for brief activity drops rather than the user actually stopping
        await asyncio.sleep(GAME_STOP_GRACE_PERIOD)

        userSessions = self.session.get(userID)
        if userSessions is None or gameName not in userSessions:
            return

        userSessions.pop(gameName)
        await db.end_game_session(str(userID), gameName)

        matching = self.bot.get_cog("Matching")
        if matching:
            # Re-queue any remaining players now that this user has left,
            # subject to their normal cooldown in is_eligible
            await matching.on_session_ended(userID, gameName)

        if not userSessions:
            del self.session[userID]

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member) -> None:
        userID = before.id
        guildID = after.guild.id

        currentActivities: list[tuple[str, object, object]] = [
            (activity.name, activity.start, activity.party)
            for activity in after.activities
            if activity.type == discord.ActivityType.playing
        ]

        for gameName, startTime, party in currentActivities:
            partySize = party.get("current", 1) if party else 1
            maxPartySize = party.get("max", None) if party else None
            asyncio.create_task(
                self._confirm_session_start(
                    currentActivities,
                    userID,
                    gameName,
                    startTime,
                    partySize,
                    maxPartySize,
                    guildID,
                )
            )

        activeGames = self.session.get(userID)
        if not activeGames:
            return

        currentGameNames = {activity[0] for activity in currentActivities}
        endedGames = [gameName for gameName in activeGames if gameName not in currentGameNames]

        for gameName in endedGames:
            asyncio.create_task(self._confirm_session_end(userID, gameName))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Presence(bot))