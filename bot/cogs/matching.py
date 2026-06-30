from discord.ext import commands
import discord
import datetime
import asyncio
from zoneinfo import ZoneInfo

TIMEZONE = {
    "utc": ZoneInfo("UTC"),
    "est": ZoneInfo("US/Eastern"),
    "cst": ZoneInfo("US/Central"),
    "mst": ZoneInfo("US/Mountain"),
    "pst": ZoneInfo("US/Pacific"),
    "akst": ZoneInfo("US/Alaska"),
    "hst": ZoneInfo("US/Hawaii"),
    "gmt": ZoneInfo("GMT"),
    "cet": ZoneInfo("CET"),
    "ist": ZoneInfo("Asia/Kolkata"),
    "jst": ZoneInfo("Asia/Tokyo"),
    "aest": ZoneInfo("Australia/Sydney"),
}

class Matching(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.matchHistory: dict[frozenset[int], datetime.datetime] = {}
        self.dailyMatchCounts: dict[int, dict[str, int]] = {}
    
    def get_eligible_users(self, gameName: str) -> list[int]:
        presence = self.bot.get_cog("Presence")
        if not presence:
            return []

        session = presence.session
        return [userID for userID, games in session.items() if gameName in games]

    def get_current_hour(self, timezone: str) -> int:
        return datetime.datetime.now(TIMEZONE[timezone]).hour

    def checkDND(self, userID : int) -> bool:
        preferences = self.bot.get_cog("Preferences").get_preferences(userID)

        timezone = preferences["time"]["timezone"]
        startTime = preferences["time"]["dnd_start"]
        endTime = preferences["time"]["dnd_end"]

        if startTime is None or endTime is None:
            return False

        tz = TIMEZONE.get(timezone, ZoneInfo("UTC"))
        userCurrentHour = datetime.datetime.now(tz).hour

        if startTime < endTime:
            return startTime <= userCurrentHour < endTime

        return userCurrentHour >= startTime or userCurrentHour < endTime

    def check_user_cooldown(self, userID: int, cooldown_minutes: int) -> bool:
        latestMatchTime = None

        for otherUser, matchedTime in self.matchHistory.items():
            if userID in otherUser and (latestMatchTime is None or matchedTime> latestMatchTime):
                latestMatchTime = matchedTime

        if latestMatchTime is None:
            return False

        elapsed = datetime.datetime.now(datetime.timezone.utc) - latestMatchTime
        return elapsed < datetime.timedelta(minutes=cooldown_minutes)

    def check_user_limit(self, userID : int, match_limit : int) -> bool:
        matchedTimes = 0

        for match in self.matchHistory:
            if userID in match:
                matchedTimes += 1
        
        return matchedTimes < match_limit

    def is_eligible(self, userID: int, otherUserID: int, gameName: str) -> bool:
        preferences = self.bot.get_cog("Preferences")
        if preferences is None:
            return False

        userPreferences = preferences.get_preferences(userID)
        otherUserPreferences = preferences.get_preferences(otherUserID)

        if not userPreferences["global"]["enabled"] or not otherUserPreferences["global"]["enabled"]:
            return False

        if not userPreferences["notifications"]["dm_enabled"] or not otherUserPreferences["notifications"]["dm_enabled"]:
            return False

        if self.checkDND(userID) or self.checkDND(otherUserID):
            return False

        if userID in otherUserPreferences["global"]["blocklist"] or otherUserID in userPreferences["global"]["blocklist"]:
            return False

        if self.check_user_cooldown(userID, userPreferences["global"]["match_cooldown"]):
            return False

        if self.check_user_cooldown(otherUserID, otherUserPreferences["global"]["match_cooldown"]):
            return False
        
        if userPreferences["global"]["match_limit"] is not None and not self.check_user_limit(userID, userPreferences["global"]["match_limit"]):
            return False
        
        if otherUserPreferences["global"]["match_limit"] is not None and not self.check_user_limit(otherUserID, otherUserPreferences["global"]["match_limit"]):
            return False

        return True
    


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Matching(bot))