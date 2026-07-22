import { useEffect, useState } from "react";
import AppShell from "../components/AppShell";
import { Skeleton } from "../components/Skeleton";
import { ErrorState } from "../components/ErrorState";
import api from "../api";
import { useRealTime } from "../contexts/RealTimeContext";
import { getCurrentUserId } from "../utils/jwt";
import {
  IconUsersGroup,
  IconClock,
  IconActivity,
  IconBolt,
  IconServer,
  IconTrendingUp,
} from "@tabler/icons-react";

const POLL_INTERVAL_MS = 10000; // fallback in case the websocket drops
const TICK_INTERVAL_MS = 1000; // re-render cadence for the elapsed-time counters

function formatElapsed(startedAt) {
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(startedAt).getTime()) / 1000));
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function avgCurrentWait(sessions) {
  if (sessions.length === 0) return "—";
  const totalSeconds = sessions.reduce(
    (sum, s) => sum + Math.max(0, Math.floor((Date.now() - new Date(s.started_at).getTime()) / 1000)),
    0
  );
  const avg = Math.round(totalSeconds / sessions.length);
  return avg < 60 ? `${avg}s` : `${Math.floor(avg / 60)}m ${avg % 60}s`;
}

function StatPill({ icon: Icon, label, value, accent }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-void-border bg-void-card/50 px-4 py-3 backdrop-blur-sm">
      <div className={`flex h-9 w-9 items-center justify-center rounded-xl ring-1 ${accent}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div>
        <p className="text-lg font-bold leading-tight text-primary tabular-nums">{value}</p>
        <p className="text-[11px] text-muted leading-tight">{label}</p>
      </div>
    </div>
  );
}

// Row-shaped placeholder for a queue pool card, shown while sessions load
function QueueRowSkeleton() {
  return (
    <div className="rounded-2xl border border-void-border bg-void-card/50 p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-10 rounded-xl" />
          <Skeleton className="h-4 w-24" />
        </div>
        <Skeleton className="h-6 w-8" />
      </div>
      <Skeleton className="mt-3 h-1 w-full rounded-full" />
    </div>
  );
}

export function LiveContent() {
  const [sessions, setSessions] = useState([]);
  const [currentUserId, setCurrentUserId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // Only used to force a re-render each second so elapsed-time labels stay live
  const [, forceTick] = useState(0);
  const { lastEvent } = useRealTime();

  const loadLiveData = async () => {
    try {
      const res = await api.get("/live");
      setSessions(Array.isArray(res.data) ? res.data : []);
      setError(null);
    } catch {
      setError("Failed to load live status.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLiveData();
    const pollId = setInterval(loadLiveData, POLL_INTERVAL_MS);
    return () => clearInterval(pollId);
  }, []);

  // Instant refetch the moment a session starts or ends anywhere
  useEffect(() => {
    if (lastEvent?.type === "live_session_changed") {
      loadLiveData();
    }
  }, [lastEvent]);

  useEffect(() => {
    const tickId = setInterval(() => forceTick((t) => t + 1), TICK_INTERVAL_MS);
    return () => clearInterval(tickId);
  }, []);

  useEffect(() => {
    setCurrentUserId(getCurrentUserId());
  }, []);

  const pool = {};
  for (const s of sessions) pool[s.game_name] = (pool[s.game_name] || 0) + 1;
  const poolEntries = Object.entries(pool).sort((a, b) => b[1] - a[1]);

  const mySessions = sessions.filter((s) => s.user_id === currentUserId);
  const myGames = new Set(mySessions.map((s) => s.game_name));
  const totalPlayers = sessions.length;
  const uniqueGames = poolEntries.length;
  const avgWait = avgCurrentWait(sessions);

  if (error) {
    return (
      <ErrorState message={error} onRetry={loadLiveData} />
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-end">
        <div className="flex items-center gap-2 rounded-xl border border-match/30 bg-match/5 px-3.5 py-2">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-match opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-match" />
          </span>
          <span className="text-sm font-medium text-match">{loading ? "Syncing…" : `${totalPlayers} active`}</span>
        </div>
      </div>

      {!loading && (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          <StatPill icon={IconUsersGroup} label="Players in queue" value={totalPlayers} accent="bg-brand-500/10 ring-brand-500/20 text-brand-400" />
          <StatPill icon={IconActivity} label="Active games" value={uniqueGames} accent="bg-neon-500/10 ring-neon-500/20 text-neon-400" />
          <StatPill icon={IconClock} label="Avg. current wait" value={avgWait} accent="bg-accent-500/10 ring-accent-500/20 text-accent-400" />
          <StatPill icon={IconServer} label="Your queues" value={mySessions.length} accent="bg-match/10 ring-match/20 text-match" />
        </div>
      )}

      {loading && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {[0, 1, 2, 3].map((i) => (
            <QueueRowSkeleton key={i} />
          ))}
        </div>
      )}

      {!loading && (
        <div className="space-y-8">
          {mySessions.length > 0 && (
            <section>
              <h2 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-brand-400">
                <IconClock className="h-4 w-4" />
                You're currently in queue
              </h2>
              <div className="space-y-3">
                {mySessions.map((session) => (
                  <div
                    key={session.game_name}
                    className="group relative overflow-hidden rounded-2xl border border-brand-400/30 bg-gradient-to-r from-brand-500/10 via-void-card to-void-card p-5 transition-all hover:border-brand-400/50"
                  >
                    <div className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-brand-500/15 blur-2xl opacity-60 transition-opacity group-hover:opacity-100" />
                    <div className="relative flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-500/15 ring-1 ring-brand-500/30">
                          <IconClock className="h-5 w-5 text-brand-400" />
                        </div>
                        <div>
                          <p className="font-semibold text-primary">{session.game_name}</p>
                          <p className="text-xs text-muted">Waiting for a match</p>
                        </div>
                      </div>
                      <p className="font-mono text-lg font-semibold tabular-nums text-brand-300">
                        {formatElapsed(session.started_at)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section>
            <h2 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted">
              <IconActivity className="h-4 w-4" />
              Active across all servers
            </h2>

            {poolEntries.length === 0 ? (
              <div className="relative overflow-hidden rounded-2xl border border-void-border bg-void-card/40 p-16 text-center">
                <div className="pointer-events-none absolute left-1/2 top-0 h-40 w-40 -translate-x-1/2 rounded-full bg-brand-500/5 blur-3xl" />
                <div className="relative mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-void-raised to-void-card ring-1 ring-void-border">
                  <IconUsersGroup className="h-7 w-7 text-muted" />
                </div>
                <p className="relative font-semibold text-primary">No one is currently in queue</p>
                <p className="relative mt-1.5 text-sm text-muted">Be the first — start matching from your server.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {poolEntries.map(([gameName, count]) => {
                  const includesMe = myGames.has(gameName);
                  const pct = Math.min(100, count * 10);
                  return (
                    <div
                      key={gameName}
                      className={`group relative overflow-hidden rounded-2xl border p-5 transition-all hover:-translate-y-0.5 ${
                        includesMe
                          ? "border-brand-400/30 bg-gradient-to-r from-brand-500/10 to-void-card"
                          : "border-void-border bg-void-card/50 hover:border-brand-400/30"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-void-raised ring-1 ring-void-border">
                            <IconUsersGroup className={`h-5 w-5 ${includesMe ? "text-brand-400" : "text-secondary"}`} />
                          </div>
                          <div>
                            <p className="font-medium text-primary">{gameName}</p>
                            {includesMe && <p className="text-xs font-medium text-brand-400">includes you</p>}
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xl font-bold text-primary tabular-nums">{count}</p>
                          <p className="text-[11px] text-muted">{count === 1 ? "player" : "players"}</p>
                        </div>
                      </div>
                      <div className="mt-3 h-1 overflow-hidden rounded-full bg-void-raised">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${includesMe ? "bg-gradient-to-r from-brand-400 to-neon-400" : "bg-void-border"}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {poolEntries.length > 0 && (
            <div className="flex items-center gap-2.5 rounded-2xl bg-brand-500/5 px-5 py-3.5 ring-1 ring-brand-500/20">
              <IconBolt className="h-4 w-4 shrink-0 text-brand-400" />
              <p className="text-xs text-secondary">
                Live via WebSocket, polling every <span className="font-semibold text-primary">10s</span> as fallback
              </p>
              <span className="ml-auto inline-flex items-center gap-1 text-[11px] text-muted">
                <IconTrendingUp className="h-3 w-3" /> {totalPlayers} in queue
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function Live() {
  return (
    <AppShell>
      <LiveContent />
    </AppShell>
  );
}