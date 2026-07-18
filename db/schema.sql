CREATE TABLE IF NOT EXISTS users (
    user_id                    TEXT PRIMARY KEY,
    avatar                     TEXT,
    discord_access_token       TEXT,
    discord_refresh_token      TEXT,
    discord_token_expires_at   TIMESTAMPTZ,
    created_at                 TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id                     TEXT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    enabled                     BOOLEAN DEFAULT FALSE,
    match_limit                 INTEGER DEFAULT NULL,
    match_cooldown              INTEGER DEFAULT 2,
    match_confirmation_required BOOLEAN DEFAULT FALSE,
    game_mode                   TEXT DEFAULT 'any',
    dm_enabled                  BOOLEAN DEFAULT FALSE,
    friend_online_enabled       BOOLEAN DEFAULT FALSE,
    dnd_start                   INTEGER DEFAULT NULL,
    dnd_end                     INTEGER DEFAULT NULL,
    timezone                    TEXT DEFAULT 'UTC',
    display_name                TEXT DEFAULT NULL,
    bio                         TEXT DEFAULT NULL,
    language                    TEXT DEFAULT NULL,
    region                      TEXT DEFAULT NULL,
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_blocklist (
    user_id         TEXT REFERENCES users(user_id) ON DELETE CASCADE,
    blocked_user_id TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, blocked_user_id)
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id              BIGSERIAL PRIMARY KEY,
    user_id         TEXT REFERENCES users(user_id) ON DELETE CASCADE,
    game_name       TEXT NOT NULL,
    party_size      INTEGER DEFAULT 1,
    max_party_size  INTEGER DEFAULT NULL,
    started_at      TIMESTAMPTZ NOT NULL,
    ended_at        TIMESTAMPTZ DEFAULT NULL,
    guild_id        TEXT
);

CREATE TABLE IF NOT EXISTS matches (
    id            BIGSERIAL PRIMARY KEY,
    user_id_1     TEXT REFERENCES users(user_id) ON DELETE CASCADE,
    user_id_2     TEXT REFERENCES users(user_id) ON DELETE CASCADE,
    game_name     TEXT NOT NULL,
    matched_at    TIMESTAMPTZ DEFAULT NOW(),
    cross_server  BOOLEAN DEFAULT FALSE,
    wait_time_1   INTEGER DEFAULT NULL,
    wait_time_2   INTEGER DEFAULT NULL,
    CONSTRAINT no_self_match CHECK (user_id_1 != user_id_2)
);