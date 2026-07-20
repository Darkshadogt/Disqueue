import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
pool: asyncpg.Pool | None = None

async def create_pool() -> None:
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

async def close_pool() -> None:
    global pool
    if pool:
        await pool.close()

async def create_user(user_id: str):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id)
            VALUES ($1)
            ON CONFLICT (user_id) DO NOTHING
            """,
            user_id
        )

async def get_user_profile(user_id: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT avatar FROM users WHERE user_id = $1",
            user_id
        )

async def update_user_profile(user_id: str, avatar: str):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE users
            SET avatar = $1
            WHERE user_id = $2
            """,
            avatar, user_id
        )

async def get_preferences(user_id: str) -> asyncpg.Record | None:
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM user_preferences WHERE user_id = $1",
            user_id
        )

async def create_default_preferences(user_id: str) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_preferences (user_id)
            VALUES ($1)
            ON CONFLICT (user_id) DO NOTHING
            """,
            user_id
        )

async def update_preference(user_id: str, column: str, value) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            f"UPDATE user_preferences SET {column} = $1, updated_at = NOW() WHERE user_id = $2",
            value, user_id
        )

async def reset_preferences(user_id: str) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM user_preferences WHERE user_id = $1",
            user_id
        )
        await create_default_preferences(user_id)

async def get_blocklist(user_id: str) -> list[str]:
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT blocked_user_id FROM user_blocklist WHERE user_id = $1",
            user_id
        )
        return [row["blocked_user_id"] for row in rows]

async def add_to_blocklist(user_id: str, blocked_user_id: str) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_blocklist (user_id, blocked_user_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            """,
            user_id, blocked_user_id
        )

async def remove_from_blocklist(user_id: str, blocked_user_id: str) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM user_blocklist WHERE user_id = $1 AND blocked_user_id = $2",
            user_id, blocked_user_id
        )

async def reset_blocklist(user_id: str) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM user_blocklist WHERE user_id = $1",
            user_id
        )

async def start_game_session(
    user_id: str,
    game_name: str,
    party_size: int,
    max_party_size: int | None,
    started_at,
    guild_id: str | None = None,
) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            """
            INSERT INTO game_sessions (user_id, game_name, party_size, max_party_size, started_at, guild_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            user_id, game_name, party_size, max_party_size, started_at, guild_id
        )

async def end_game_session(user_id: str, game_name: str) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE game_sessions
            SET ended_at = NOW()
            WHERE user_id = $1 AND game_name = $2 AND ended_at IS NULL
            """,
            user_id, game_name
        )

async def get_session_start(user_id: str, game_name: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT started_at, guild_id
            FROM game_sessions
            WHERE user_id = $1 AND game_name = $2 AND ended_at IS NULL
            ORDER BY started_at DESC
            LIMIT 1
            """,
            user_id, game_name
        )

async def get_active_sessions(game_name: str) -> list[asyncpg.Record]:
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT user_id, party_size, max_party_size, started_at
            FROM game_sessions
            WHERE game_name = $1 AND ended_at IS NULL
            """,
            game_name
        )

async def get_active_sessions_for_user(user_id: str) -> list[asyncpg.Record]:
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT game_name, party_size, max_party_size, started_at
            FROM game_sessions
            WHERE user_id = $1 AND ended_at IS NULL
            """,
            user_id
        )

async def get_all_active_sessions() -> list[asyncpg.Record]:
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT user_id, game_name, started_at FROM game_sessions WHERE ended_at IS NULL"
        )

async def record_match(
    user_id_1: str,
    user_id_2: str,
    game_name: str,
    cross_server: bool = False,
    wait_time_1: int | None = None,
    wait_time_2: int | None = None,
) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            """
            INSERT INTO matches (user_id_1, user_id_2, game_name, cross_server, wait_time_1, wait_time_2)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            user_id_1, user_id_2, game_name, cross_server, wait_time_1, wait_time_2
        )

async def get_match_history(user_id: str, limit: int = 10) -> list[asyncpg.Record]:
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT
                m.id,
                m.game_name,
                m.matched_at,
                m.cross_server,
                CASE WHEN m.user_id_1 = $1 THEN m.user_id_2 ELSE m.user_id_1 END AS other_user_id,
                CASE WHEN m.user_id_1 = $1 THEN m.wait_time_1 ELSE m.wait_time_2 END AS my_wait_time,
                other_user.avatar AS other_avatar,
                other_prefs.display_name AS other_display_name
            FROM matches m
            JOIN users other_user
                ON other_user.user_id = CASE WHEN m.user_id_1 = $1 THEN m.user_id_2 ELSE m.user_id_1 END
            LEFT JOIN user_preferences other_prefs
                ON other_prefs.user_id = other_user.user_id
            WHERE m.user_id_1 = $1 OR m.user_id_2 = $1
            ORDER BY m.matched_at DESC
            LIMIT $2
            """,
            user_id, limit
        )

async def get_last_match_time(user_id: str):
    async with pool.acquire() as conn:
        return await conn.fetchval(
            """
            SELECT MAX(matched_at)
            FROM matches
            WHERE user_id_1 = $1 OR user_id_2 = $1
            """,
            user_id
        )

async def get_match_count_today(user_id: str) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM matches
            WHERE (user_id_1 = $1 OR user_id_2 = $1)
            AND matched_at >= CURRENT_DATE
            """,
            user_id
        )

async def check_user(user_id: str) -> asyncpg.Record:
    await create_user(user_id)
    await create_default_preferences(user_id)
    return await get_preferences(user_id)

async def store_discord_tokens(
    user_id: str,
    access_token: str,
    refresh_token: str,
    expires_at,
) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE users
            SET discord_access_token = $1,
                discord_refresh_token = $2,
                discord_token_expires_at = $3
            WHERE user_id = $4
            """,
            access_token, refresh_token, expires_at, user_id
        )

async def get_discord_tokens(user_id: str) -> asyncpg.Record | None:
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT discord_access_token, discord_refresh_token, discord_token_expires_at
            FROM users
            WHERE user_id = $1
            """,
            user_id
        )

async def create_notification(user_id: str, type_: str, title: str, body: str | None = None) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO notifications (user_id, type, title, body)
            VALUES ($1, $2, $3, $4)
            """,
            user_id, type_, title, body
        )

async def get_notifications(user_id: str, limit: int = 20) -> list[asyncpg.Record]:
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT id, type, title, body, read, created_at
            FROM notifications
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            user_id, limit
        )

async def get_unread_count(user_id: str) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM notifications WHERE user_id = $1 AND read = FALSE",
            user_id
        )

async def mark_notification_read(user_id: str, notification_id: int) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE notifications SET read = TRUE WHERE id = $1 AND user_id = $2",
            notification_id, user_id
        )

async def mark_all_notifications_read(user_id: str) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE notifications SET read = TRUE WHERE user_id = $1 AND read = FALSE",
            user_id
        )