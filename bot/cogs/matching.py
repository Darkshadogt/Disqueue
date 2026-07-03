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
        self.lastMatchTime: dict[int, datetime.datetime] = {}

    # Custom embeds sent to users for matching
    def build_match_embed(self, user: discord.User, otherUser: discord.User, gameName: str) -> discord.Embed:
        preferences = self.bot.get_cog("Preferences")
        userPreferences = preferences.get_preferences(user.id) if preferences else None
        otherUserPreferences = preferences.get_preferences(otherUser.id) if preferences else None

        userProfile = userPreferences["profile"] if userPreferences else {}
        other_user_profile = otherUserPreferences["profile"] if otherUserPreferences else {}

        userBio = userProfile.get("bio") or "Not set"
        userRegion = userProfile.get("region") or "Not set"
        otherUserBio = other_user_profile.get("bio") or "Not set"
        otherUserRegion = other_user_profile.get("region") or "Not set"

        embed = discord.Embed(
            title="Match Found",
            description=f"You and {otherUser.display_name} are both playing {gameName} right now.",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )

        embed.add_field(
            name="Players",
            value=f"You: {user.display_name}\nMatch: {otherUser.display_name}",
            inline=False,
        )
        embed.add_field(
            name=f"Your Profile: {user.display_name}",
            value=f"Bio: {userBio}\nRegion: {userRegion}",
            inline=True,
        )
        embed.add_field(
            name=f"Match Profile: {otherUser.display_name}",
            value=f"Bio: {otherUserBio}\nRegion: {otherUserRegion}",
            inline=True,
        )
        embed.set_footer(text="Disqueue Matchmaking")
        return embed
    
    # Retrieves users currently playing the certain game
    def get_eligible_users(self, gameName: str) -> list[int]:
        presence = self.bot.get_cog("Presence")
        if not presence:
            return []

        session = presence.session
        return [userID for userID, games in session.items() if gameName in games]

    # Checks if the user has DND enabled
    def checkDND(self, userID : int) -> bool:
        preferencesCog = self.bot.get_cog("Preferences")
        if preferencesCog is None:
            return False
        preferences = preferencesCog.get_preferences(userID)

        timezone = preferences["time"]["timezone"]
        startTime = int(preferences["time"]["dnd_start"])
        endTime = int(preferences["time"]["dnd_end"])

        if startTime is None or endTime is None:
            return False

        tz = TIMEZONE.get(timezone, ZoneInfo("UTC"))
        userCurrentHour = datetime.datetime.now(tz).hour

        if startTime < endTime:
            return startTime <= userCurrentHour < endTime

        return userCurrentHour >= startTime or userCurrentHour < endTime

    # Checks if user is able to be matched again based on the cooldown
    def check_user_cooldown(self, userID: int, cooldownMinutes: int) -> bool:
        lastMatch = self.lastMatchTime.get(userID)
        if lastMatch is None:
            return False
        elapsed = datetime.datetime.now(datetime.timezone.utc) - lastMatch
        return elapsed < datetime.timedelta(minutes=cooldownMinutes)

    # Checks if user is able ton be matched again based on their daily limits
    def check_user_limit(self, userID : int, matchLimit : int) -> bool:
        day = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        userCounts = self.dailyMatchCounts.get(userID, {})
        todayCount = userCounts.get(day, 0)
        return todayCount < matchLimit

    # Checks if both users are eligible to be matched together
    def is_eligible(self, userID: int, otherUserID: int, gameName: str) -> bool:
        preferences = self.bot.get_cog("Preferences")
        if preferences is None:
            return False

        userPreferences = preferences.get_preferences(userID)
        otherUserPreferences = preferences.get_preferences(otherUserID)

        # Check if both users have matching enabled
        if not userPreferences["global"]["enabled"] or not otherUserPreferences["global"]["enabled"]:
            return False

        # Check if both users have DMs enabled
        if not userPreferences["notifications"]["dm_enabled"] or not otherUserPreferences["notifications"]["dm_enabled"]:
            return False

        # Check if either user is in DND
        if self.checkDND(userID) or self.checkDND(otherUserID):
            return False

        # Check blocklists in both directions
        if userID in otherUserPreferences["global"]["blocklist"] or otherUserID in userPreferences["global"]["blocklist"]:
            return False

        # Check cooldown for both users
        if self.check_user_cooldown(userID, userPreferences["global"]["match_cooldown"]):
            return False
        if self.check_user_cooldown(otherUserID, otherUserPreferences["global"]["match_cooldown"]):
            return False

        # Check daily match limit for both users
        if userPreferences["global"]["match_limit"] is not None:
            if not self.check_user_limit(userID, userPreferences["global"]["match_limit"]):
                return False
        if otherUserPreferences["global"]["match_limit"] is not None:
            if not self.check_user_limit(otherUserID, otherUserPreferences["global"]["match_limit"]):
                return False

        # Language filter — only apply if both users have explicitly set a language
        # None means no preference, so skip the filter if either is unset
        userLanguage = userPreferences["profile"]["language"]
        otherUserLanguage = otherUserPreferences["profile"]["language"]
        if userLanguage is not None and otherUserLanguage is not None:
            if userLanguage != otherUserLanguage:
                return False

        # Game mode filter — only block if neither user is set to "any"
        # and their specific modes differ
        userGameMode = userPreferences["matching"]["game_mode"]
        otherUserGameMode = otherUserPreferences["matching"]["game_mode"]
        if userGameMode != "any" and otherUserGameMode != "any":
            if userGameMode != otherUserGameMode:
                return False

        # Region filter — only apply if both users are strictly in ranked mode
        # (neither set to "any") AND both have explicitly set a region
        userRegion = userPreferences["profile"]["region"]
        otherUserRegion = otherUserPreferences["profile"]["region"]
        bothStrictlyRanked = userGameMode == "ranked" and otherUserGameMode == "ranked"
        bothHaveRegion = userRegion is not None and otherUserRegion is not None
        if bothStrictlyRanked and bothHaveRegion and userRegion != otherUserRegion:
            return False

        return True

    # Continously matching users and check if their is a match
    async def check_for_match(self, userID: int, gameName: str) -> None:
        eligibleUsers = self.get_eligible_users(gameName)

        if userID in eligibleUsers:
            eligibleUsers.remove(userID)

        for otherUserID in eligibleUsers:
            if not self.is_eligible(userID, otherUserID, gameName):
                continue

            if not self.is_eligible(otherUserID, userID, gameName):
                continue

            self.record_match(userID, otherUserID)
            await self.send_match_dm(userID, otherUserID, gameName)
            break

    # Update user information once matched
    def record_match(self, userID: int, otherUserID: int) -> None:
        users = frozenset((userID, otherUserID))
        currentTime = datetime.datetime.now(datetime.timezone.utc)
        self.matchHistory[users] = currentTime

        day = currentTime.date().isoformat()
        for user in (userID, otherUserID):
            self.lastMatchTime[user] = currentTime
            self.dailyMatchCounts.setdefault(user, {})
            self.dailyMatchCounts[user][day] = self.dailyMatchCounts[user].get(day, 0) + 1

    # Sent the match notification to both user
    async def send_match_dm(self, userID: int, otherUserID: int, gameName: str) -> None:
        user = await self.bot.fetch_user(userID)
        otherUser = await self.bot.fetch_user(otherUserID)
        userEmbed = self.build_match_embed(user, otherUser, gameName)
        otherUserEmbed = self.build_match_embed(otherUser, user, gameName)

        try:
            await user.send(embed=userEmbed)
        except discord.Forbidden:
            pass

        try:
            await otherUser.send(embed=otherUserEmbed)
        except discord.Forbidden:
            pass
    


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Matching(bot))