from discord.ext import commands
import discord
import asyncio

GAME_START_GRACE_PERIOD = 10
GAME_STOP_GRACE_PERIOD = 60

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = {}
    
    # Confirms a game session is genuine before recording it
    # Waits before adding to session to filter out accidental launches
    # and focus-detection noise from Discord's activity tracking
    async def verify_session_start(self, update, userID, gameName, startTime):
        await asyncio.sleep(GAME_START_GRACE_PERIOD)   
        if any(gameName == game[0] for game in update):
            if userID not in self.session:
                self.session[userID] = {gameName: startTime}
                print(f"{userID} started playing {gameName}")
            else:
                if gameName not in self.session[userID]:
                    self.session[userID][gameName] = startTime
                    print(f"{userID} started playing {gameName}")
    
    # Confirms a game session has genuinely ended before removing it
    # Waits before removing from session to account for brief focus switches
    # where Discord temporarily drops the activity before restoring it
    async def verify_session_end(self, userID, gameName):
        await asyncio.sleep(GAME_STOP_GRACE_PERIOD)
        if userID in self.session and gameName in self.session[userID]:
            self.session[userID].pop(gameName)
            print(f"{userID} stopped playing {gameName}")

            # Remove the user entirely once their game dict is empty,
            # to avoid accumulating stale empty entries over time
            if userID in self.session and len(self.session[userID]) == 0:
                del self.session[userID]

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        userID = before.id
        update = [(game.name, game.start) for game in after.activities if game.type == discord.ActivityType.playing]

        # Add or update active games for this user
        for currentGame in update:
            gameName = currentGame[0]
            startTime = currentGame[1]
            asyncio.create_task(self.verify_session_start(update, userID, gameName, startTime))

        # Remove games the user is no longer playing
        if userID in self.session:
            gamesToRemove = []
            for currentGame in self.session[userID]:
                if not any(currentGame == game[0] for game in update):
                    gamesToRemove.append(currentGame)
            for gameName in gamesToRemove:
                asyncio.create_task(self.verify_session_end(userID, gameName))


async def setup(bot):
    await bot.add_cog(Presence(bot))