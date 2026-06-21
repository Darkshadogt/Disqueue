from discord.ext import commands
import discord

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = {}
    
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        userID = before.id
        update = [(game.name, game.start) for game in after.activities if game.type == discord.ActivityType.playing]
        
        # Add or update active games for this user
        for currentGame in update:
            gameName = currentGame[0]
            startTime = currentGame[1]
            if userID not in self.session.keys():
                self.session[userID] = {gameName : startTime}
                print(f"{userID} started playing {gameName}")
            else:
                if gameName not in self.session[userID].keys():
                    self.session[userID][gameName] = startTime             
                    print(f"{userID} started playing {gameName}")

        # Remove games the user is no longer playing
        if userID in self.session:
            gamesToRemove = []
            for currentGame in self.session[userID]:
                if not any(currentGame == game[0] for game in update):
                    gamesToRemove.append(currentGame)
            for game in gamesToRemove:
                self.session[userID].pop(game)
            print(f"{userID} stopped playing {game}")
            
        # Remove the user entirely once their game dict is empty,
        # to avoid accumulating stale empty entries over time
        if userID in self.session.keys() and len(self.session[userID]) == 0:
            del self.session[userID]

async def setup(bot):
    await bot.add_cog(Presence(bot))