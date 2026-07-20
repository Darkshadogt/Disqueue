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

CREATE OR REPLACE FUNCTION notify_preferences_change() RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify(
    'preferences_updated',
    json_build_object('user_id', NEW.user_id)::text
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_preferences_notify
AFTER UPDATE ON user_preferences
FOR EACH ROW
EXECUTE FUNCTION notify_preferences_change();


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

CREATE TABLE IF NOT EXISTS notifications (
    id          BIGSERIAL PRIMARY KEY,
    user_id     TEXT REFERENCES users(user_id) ON DELETE CASCADE,
    type        TEXT NOT NULL,   -- 'match', 'server_added', 'server_removed', 'preference_alert'
    title       TEXT NOT NULL,
    body        TEXT,
    read        BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_unread
    ON notifications (user_id, read, created_at DESC);

CREATE OR REPLACE FUNCTION notify_live_session_change() RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify('live_session_changed', '1');
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
 
CREATE TRIGGER game_sessions_notify_insert
AFTER INSERT ON game_sessions
FOR EACH ROW
EXECUTE FUNCTION notify_live_session_change();
 
CREATE TRIGGER game_sessions_notify_update
AFTER UPDATE ON game_sessions
FOR EACH ROW
EXECUTE FUNCTION notify_live_session_change();