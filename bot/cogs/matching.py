from discord.ext import commands
from discord import app_commands
import discord
import asyncio
import datetime
from zoneinfo import ZoneInfo
from config import DISQUEUE_SERVER_INVITE, DISQUEUE_GUILD_ID, DISQUEUE_MATCHES_CHANNEL_ID, DISQUEUE_LOGO_URL
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

EMBED_COLORS = {
    "pending": 0xFFB830,    # --color-pending (yellow) — awaiting a response
    "accepted": 0xFFB830,   # same yellow — still in progress until both sides confirm
    "confirmed": 0x0FFB8A,  # --color-match (green)
    "declined": 0xFF4D6A,   # --color-declined (red)
    "expired": 0x8888AA,    # --color-muted (grey)
    "brand": 0x8B72FF,      # --color-brand-400 — used for neutral, non-status embeds
}

CONFIRMATION_TIMEOUT_SECONDS = 300

STATUS_STYLE = {
    "Pending other player's confirmation": ("Awaiting confirmation", "pending"),
    "Accepted — waiting for the other user": ("Accepted — waiting on the other player", "accepted"),
    "Confirmed": ("Confirmed", "confirmed"),
    "Declined": ("Declined", "declined"),
    "Declined by the other user": ("Declined by the other player", "declined"),
    "Expired after 5 minutes": ("Expired", "expired"),
}

# Keeps every status embed the same shape — pending, declined, and expired
# all get a "Next Step" field, just with different guidance. Confirmed skips
# it since the Connect field already tells the player what to do next
NEXT_STEP_TEXT = {
    "pending": "Use the buttons below to accept or decline. No response before it expires counts as a decline.",
    "accepted": "Use the buttons below to accept or decline. No response before it expires counts as a decline.",
    "declined": "This match won't be created. You'll be considered for a new match automatically the next time you're eligible.",
    "expired": "Neither side responded in time, so this match won't be created. You'll be considered for a new match automatically.",
}


class MatchConfirmationView(discord.ui.View):
    # Per-user confirmation view shown in DM for a single pending match
    def __init__(
        self,
        matching: "Matching",
        pairKey: frozenset[int],
        userID: int,
        otherUserID: int,
        gameName: str,
        timeout: float = CONFIRMATION_TIMEOUT_SECONDS,
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
        # Expired requests are cleaned up by the cog so they don't stay pending forever
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
        self._limitNotifiedToday: set[tuple[int, object]] = set()

    def _icon_url(self) -> str | None:
        # Prefer the hosted logo; fall back to the bot's avatar if it isn't set
        if DISQUEUE_LOGO_URL:
            return DISQUEUE_LOGO_URL
        return self.bot.user.display_avatar.url if self.bot.user else None

    def _themed_embed(
        self,
        title: str,
        description: str | None = None,
        color: int = EMBED_COLORS["brand"],
    ) -> discord.Embed:
        # Shared base for every non-match-flow embed (history, status, errors)
        # so they all carry the same author/footer/color conventions
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        embed.set_author(name="Disqueue", icon_url=self._icon_url())
        embed.set_footer(text="Disqueue — Cross Server Matchmaking", icon_url=self._icon_url())
        return embed

    def _format_profile_block(self, preferences: dict | None) -> str:
        # Only surface fields the user actually filled in — an empty "Region:
        # Not set" line adds noise without adding information
        if preferences is None:
            return "*No profile info shared*"

        lines = []
        region = preferences.get("region")
        bio = preferences.get("bio")

        if region:
            lines.append(f"**Region:** {region}")
        if bio:
            lines.append(f"**Bio:** {bio}")

        return "\n".join(lines) if lines else "*No profile info shared*"

    async def build_match_embed(
        self,
        user: discord.User,
        otherUser: discord.User,
        gameName: str,
        statusText: str = "Pending other player's confirmation",
        expiresAt: datetime.datetime | None = None,
    ) -> discord.Embed:
        userPreferences = await db.get_preferences(str(user.id))
        otherUserPreferences = await db.get_preferences(str(otherUser.id))

        statusLabel, colorKey = STATUS_STYLE.get(statusText, ("Awaiting confirmation", "pending"))
        color = EMBED_COLORS[colorKey]
        awaitingResponse = colorKey in ("pending", "accepted")

        embed = discord.Embed(
            title="Match Found",
            url=DISQUEUE_SERVER_INVITE,
            description=f"You and **{otherUser.display_name}** are both playing **{gameName}** right now.",
            color=color,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )

        embed.set_author(name="Disqueue", icon_url=self._icon_url())
        embed.set_thumbnail(url=otherUser.display_avatar.url)

        def pad_row_to_three() -> None:
            remainder = len(embed.fields) % 3
            if remainder != 0:
                for _ in range(3 - remainder):
                    embed.add_field(name="\u200b", value="\u200b", inline=True)

        def add_metadata_row() -> None:
            embed.add_field(name="Game", value=f"**{gameName}**", inline=True)
            embed.add_field(name="Status", value=statusLabel, inline=True)
            if awaitingResponse and expiresAt is not None:
                embed.add_field(name="Expires", value=f"<t:{int(expiresAt.timestamp())}:R>", inline=True)
            pad_row_to_three()

        def add_players_row() -> None:
            embed.add_field(
                name="You",
                value=f"**{user.display_name}**\n{self._format_profile_block(userPreferences)}",
                inline=True,
            )
            embed.add_field(
                name="Duo",
                value=f"**{otherUser.display_name}**\n{self._format_profile_block(otherUserPreferences)}",
                inline=True,
            )
            pad_row_to_three()

        playersFirst = colorKey in ("accepted", "confirmed")

        if playersFirst:
            add_players_row()
            add_metadata_row()
        else:
            add_metadata_row()
            add_players_row()

        nextStepText = NEXT_STEP_TEXT.get(colorKey)
        if nextStepText:
            embed.add_field(name="Next Step", value=nextStepText, inline=False)

        embed.set_footer(text="Disqueue — Cross Server Matchmaking", icon_url=self._icon_url())
        return embed

    async def build_confirmed_match_embed(self, user: discord.User, otherUser: discord.User, gameName: str) -> discord.Embed:
        # Reuse the base embed and append connection details, which are only
        # relevant once both sides have confirmed
        embed = await self.build_match_embed(user, otherUser, gameName, statusText="Confirmed")
        embed.add_field(
            name="Connect",
            value=(
                f"**Official Server:** {DISQUEUE_SERVER_INVITE}\n"
                f"**Add Directly:** `{otherUser.name}`"
            ),
            inline=False,
        )
        return embed

    def _build_thread_embed(
        self,
        user: discord.User,
        otherUser: discord.User,
        gameName: str,
    ) -> discord.Embed:
        # Shorter public-facing embed for the official server thread with no bios/regions,
        # since that's private profile info meant for DMs only
        embed = discord.Embed(
            title="Match Confirmed",
            description=f"{user.mention} and {otherUser.mention} are set up to play **{gameName}** together.",
            color=EMBED_COLORS["brand"],
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        embed.set_author(name="Disqueue", icon_url=self._icon_url())
        embed.set_thumbnail(url=self._icon_url())

        # Top row: quick-glance metadata, same shape as the DM embed
        embed.add_field(name="Game", value=f"**{gameName}**", inline=True)
        embed.add_field(name="Players", value=f"{user.mention}\n{otherUser.mention}", inline=True)
        embed.add_field(name="Visibility", value="Private to you two", inline=True)

        embed.add_field(
            name="Getting Started",
            value=(
                "Say hello, then jump into a voice channel or party up in-game.\n"
                "Run `/match-history` in either server anytime to revisit this match."
            ),
            inline=False,
        )
        embed.add_field(
            name="Notes",
            value=(
                "This thread auto-archives after an hour of inactivity — sending a message reopens it.\n"
                "Having an issue with your duo? Use `/support` to reach the team."
            ),
            inline=False,
        )

        embed.set_footer(text="Disqueue — Cross Server Matchmaking", icon_url=self._icon_url())
        return embed

    async def announce_match_thread(self, user: discord.User, otherUser: discord.User, gameName: str) -> None:
        # Best-effort: posting the announcement is a nice-to-have, so any
        # failure here should never affect the actual match outcome
        officialGuild = self.bot.get_guild(DISQUEUE_GUILD_ID)
        if officialGuild is None:
            return

        channel = officialGuild.get_channel(DISQUEUE_MATCHES_CHANNEL_ID)
        if not isinstance(channel, discord.TextChannel):
            return

        try:
            # Private threads keep the conversation between just the two matched
            # users, requires the bot to have "Create Private Threads" permission
            thread = await channel.create_thread(
                name=f"{user.display_name} & {otherUser.display_name} · {gameName}",
                type=discord.ChannelType.private_thread,
                invitable=False,
                auto_archive_duration=60,
            )
            await thread.add_user(user)
            await thread.add_user(otherUser)
            await thread.send(
                content=f"{user.mention} {otherUser.mention}",
                embed=self._build_thread_embed(user, otherUser, gameName),
            )
        except discord.HTTPException:
            pass

    def _match_key(self, userID: int, otherUserID: int) -> frozenset[int]:
        return frozenset((userID, otherUserID))

    async def _match_confirmation_required(self, userID: int) -> bool:
        preferences = await db.get_preferences(str(userID))
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
        presenceCog = self.bot.get_cog("Presence")
        if not presenceCog:
            return []
        session = presenceCog.session
        return [userID for userID, games in session.items() if gameName in games]

    async def is_in_dnd_window(self, userID: int) -> bool:
        preferences = await db.get_preferences(str(userID))
        if preferences is None:
            return False

        timezone = preferences["timezone"]
        startTime = preferences["dnd_start"]
        endTime = preferences["dnd_end"]

        if startTime is None or endTime is None:
            return False

        tz = TIMEZONE.get(timezone, ZoneInfo("UTC"))
        currentHour = datetime.datetime.now(tz).hour
        startHour = int(startTime)
        endHour = int(endTime)

        if startHour < endHour:
            return startHour <= currentHour < endHour
        return currentHour >= startHour or currentHour < endHour

    async def is_on_cooldown(self, userID: int, cooldownMinutes: int) -> bool:
        lastMatch = await db.get_last_match_time(str(userID))
        if lastMatch is None:
            return False
        elapsed = datetime.datetime.now(datetime.timezone.utc) - lastMatch
        return elapsed < datetime.timedelta(minutes=cooldownMinutes)

    async def is_under_daily_limit(self, userID: int, matchLimit: int) -> bool:
        todayCount = await db.get_match_count_today(str(userID))
        return todayCount < matchLimit

    async def is_eligible(self, userID: int, otherUserID: int, gameName: str) -> bool:
        # Applies every matching rule before a DM is ever sent
        await db.check_user(str(userID))
        await db.check_user(str(otherUserID))

        userPreferences = await db.get_preferences(str(userID))
        otherUserPreferences = await db.get_preferences(str(otherUserID))

        if userPreferences is None or otherUserPreferences is None:
            return False

        if not userPreferences["enabled"] or not otherUserPreferences["enabled"]:
            return False

        if not userPreferences["dm_enabled"] or not otherUserPreferences["dm_enabled"]:
            return False

        if await self.is_in_dnd_window(userID) or await self.is_in_dnd_window(otherUserID):
            return False

        userBlocklist = await db.get_blocklist(str(userID))
        otherBlocklist = await db.get_blocklist(str(otherUserID))
        if userID in otherBlocklist or otherUserID in userBlocklist:
            return False

        if await self.is_on_cooldown(userID, userPreferences["match_cooldown"]):
            return False
        if await self.is_on_cooldown(otherUserID, otherUserPreferences["match_cooldown"]):
            return False

        if userPreferences["match_limit"] is not None:
            if not await self.is_under_daily_limit(userID, userPreferences["match_limit"]):
                await self._notify_limit_reached(userID, userPreferences["match_limit"])
                return False
        if otherUserPreferences["match_limit"] is not None:
            if not await self.is_under_daily_limit(otherUserID, otherUserPreferences["match_limit"]):
                await self._notify_limit_reached(otherUserID, otherUserPreferences["match_limit"])
                return False

        userLanguage = userPreferences["language"]
        otherUserLanguage = otherUserPreferences["language"]
        if userLanguage is not None and otherUserLanguage is not None and userLanguage != otherUserLanguage:
            return False

        userGameMode = userPreferences["game_mode"]
        otherUserGameMode = otherUserPreferences["game_mode"]
        if userGameMode != "any" and otherUserGameMode != "any" and userGameMode != otherUserGameMode:
            return False

        userRegion = userPreferences["region"]
        otherUserRegion = otherUserPreferences["region"]
        bothStrictlyRanked = userGameMode == "ranked" and otherUserGameMode == "ranked"
        bothHaveRegion = userRegion is not None and otherUserRegion is not None
        if bothStrictlyRanked and bothHaveRegion and userRegion != otherUserRegion:
            return False

        return True

    async def check_for_match(self, userID: int, gameName: str) -> None:
        # Find the first eligible partner and kick off the confirmation flow
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

            if await self.send_match_dm(userID, otherUserID, gameName):
                break

    async def record_match(self, userID: int, otherUserID: int, gameName: str) -> None:
        matchedAt = datetime.datetime.now(datetime.timezone.utc)

        userSession = await db.get_session_start(str(userID), gameName)
        otherSession = await db.get_session_start(str(otherUserID), gameName)

        waitTimeUser = int((matchedAt - userSession["started_at"]).total_seconds()) if userSession else None
        waitTimeOther = int((matchedAt - otherSession["started_at"]).total_seconds()) if otherSession else None

        crossServer = (
            userSession is not None
            and otherSession is not None
            and userSession["guild_id"] != otherSession["guild_id"]
        )

        await db.record_match(
            str(userID),
            str(otherUserID),
            gameName,
            cross_server=crossServer,
            wait_time_1=waitTimeUser,
            wait_time_2=waitTimeOther,
        )

        await db.create_notification(str(userID), "match", "New match found", f"You matched with someone for {gameName}.")
        await db.create_notification(str(otherUserID), "match", "New match found", f"You matched with someone for {gameName}.")

    async def _notify_limit_reached(self, userID: int, limit: int) -> None:
        # Only notify once per day per user which resets naturally since
        # the underlying daily count also resets each day
        today = datetime.datetime.now(datetime.timezone.utc).date()
        key = (userID, today)
        if key in self._limitNotifiedToday:
            return
        self._limitNotifiedToday.add(key)

        await db.create_notification(
            str(userID),
            "preference_alert",
            "Daily match limit reached",
            f"You've hit your daily limit of {limit} matches. New matches will resume tomorrow.",
        )

        try:
            user = self.bot.get_user(userID) or await self.bot.fetch_user(userID)
            embed = discord.Embed(
                title="Daily Match Limit Reached",
                description=f"You've hit your daily limit of **{limit}** matches. New matches will resume tomorrow.",
                color=EMBED_COLORS["pending"],
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embed.set_author(name="Disqueue", icon_url=self._icon_url())
            embed.set_footer(text="Disqueue — Cross Server Matchmaking", icon_url=self._icon_url())
            await user.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException, discord.NotFound):
            pass

    async def handle_match_response(
        self,
        interaction: discord.Interaction,
        pairKey: frozenset[int],
        userID: int,
        accepted: bool,
        view: MatchConfirmationView,
    ) -> None:
        state = self.pendingMatches.get(pairKey)
        if state is None or state.get("resolved"):
            await interaction.response.send_message("This match is no longer active.", ephemeral=True)
            return

        # Serialize against the other user's response — without this, two
        # near-simultaneous accepts can both read "not yet resolved" and both
        # run the finalize block, causing duplicate match records/threads or
        # one side getting stuck on the "waiting" embed if the other errors mid-finalize
        lock: asyncio.Lock = state["lock"]
        async with lock:
            # Re-fetch in case the match resolved while we were waiting on the lock
            state = self.pendingMatches.get(pairKey)
            if state is None or state.get("resolved"):
                await interaction.response.send_message("This match is no longer active.", ephemeral=True)
                return

            gameName = state["gameName"]
            choices: dict[int, str] = state["choices"]
            messages: dict[int, discord.Message] = state["messages"]
            views: dict[int, MatchConfirmationView] = state["views"]
            otherUserID = next(uid for uid in pairKey if uid != userID)

            storedUser: discord.User = state["user"]
            storedOtherUser: discord.User = state["otherUser"]
            currentUser = storedUser if storedUser.id == userID else storedOtherUser
            currentOtherUser = storedOtherUser if storedUser.id == userID else storedUser

            choices[userID] = "accepted" if accepted else "declined"
            self._disable_view(view)

            if not accepted:
                # A single decline cancels the pair immediately
                state["resolved"] = True
                declinedEmbed = await self.build_match_embed(currentUser, currentOtherUser, gameName, statusText="Declined")
                await interaction.response.edit_message(view=view, embed=declinedEmbed)

                otherMessage = messages.get(otherUserID)
                otherView = views.get(otherUserID)
                self._disable_view(otherView)
                declinedOtherEmbed = await self.build_match_embed(
                    currentOtherUser, currentUser, gameName, statusText="Declined by the other user"
                )
                await self._edit_message(otherMessage, None, otherView, declinedOtherEmbed)
                self.pendingMatches.pop(pairKey, None)
                return

            acceptedEmbed = await self.build_match_embed(
                currentUser,
                currentOtherUser,
                gameName,
                statusText="Accepted — waiting for the other user",
                expiresAt=state.get("expiresAt"),
            )
            await interaction.response.edit_message(view=view, embed=acceptedEmbed)

            if len(choices) != 2 or any(choice != "accepted" for choice in choices.values()):
                return

            # Both sides accepted, finalize and tear down the pending state
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
            await self.announce_match_thread(currentUser, currentOtherUser, gameName)

            self.pendingMatches.pop(pairKey, None)

    async def handle_match_timeout(
        self,
        pairKey: frozenset[int],
        userID: int,
        otherUserID: int,
        view: MatchConfirmationView,
    ) -> None:
        state = self.pendingMatches.get(pairKey)
        if state is None or state.get("resolved"):
            return

        lock: asyncio.Lock = state["lock"]
        async with lock:
            # Re-fetch in case an accept/decline resolved this match while
            # we were waiting on the lock
            state = self.pendingMatches.get(pairKey)
            if state is None or state.get("resolved"):
                return
            state["resolved"] = True

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

            expiredUserEmbed = await self.build_match_embed(currentUser, currentOtherUser, state["gameName"], statusText="Expired after 5 minutes")
            expiredOtherEmbed = await self.build_match_embed(currentOtherUser, currentUser, state["gameName"], statusText="Expired after 5 minutes")

            self._disable_view(currentView)
            self._disable_view(otherView)

            await self._edit_message(currentMessage, None, currentView, expiredUserEmbed)
            await self._edit_message(otherMessage, None, otherView, expiredOtherEmbed)
            self.pendingMatches.pop(pairKey, None)

    async def send_match_dm(self, userID: int, otherUserID: int, gameName: str) -> bool:
        # Three possible outcomes:
        # 1. Neither user requires confirmation — match sent and recorded immediately
        # 2. One or both require confirmation — DM sent with Accept/Decline buttons
        # 3. The request later resolves via accept, decline, or timeout cleanup
        user = await self.bot.fetch_user(userID)
        otherUser = await self.bot.fetch_user(otherUserID)

        pairKey = self._match_key(userID, otherUserID)
        userRequiresConfirmation = await self._match_confirmation_required(userID)
        otherRequiresConfirmation = await self._match_confirmation_required(otherUserID)

        if not userRequiresConfirmation and not otherRequiresConfirmation:
            try:
                await user.send(embed=await self.build_confirmed_match_embed(user, otherUser, gameName))
            except discord.Forbidden:
                return False

            try:
                await otherUser.send(embed=await self.build_confirmed_match_embed(otherUser, user, gameName))
            except discord.Forbidden:
                try:
                    await user.send("Match canceled — the other player's DMs are closed.")
                except discord.Forbidden:
                    pass
                return False

            await self.record_match(userID, otherUserID, gameName)
            await self.announce_match_thread(user, otherUser, gameName)
            return True

        expiresAt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=CONFIRMATION_TIMEOUT_SECONDS
        )

        userEmbed = await self.build_match_embed(user, otherUser, gameName, expiresAt=expiresAt)
        otherUserEmbed = await self.build_match_embed(otherUser, user, gameName, expiresAt=expiresAt)

        self.pendingMatches[pairKey] = {
            "gameName": gameName,
            "choices": {},
            "messages": {},
            "views": {},
            "resolved": False,
            "user": user,
            "otherUser": otherUser,
            "expiresAt": expiresAt,
            "lock": asyncio.Lock(),
        }

        if not userRequiresConfirmation:
            self.pendingMatches[pairKey]["choices"][userID] = "accepted"
        if not otherRequiresConfirmation:
            self.pendingMatches[pairKey]["choices"][otherUserID] = "accepted"

        userView = self._create_confirmation_view(pairKey, userID, otherUserID, gameName) if userRequiresConfirmation else None
        otherView = self._create_confirmation_view(pairKey, otherUserID, userID, gameName) if otherRequiresConfirmation else None

        userMessage: discord.Message | None = None

        try:
            userMessage = await (
                user.send(embed=userEmbed, view=userView) if userView is not None else user.send(embed=userEmbed)
            )
            self.pendingMatches[pairKey]["messages"][userID] = userMessage
            if userView is not None:
                self.pendingMatches[pairKey]["views"][userID] = userView
        except (discord.Forbidden, discord.HTTPException):
            self.pendingMatches.pop(pairKey, None)
            return False

        try:
            otherMessage = await (
                otherUser.send(embed=otherUserEmbed, view=otherView) if otherView is not None else otherUser.send(embed=otherUserEmbed)
            )
            self.pendingMatches[pairKey]["messages"][otherUserID] = otherMessage
            if otherView is not None:
                self.pendingMatches[pairKey]["views"][otherUserID] = otherView
        except (discord.Forbidden, discord.HTTPException):
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
        # When a player stops playing, re-check remaining players for a new match.
        # Cooldowns from is_eligible still apply.
        eligibleUsers = self.get_eligible_users(gameName)

        for userID in eligibleUsers:
            if userID == departedUserID:
                continue

            hasActivePendingMatch = any(userID in pair for pair in self.pendingMatches)
            if hasActivePendingMatch:
                continue

            await self.check_for_match(userID, gameName)

    # ---------------------------------------------------------------------
    # Slash commands
    # ---------------------------------------------------------------------

    @app_commands.command(name="match-history", description="View your recent matches")
    async def matchHistory(self, interaction: discord.Interaction) -> None:
        # Defer immediately — Discord only gives a 3-second window to
        # acknowledge an interaction, and DB calls can occasionally run long
        # Without this, a slow or failing query shows the user "the
        # application did not respond" instead of an actual message
        await interaction.response.defer(ephemeral=True)

        userID = interaction.user.id

        try:
            await db.check_user(str(userID))
            matches = await db.get_match_history(str(userID))

            if not matches:
                embed = self._themed_embed(
                    "Match History",
                    "You have no match history yet — get playing to start matching.",
                    color=EMBED_COLORS["expired"],
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            embed = self._themed_embed("Your Match History")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)

            for match in matches:
                # get_match_history's query only returns other_user_id (already
                # resolved via CASE against the caller's own ID) — it never
                # returns raw user_id_1/user_id_2, so don't try to read those here
                otherUserID = int(match["other_user_id"])
                otherUser = self.bot.get_user(otherUserID)
                otherName = (
                    otherUser.display_name
                    if otherUser
                    else (match["other_display_name"] or f"User {otherUserID}")
                )
                crossServerTag = " · Cross-Server" if match.get("cross_server") else ""
                embed.add_field(
                    name=f"{otherName} — {match['game_name']}{crossServerTag}",
                    value=f"Matched <t:{int(match['matched_at'].timestamp())}:R>",
                    inline=False,
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception:
            # Covers the whole command body now, not just the initial DB
            # calls — a bad row or formatting error here previously crashed
            # past defer() with no followup ever sent, leaving the user
            # stuck on "thinking..." indefinitely
            errorEmbed = self._themed_embed(
                "Match History",
                "Something went wrong loading your match history. Please try again in a moment.",
                color=EMBED_COLORS["declined"],
            )
            await interaction.followup.send(embed=errorEmbed, ephemeral=True)

    @app_commands.command(name="status", description="See who is currently playing what game")
    async def status(self, interaction: discord.Interaction) -> None:
        # Same reasoning as match-history: defer first so a slow query never
        # surfaces as an unresponsive-application error to the user
        await interaction.response.defer(ephemeral=True)

        try:
            sessions = await db.get_all_active_sessions()
        except Exception:
            errorEmbed = self._themed_embed(
                "Currently Playing",
                "Something went wrong loading active sessions. Please try again in a moment.",
                color=EMBED_COLORS["declined"],
            )
            await interaction.followup.send(embed=errorEmbed, ephemeral=True)
            return

        if not sessions:
            embed = self._themed_embed(
                "Currently Playing",
                "No one is currently being tracked. Run `/enable` to join the queue.",
                color=EMBED_COLORS["expired"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = self._themed_embed("Currently Playing")

        gamesToPlayers: dict[str, list[str]] = {}
        for session in sessions:
            user = self.bot.get_user(session["user_id"])
            userName = user.display_name if user else f"User {session['user_id']}"
            gamesToPlayers.setdefault(session["game_name"], []).append(userName)

        for gameName, players in gamesToPlayers.items():
            embed.add_field(name=gameName, value="\n".join(players), inline=True)

        embed.set_footer(text=f"Disqueue — {len(sessions)} Player(s) Active", icon_url=self._icon_url())
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Matching(bot))