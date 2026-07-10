from discord.ext import commands
import discord
import asyncio

GAME_START_GRACE_PERIOD = 90
GAME_STOP_GRACE_PERIOD = 120

class Presence(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.session: dict[int, dict[str, dict[str, object]]] = {}
    
    # Confirms a game session is genuine before recording it
    # Waits before adding to session to filter out accidental launches
    # and focus-detection noise from Discord's activity tracking
    async def verify_session_start(self, update, userID, gameName, startTime, partySize, maxPartySize):
        await asyncio.sleep(GAME_START_GRACE_PERIOD)
        if any(gameName == game[0] for game in update):
            matching = self.bot.get_cog("Matching")
            if userID not in self.session:
                self.session[userID] = {
                    gameName: {
                        "start_time": startTime,
                        "party_size": partySize,
                        "max_party_size": maxPartySize
                    }
                }
                print(f"{userID} started playing {gameName}")
                if matching:
                    await matching.check_for_match(userID, gameName)
            else:
                if gameName not in self.session[userID]:
                    self.session[userID][gameName] = {
                        "start_time": startTime,
                        "party_size": partySize,
                        "max_party_size": maxPartySize
                    }
                    print(f"{userID} started playing {gameName}")
                    if matching:
                        await matching.check_for_match(userID, gameName)
    
    # Confirms a game session has genuinely ended before removing it
    # Waits before removing from session to account for brief focus switches
    # where Discord temporarily drops the activity before restoring it
    async def verify_session_end(self, userID: int, gameName: str) -> None:
        await asyncio.sleep(GAME_STOP_GRACE_PERIOD)
        if userID in self.session and gameName in self.session[userID]:
            self.session[userID].pop(gameName)
            print(f"{userID} stopped playing {gameName}")

            # Notify matching that this user left so remaining players
            # can be re-queued for a new match after their cooldown expires
            matching = self.bot.get_cog("Matching")
            if matching:
                await matching.on_session_ended(userID, gameName)

            # Remove the user entirely once their game dict is empty,
            # to avoid accumulating stale empty entries over time
            if userID in self.session and len(self.session[userID]) == 0:
                del self.session[userID]

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member) -> None:
        userID = before.id
        update: list[tuple[str, object, object]] = [
            (game.name, game.start, game.party)
            for game in after.activities
            if game.type == discord.ActivityType.playing
        ]

        # Add or update active games for this user
        for currentGame in update:
            gameName = currentGame[0]
            startTime = currentGame[1]
            party = currentGame[2]
            partySize = party.get("current", 1) if party else 1
            maxPartySize = party.get("max", None) if party else None
            asyncio.create_task(self.verify_session_start(update, userID, gameName, startTime, partySize, maxPartySize))

        # Remove games the user is no longer playing
        if userID in self.session:
            gamesToRemove = []
            for currentGame in self.session[userID]:
                if not any(currentGame == game[0] for game in update):
                    gamesToRemove.append(currentGame)
            for gameName in gamesToRemove:
                asyncio.create_task(self.verify_session_end(userID, gameName))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Presence(bot))