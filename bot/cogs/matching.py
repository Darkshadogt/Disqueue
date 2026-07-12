from discord.ext import commands
from discord import app_commands
import discord
import datetime
from zoneinfo import ZoneInfo
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import db.database as db


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

DISQUEUE_SERVER_INVITE = "https://discord.gg/..."


class MatchConfirmationView(discord.ui.View):
    # Per-user confirmation view shown in DM for a single pending match
    def __init__(
        self,
        matching: "Matching",
        pairKey: frozenset[int],
        userID: int,
        otherUserID: int,
        gameName: str,
        timeout: float = 300,
    ) -> None:
        super().__init__(timeout=timeout)
        self.matching = matching
        self.pairKey = pairKey
        self.userID = userID
        self.otherUserID = otherUserID
        self.gameName = gameName

    def disable_buttons(self) -> None:
        # Disable the view once the request is resolved so the buttons cannot be reused
        for item in self.children:
            item.disabled = True

    async def on_timeout(self) -> None:
        # Expired requests are cleaned up by the cog so they do not stay pending forever
        await self.matching.handle_match_timeout(self.pairKey, self.userID, self.otherUserID, self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only the intended recipient can respond to this DM prompt
        if interaction.user.id != self.userID:
            await interaction.response.send_message(
                "These match buttons are only for the intended recipient.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.matching.handle_match_response(interaction, self.pairKey, self.userID, True, self)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.matching.handle_match_response(interaction, self.pairKey, self.userID, False, self)


class Matching(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.pendingMatches: dict[frozenset[int], dict[str, object]] = {}

    async def build_match_embed(
        self,
        user: discord.User,
        otherUser: discord.User,
        gameName: str,
        statusText: str = "Pending other player's confirmation",
    ) -> discord.Embed:
        # Build the DM embed with both players' profile details
        userPreferences = await db.get_preferences(user.id)
        otherUserPreferences = await db.get_preferences(otherUser.id)

        userBio = (userPreferences["bio"] if userPreferences else None) or "Not set"
        userRegion = (userPreferences ["region"] if userPreferences else None) or "Not set"
        otherUserBio = (otherUserPreferences["bio"] if otherUserPreferences else None) or "Not set"
        otherUserRegion = (otherUserPreferences["region"] if otherUserPreferences else None) or "Not set"

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
        embed.add_field(
            name="Status",
            value=statusText,
            inline=False,
        )
        embed.set_footer(text="Disqueue Matchmaking")
        return embed

    async def build_confirmed_match_embed(self, user: discord.User, otherUser: discord.User, gameName: str) -> discord.Embed:
        # Reuse the base match embed, then add connection instructions only after both users accept
        embed = await self.build_match_embed(user, otherUser, gameName, statusText="Confirmed")
        embed.add_field(
            name="How to connect",
            value=(
                f"Now that the match is confirmed for both of you, join our hub server to chat: {DISQUEUE_SERVER_INVITE}\n"
                f"Or add them directly on Discord: `{otherUser.name}`"
            ),
            inline=False,
        )
        return embed

    def _match_key(self, userID: int, otherUserID: int) -> frozenset[int]:
        return frozenset((userID, otherUserID))

    async def _match_confirmation_required(self, userID: int) -> bool:
        # Fall back to confirmation enabled if preferences are unavailable
        preferences = await db.get_preferences(userID)
        if preferences is None:
            return False
        return preferences["match_confirmation_required"]

    def _create_confirmation_view(
        self,
        pairKey: frozenset[int],
        userID: int,
        otherUserID: int,
        gameName: str,
    ) -> MatchConfirmationView:
        return MatchConfirmationView(self, pairKey, userID, otherUserID, gameName)

    def _disable_view(self, view: MatchConfirmationView | None) -> None:
        # Guard helper for optional views stored in the pending match state
        if view is not None:
            view.disable_buttons()

    async def _edit_message(
        self,
        message: discord.Message | None,
        content: str | None,
        view: MatchConfirmationView | None,
        embed: discord.Embed | None = None,
    ) -> None:
        if message is None:
            return

        try:
            await message.edit(content=content, embed=embed, view=view)
        except discord.HTTPException:
            pass

    def get_eligible_users(self, gameName: str) -> list[int]:
        # Read the active presence session and return users currently playing the same game
        presenceCog = self.bot.get_cog("Presence")
        if not presenceCog:
            return []
        session = presenceCog.session
        return [userID for userID, games in session.items() if gameName in games]

    async def checkDND(self, userID: int) -> bool:
        # Respect each user's quiet hours before creating a match
        preferences = await db.get_preferences(userID)
        if preferences is None:
            return False

        timezone = preferences["timezone"]
        startTime = preferences["dnd_start"]
        endTime = preferences["dnd_end"]

        if startTime is None or endTime is None:
            return False

        tz = TIMEZONE.get(timezone, ZoneInfo("UTC"))
        userCurrentHour = datetime.datetime.now(tz).hour
        startHour = int(startTime)
        endHour = int(endTime)

        if startHour < endHour:
            return startHour <= userCurrentHour < endHour

        return userCurrentHour >= startHour or userCurrentHour < endHour

    async def check_user_cooldown(self, userID: int, cooldownMinutes: int) -> bool:
        lastMatch = await db.get_last_match_time(userID)
        if lastMatch is None:
            return False
        elapsed = datetime.datetime.now(datetime.timezone.utc) - lastMatch
        return elapsed < datetime.timedelta(minutes=cooldownMinutes)

    async def check_user_limit(self, userID: int, matchLimit: int) -> bool:
        todayCount = await db.get_match_count_today(userID)
        return todayCount < matchLimit

    async def is_eligible(self, userID: int, otherUserID: int, gameName : str) -> bool:
        #Apply all matching rules before DM is sent
        await db.check_user(userID)
        await db.check_user(otherUserID)

        userPreferences = await db.get_preferences(userID)
        otherUserPreferences = await db.get_preferences(otherUserID)

        if userPreferences is None or otherUserPreferences is None:
            return False

        if not userPreferences["enabled"] or not otherUserPreferences["enabled"]:
            return False

        if not userPreferences["dm_enabled"] or not otherUserPreferences["dm_enabled"]:
            return False

        if await self.checkDND(userID) or await self.checkDND(otherUserID):
            return False

        userBlocklist = await db.get_blocklist(userID)
        otherBlocklist = await db.get_blocklist(otherUserID)
        if userID in otherBlocklist or otherUserID in userBlocklist:
            return False

        if await self.check_user_cooldown(userID, userPreferences["match_cooldown"]):
            return False
        if await self.check_user_cooldown(otherUserID, otherUserPreferences["match_cooldown"]):
            return False

        if userPreferences["match_limit"] is not None:
            if not await self.check_user_limit(userID, userPreferences["match_limit"]):
                return False
        if otherUserPreferences["match_limit"] is not None:
            if not await self.check_user_limit(otherUserID, otherUserPreferences["match_limit"]):
                return False

        userLanguage = userPreferences["language"]
        otherUserLanguage = otherUserPreferences["language"]
        if userLanguage is not None and otherUserLanguage is not None:
            if userLanguage != otherUserLanguage:
                return False

        userGameMode = userPreferences["game_mode"]
        otherUserGameMode = otherUserPreferences["game_mode"]
        if userGameMode != "any" and otherUserGameMode != "any":
            if userGameMode != otherUserGameMode:
                return False

        userRegion = userPreferences["region"]
        otherUserRegion = otherUserPreferences["region"]
        bothStrictlyRanked = userGameMode == "ranked" and otherUserGameMode == "ranked"
        bothHaveRegion = userRegion is not None and otherUserRegion is not None
        if bothStrictlyRanked and bothHaveRegion and userRegion != otherUserRegion:
            return False

        return True

    async def check_for_match(self, userID: int, gameName: str) -> None:
        # Find the first eligible partner and start the confirmation flow
        eligibleUsers = self.get_eligible_users(gameName)

        if userID in eligibleUsers:
            eligibleUsers.remove(userID)

        for otherUserID in eligibleUsers:
            pairKey = self._match_key(userID, otherUserID)
            if pairKey in self.pendingMatches:
                continue

            if not await self.is_eligible(userID, otherUserID, gameName):
                continue

            if not await self.is_eligible(otherUserID, userID, gameName):
                continue

            sent = await self.send_match_dm(userID, otherUserID, gameName)
            if sent:
                break
        
    async def record_match(self, userID: int, otherUserID: int, gameName: str) -> None:
        # Record the match only after both players have confirmed
        await db.record_match(userID, otherUserID, gameName)

    async def handle_match_response(
        self,
        interaction: discord.Interaction,
        pairKey: frozenset[int],
        userID: int,
        accepted: bool,
        view: MatchConfirmationView,
    ) -> None:
        # Process an accept or decline from one side of a pending match
        state = self.pendingMatches.get(pairKey)
        if state is None or state.get("resolved"):
            await interaction.response.send_message("This match is no longer active.", ephemeral=True)
            return

        gameName = state["gameName"]
        choices: dict[int, str] = state["choices"]
        messages: dict[int, discord.Message] = state["messages"]
        views: dict[int, MatchConfirmationView] = state["views"]
        otherUserID = next(uid for uid in pairKey if uid != userID)

        # Retrieve stored user objects
        storedUser: discord.User = state["user"]
        storedOtherUser: discord.User = state["otherUser"]
        currentUser = storedUser if storedUser.id == userID else storedOtherUser
        currentOtherUser = storedOtherUser if storedUser.id == userID else storedUser

        # Store the user's choice so the second response can complete or cancel the pair
        choices[userID] = "accepted" if accepted else "declined"
        self._disable_view(view)

        if not accepted:
            # One decline cancels the entire pair immediately
            state["resolved"] = True
            declinedEmbed = await self.build_match_embed(
                currentUser,
                currentOtherUser,
                gameName,
                statusText="Declined",
            )
            await interaction.response.edit_message(view=view, embed=declinedEmbed)

            otherMessage = messages.get(otherUserID)
            otherView = views.get(otherUserID)
            self._disable_view(otherView)
            declinedOtherEmbed = await self.build_match_embed(
                currentOtherUser,
                currentUser,
                gameName,
                statusText="Declined by the other user",
            )
            await self._edit_message(otherMessage, None, otherView, declinedOtherEmbed)
            self.pendingMatches.pop(pairKey, None)
            return

        acceptedEmbed = await self.build_match_embed(
            currentUser,
            currentOtherUser,
            gameName,
            statusText="Accepted — waiting for the other user",
        )
        await interaction.response.edit_message(view=view, embed=acceptedEmbed)

        # If the second player has not responded yet, keep the match pending
        if len(choices) != 2 or any(choice != "accepted" for choice in choices.values()):
            return

        # Both users accepted — finalize the match and close out the pending state
        state["resolved"] = True
        await self.record_match(userID, otherUserID, gameName)

        confirmedUserEmbed = await self.build_confirmed_match_embed(currentUser, currentOtherUser, gameName)
        confirmedOtherEmbed = await self.build_confirmed_match_embed(currentOtherUser, currentUser, gameName)

        currentMessage = messages.get(userID)
        otherMessage = messages.get(otherUserID)
        currentView = views.get(userID)
        otherView = views.get(otherUserID)

        self._disable_view(currentView)
        self._disable_view(otherView)

        await self._edit_message(currentMessage, None, currentView, confirmedUserEmbed)
        await self._edit_message(otherMessage, None, otherView, confirmedOtherEmbed)
        self.pendingMatches.pop(pairKey, None)

    async def handle_match_timeout(
        self,
        pairKey: frozenset[int],
        userID: int,
        otherUserID: int,
        view: MatchConfirmationView,
    ) -> None:
        # Timeout cleanup keeps stale requests from blocking future matches
        state = self.pendingMatches.get(pairKey)
        if state is None or state.get("resolved"):
            return

        state["resolved"] = True

        # Retrieve stored user objects
        # which can fail silently if the network is unavailable
        storedUser: discord.User = state["user"]
        storedOtherUser: discord.User = state["otherUser"]
        currentUser = storedUser if storedUser.id == userID else storedOtherUser
        currentOtherUser = storedOtherUser if storedUser.id == userID else storedUser

        messages: dict[int, discord.Message] = state["messages"]
        views: dict[int, MatchConfirmationView] = state["views"]

        currentMessage = messages.get(userID)
        currentView = views.get(userID)
        otherMessage = messages.get(otherUserID)
        otherView = views.get(otherUserID)

        expiredUserEmbed = await self.build_match_embed(
            currentUser,
            currentOtherUser,
            state["gameName"],
            statusText="Expired after 5 minutes",
        )
        expiredOtherEmbed = await self.build_match_embed(
            currentOtherUser,
            currentUser,
            state["gameName"],
            statusText="Expired after 5 minutes",
        )

        self._disable_view(currentView)
        self._disable_view(otherView)

        await self._edit_message(currentMessage, None, currentView, expiredUserEmbed)
        await self._edit_message(otherMessage, None, otherView, expiredOtherEmbed)
        self.pendingMatches.pop(pairKey, None)

    async def send_match_dm(self, userID: int, otherUserID: int, gameName: str) -> bool:
        # There are three possible outcomes here:
        # 1. Neither user requires confirmation, so the match is sent and recorded immediately
        # 2. One or both users require confirmation, so the DM is sent with Accept/Decline buttons
        # 3. The request later resolves through accept, decline, or timeout cleanup
        user = await self.bot.fetch_user(userID)
        otherUser = await self.bot.fetch_user(otherUserID)

        pairKey = self._match_key(userID, otherUserID)
        userRequiresConfirmation = await self._match_confirmation_required(userID)
        otherRequiresConfirmation = await self._match_confirmation_required(otherUserID)

        if not userRequiresConfirmation and not otherRequiresConfirmation:
            # Auto-match path: both players have confirmation disabled, so no pending state is needed
            # Confirmed embeds are built directly here
            try:
                await user.send(embed = await self.build_confirmed_match_embed(user, otherUser, gameName))
            except discord.Forbidden:
                return False

            try:
                await otherUser.send(embed = await self.build_confirmed_match_embed(otherUser, user, gameName))
            except discord.Forbidden:
                # First user already got DM — notify them it was canceled
                try:
                    await user.send("Match canceled — the other player's DMs are closed.")
                except discord.Forbidden:
                    pass
                return False

            await self.record_match(userID, otherUserID, gameName)
            return True

        # Build pending embeds only when confirmation is required
        # avoids constructing embeds that would be immediately discarded in the auto-match path
        userEmbed = await self.build_match_embed(user, otherUser, gameName)
        otherUserEmbed = await self.build_match_embed(otherUser, user, gameName)

        # Pending-match path: at least one player must confirm before the match is finalized
        self.pendingMatches[pairKey] = {
            "gameName": gameName,
            "choices": {},
            "messages": {},
            "views": {},
            "resolved": False,
            "user": user,
            "otherUser": otherUser,
        }

        # If a user does not need to confirm, treat that side as already accepted
        if not userRequiresConfirmation:
            self.pendingMatches[pairKey]["choices"][userID] = "accepted"
        if not otherRequiresConfirmation:
            self.pendingMatches[pairKey]["choices"][otherUserID] = "accepted"

        userView = self._create_confirmation_view(pairKey, userID, otherUserID, gameName) if userRequiresConfirmation else None
        otherView = self._create_confirmation_view(pairKey, otherUserID, userID, gameName) if otherRequiresConfirmation else None

        userMessage: discord.Message | None = None

        try:
            if userView is None:
                # No button view means this user already auto-accepted, so send a plain embed
                userMessage = await user.send(embed=userEmbed)
            else:
                # Confirmation required: include buttons so the user can accept or decline
                userMessage = await user.send(embed=userEmbed, view=userView)
            self.pendingMatches[pairKey]["messages"][userID] = userMessage
            if userView is not None:
                self.pendingMatches[pairKey]["views"][userID] = userView
        except discord.Forbidden:
            self.pendingMatches.pop(pairKey, None)
            return False
        except discord.HTTPException:
            self.pendingMatches.pop(pairKey, None)
            return False

        try:
            if otherView is None:
                # Same behavior for the second user: plain embed when auto-accepted
                otherMessage = await otherUser.send(embed=otherUserEmbed)
            else:
                # Confirmation required for this user, so attach the per-user view
                otherMessage = await otherUser.send(embed=otherUserEmbed, view=otherView)
            self.pendingMatches[pairKey]["messages"][otherUserID] = otherMessage
            if otherView is not None:
                self.pendingMatches[pairKey]["views"][otherUserID] = otherView
        except discord.Forbidden:
            self._disable_view(userView)
            await self._edit_message(
                userMessage,
                "Match canceled because the other player could not receive the DM.",
                userView,
            )
            self.pendingMatches.pop(pairKey, None)
            return False
        except discord.HTTPException:
            self._disable_view(userView)
            await self._edit_message(
                userMessage,
                "Match canceled because the other player could not receive the DM.",
                userView,
            )
            self.pendingMatches.pop(pairKey, None)
            return False

        return True
    
    async def on_session_ended(self, departedUserID: int, gameName: str) -> None:
        # When a player leaves a game, check if any remaining players
        # need to be re-queued for a new match
        # Cooldown from is_eligible still applies — players must wait
        # their configured cooldown before being matched again
        eligibleUsers = self.get_eligible_users(gameName)

        for userID in eligibleUsers:
            if userID == departedUserID:
                continue

            # Skip users who already have an active pending match for any game
            # to avoid sending a second match DM while they're still deciding
            hasActivePendingMatch = any(
                userID in pair for pair in self.pendingMatches
            )
            if hasActivePendingMatch:
                continue

            await self.check_for_match(userID, gameName)
    
    @app_commands.command(name="match-history", description="View your recent matches")
    async def matchHistory(self, interaction: discord.Interaction) -> None:
        userID = interaction.user.id
        await db.check_user(userID)
        
        matches = await db.get_match_history(userID)

        if not matches:
            await interaction.response.send_message("You have no match history yet.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Your Match History",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        for match in matches:
            otherUserID = match["user_id_2"] if match["user_id_1"] == userID else match["user_id_1"]
            otherUser = self.bot.get_user(otherUserID)
            otherName = otherUser.display_name if otherUser else f"User {otherUserID}"
            embed.add_field(
                name=f"{otherName} — {match['game_name']}",
                value=f"<t:{int(match['matched_at'].timestamp())}:R>",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="status", description="See who is currently playing what game")
    async def status(self, interaction: discord.Interaction) -> None:
        sessions = await db.get_all_active_sessions()

        if not sessions:
            await interaction.response.send_message("No one is currently being tracked.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Currently Playing",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        for session in sessions:
            user = self.bot.get_user(session["user_id"])
            userName = user.display_name if user else f"User {session['user_id']}"
            embed.add_field(name=userName, value=session["game_name"], inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Matching(bot))