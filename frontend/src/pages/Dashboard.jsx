import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import AppShell from "../components/AppShell";
import { PageLoader } from "../components/PageLoader";
import { ErrorState } from "../components/ErrorState";
import api from "../api";
import { useRealTime } from "../contexts/RealTimeContext";
import {
  IconSwords,
  IconActivity,
  IconServer,
  IconArrowUpRight,
  IconArrowDownRight,
  IconBolt,
  IconTrendingUp,
  IconChevronRight,
  IconBell,
  IconCircleFilled,
} from "@tabler/icons-react";

const ACCENTS = [
  "bg-brand-500/10 ring-brand-500/20 text-brand-400",
  "bg-neon-500/10 ring-neon-500/20 text-neon-400",
  "bg-accent-500/10 ring-accent-500/20 text-accent-400",
  "bg-pending/10 ring-pending/20 text-pending",
];

// Builds an SVG path string for the mini trend line from a series of values
function sparkPath(points, w = 120, h = 36) {
  if (points.length < 2) return "";
  const max = Math.max(...points);
  const min = Math.min(...points);
  const range = max - min || 1;
  const step = w / (points.length - 1);
  return points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${(i * step).toFixed(1)} ${(h - ((p - min) / range) * h).toFixed(1)}`)
    .join(" ");
}

// Buckets matches into the last 12 calendar days for the trend sparkline
function buildMatchTrend(matches) {
  const days = [];
  for (let i = 11; i >= 0; i--) {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() - i);
    days.push(d);
  }
  return days.map((day) => {
    const next = new Date(day);
    next.setDate(next.getDate() + 1);
    return matches.filter((m) => {
      const t = new Date(m.matched_at);
      return t >= day && t < next;
    }).length;
  });
}

function timeAgo(iso) {
  if (!iso) return "No matches yet";
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function MetricCard({ icon: Icon, label, value, sub, i }) {
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-void-border bg-gradient-to-b from-void-card to-void-page p-5 transition-all duration-300 hover:-translate-y-0.5 hover:border-brand-400/30 hover:shadow-lg hover:shadow-brand-600/10">
      <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-brand-500/10 opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-100" />
      <div className={`relative flex h-10 w-10 items-center justify-center rounded-xl ring-1 ${ACCENTS[i % ACCENTS.length]}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="relative mt-4">
        <p className="text-3xl font-bold tracking-tight text-primary tabular-nums">{value}</p>
        <p className="mt-0.5 text-sm font-medium text-secondary">{label}</p>
        {sub && <p className="mt-1 text-xs text-muted">{sub}</p>}
      </div>
    </div>
  );
}

export function DashboardContent() {
  const [matches, setMatches] = useState([]);
  const [liveSessions, setLiveSessions] = useState([]);
  const [servers, setServers] = useState([]);
  const [stats, setStats] = useState({ matches_today: 0, last_match_at: null });
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { lastEvent } = useRealTime();

  const loadAll = async () => {
    try {
      setLoading(true);
      // allSettled so one failing endpoint (e.g. stats) doesn't blank the whole page
      const [matchesRes, liveRes, serversRes, statsRes, notifRes] = await Promise.allSettled([
        api.get("/users/me/matches"),
        api.get("/live"),
        api.get("/users/me/servers"),
        api.get("/users/me/stats"),
        api.get("/users/me/notifications"),
      ]);

      setMatches(matchesRes.status === "fulfilled" && Array.isArray(matchesRes.value.data) ? matchesRes.value.data : []);
      setLiveSessions(liveRes.status === "fulfilled" && Array.isArray(liveRes.value.data) ? liveRes.value.data : []);
      setServers(serversRes.status === "fulfilled" && Array.isArray(serversRes.value.data) ? serversRes.value.data : []);
      setStats(statsRes.status === "fulfilled" ? statsRes.value.data : { matches_today: 0, last_match_at: null });
      setNotifications(notifRes.status === "fulfilled" ? notifRes.value.data.notifications || [] : []);
      setUnreadCount(notifRes.status === "fulfilled" ? notifRes.value.data.unread_count ?? 0 : 0);
      setError(null);
    } catch {
      setError("Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  // Targeted refetches on realtime events instead of reloading everything
  useEffect(() => {
    if (lastEvent?.type === "match_recorded") {
      api.get("/users/me/matches").then((res) => setMatches(Array.isArray(res.data) ? res.data : [])).catch(() => {});
      api.get("/users/me/stats").then((res) => setStats(res.data)).catch(() => {});
    }
    if (lastEvent?.type === "live_session_changed") {
      api.get("/live").then((res) => setLiveSessions(Array.isArray(res.data) ? res.data : [])).catch(() => {});
    }
    if (lastEvent?.type === "notification_created") {
      api.get("/users/me/notifications").then((res) => {
        setNotifications(res.data.notifications || []);
        setUnreadCount(res.data.unread_count ?? 0);
      }).catch(() => {});
    }
  }, [lastEvent]);

  const pool = {};
  for (const s of liveSessions) pool[s.game_name] = (pool[s.game_name] || 0) + 1;
  const poolEntries = Object.entries(pool).sort((a, b) => b[1] - a[1]);

  const totalMatches = matches.length;
  const crossServerMatches = matches.filter((m) => m.cross_server).length;
  const uniqueGamesLive = poolEntries.length;
  const playersInQueue = liveSessions.length;
  const recentMatches = matches.slice(0, 5);
  const recentNotifications = notifications.slice(0, 5);

  const trend = buildMatchTrend(matches);
  const todayCount = trend[trend.length - 1];
  const weekBefore = trend.slice(0, 7).reduce((a, b) => a + b, 0);
  const weekAfter = trend.slice(5).reduce((a, b) => a + b, 0);
  const trendUp = weekAfter >= weekBefore;

  const avgWait = (() => {
    if (liveSessions.length === 0) return "—";
    const totalSeconds = liveSessions.reduce(
      (sum, s) => sum + Math.max(0, Math.floor((Date.now() - new Date(s.started_at).getTime()) / 1000)),
      0
    );
    const avg = Math.round(totalSeconds / liveSessions.length);
    return avg < 60 ? `${avg}s` : `${Math.floor(avg / 60)}m ${avg % 60}s`;
  })();

  if (error) {
    return (
      <ErrorState
        message={error}
        onRetry={loadAll}
      />
    );
  }

  return (
      <PageLoader isLoading={loading}>
        <div className="space-y-6 animate-fade-in">
          {/* Hero strip */}
          <section className="relative overflow-hidden rounded-2xl border border-void-border bg-gradient-to-r from-brand-500/10 via-void-card to-void-card p-6">
            <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-neon-500/10 blur-3xl" />
            <div className="pointer-events-none absolute -left-10 -bottom-16 h-40 w-40 rounded-full bg-brand-500/10 blur-3xl" />
            <div className="relative flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand-500/15 ring-1 ring-brand-500/30">
                  <IconBolt className="h-6 w-6 text-brand-400" />
                </div>
                <div>
                  <h1 className="text-xl font-bold tracking-tight text-primary">Welcome back</h1>
                  <p className="mt-0.5 text-sm text-muted">Here's what's happening across your servers.</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="rounded-2xl border border-void-border bg-void-card/60 px-5 py-3 text-center backdrop-blur-sm">
                  <p className="text-2xl font-bold text-primary tabular-nums">{stats.matches_today}</p>
                  <p className="mt-0.5 flex items-center gap-1 text-[11px] text-muted">
                    <IconSwords className="h-3 w-3" /> Matches today
                  </p>
                </div>
                <div className="rounded-2xl border border-match/20 bg-match/5 px-5 py-3 text-center backdrop-blur-sm">
                  <div className="flex items-center justify-center gap-1.5 text-2xl font-bold text-match tabular-nums">
                    <span className="relative flex h-2 w-2">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-match opacity-75" />
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-match" />
                    </span>
                    {playersInQueue}
                  </div>
                  <p className="mt-0.5 flex items-center gap-1 text-[11px] text-muted">
                    <IconActivity className="h-3 w-3" /> Live now
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Top-level metrics */}
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard icon={IconSwords} label="Total Matches" value={totalMatches} sub={`${crossServerMatches} cross-server`} i={0} />
            <MetricCard icon={IconActivity} label="Players in Queue" value={playersInQueue} sub={`${uniqueGamesLive} active games`} i={1} />
            <MetricCard icon={IconServer} label="Linked Servers" value={servers.length} sub={`${servers.filter((s) => s.is_admin).length} admin`} i={2} />
            <MetricCard icon={IconBell} label="Unread Notifications" value={unreadCount} sub={unreadCount > 0 ? "New activity waiting" : "You're all caught up"} i={3} />
          </section>

          {/* Trend + recent matches */}
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="relative overflow-hidden rounded-2xl border border-void-border bg-gradient-to-br from-brand-500/10 via-void-card to-void-page p-6">
              <div className="pointer-events-none absolute -right-12 -top-12 h-40 w-40 rounded-full bg-neon-500/10 blur-3xl" />
              <div className="relative flex items-center justify-between">
                <div>
                  <p className="text-sm text-secondary">Matches Today</p>
                  <p className="mt-1 text-4xl font-bold text-primary">{todayCount}</p>
                </div>
                <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ${trendUp ? "bg-match/10 text-match" : "bg-declined/10 text-declined"}`}>
                  {trendUp ? <IconTrendingUp className="h-3 w-3" /> : <IconArrowDownRight className="h-3 w-3" />}
                  {trendUp ? "Up" : "Down"} this week
                </span>
              </div>
              <svg viewBox="0 0 120 36" className="relative mt-4 h-9 w-full" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="spark" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-brand-400)" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="var(--color-brand-400)" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path d={`${sparkPath(trend)} L 120 36 L 0 36 Z`} fill="url(#spark)" />
                <path d={sparkPath(trend)} fill="none" stroke="var(--color-brand-400)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <p className="relative mt-2 text-xs text-muted">Last 12 days</p>
            </div>

            <div className="rounded-2xl border border-void-border bg-void-card/50 p-6 lg:col-span-2">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-base font-semibold text-primary">Recent Matches</h2>
                <span className="text-xs text-muted">Last 5</span>
              </div>
              {recentMatches.length === 0 ? (
                <p className="py-8 text-center text-sm text-muted">No matches yet — matches will show up here once you're paired with someone.</p>
              ) : (
                <div className="space-y-1.5">
                  {recentMatches.map((m) => (
                    <div key={m.id} className="group flex items-center justify-between rounded-xl px-3 py-2.5 transition-colors hover:bg-void-hover">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-500/10 ring-1 ring-brand-500/20">
                          <IconSwords className="h-4 w-4 text-brand-400" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-primary">{m.game_name}</p>
                          <p className="text-xs text-muted">{m.other_display_name || "Unknown player"} · {timeAgo(m.matched_at)}</p>
                        </div>
                      </div>
                      {m.cross_server && (
                        <span className="rounded-full bg-brand-500/10 px-2.5 py-0.5 text-xs font-medium text-brand-400 ring-1 ring-brand-500/30">
                          Cross-server
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
              <Link to="/history" className="mt-3 flex w-full items-center justify-center gap-1 rounded-xl border border-void-border py-2.5 text-sm font-medium text-secondary transition-colors hover:bg-void-hover hover:text-primary">
                View all matches <IconChevronRight className="h-4 w-4" />
              </Link>
            </div>
          </section>

          {/* Queue overview + notifications */}
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-void-border bg-void-card/50 p-6">
              <div className="mb-5 flex items-center justify-between">
                <h2 className="text-base font-semibold text-primary">Queue Overview</h2>
                <IconActivity className="h-4 w-4 text-neon-400" />
              </div>
              {poolEntries.length === 0 ? (
                <p className="py-8 text-center text-sm text-muted">No one is currently in queue.</p>
              ) : (
                <div className="space-y-5">
                  {poolEntries.slice(0, 3).map(([gameName, count]) => {
                    const maxCount = poolEntries[0][1];
                    const pct = Math.round((count / maxCount) * 100);
                    return (
                      <div key={gameName} className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-medium text-secondary">{gameName}</span>
                          <span className="text-xs text-muted tabular-nums">{count} {count === 1 ? "player" : "players"}</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-void-raised">
                          <div className="h-full rounded-full bg-gradient-to-r from-brand-500 to-neon-400 transition-all duration-500" style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
              <Link to="/live" className="mt-5 flex items-center gap-2 rounded-xl bg-brand-500/10 px-4 py-3 ring-1 ring-brand-500/20 transition-colors hover:bg-brand-500/15">
                <IconBolt className="h-4 w-4 shrink-0 text-brand-400" />
                <p className="text-xs text-secondary">Avg. wait time <span className="font-semibold text-primary">{avgWait}</span> across all queues</p>
                <IconChevronRight className="ml-auto h-4 w-4 text-muted" />
              </Link>
            </div>

            <div className="rounded-2xl border border-void-border bg-void-card/50 p-6">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-base font-semibold text-primary">Recent Notifications</h2>
                <span className="flex items-center gap-1.5 text-xs text-muted">
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-match" /> Live feed
                </span>
              </div>
              {recentNotifications.length === 0 ? (
                <p className="py-8 text-center text-sm text-muted">No notifications yet.</p>
              ) : (
                <div className="space-y-1.5">
                  {recentNotifications.map((n) => (
                    <div key={n.id} className="flex items-start gap-2.5 rounded-xl px-3 py-2.5 transition-colors hover:bg-void-hover">
                      {!n.read && <IconCircleFilled className="mt-1.5 h-2 w-2 shrink-0 text-brand-400" />}
                      <div className={n.read ? "ml-[18px]" : ""}>
                        <p className="text-sm font-medium text-primary">{n.title}</p>
                        {n.body && <p className="text-xs text-muted">{n.body}</p>}
                        <p className="mt-0.5 text-[11px] text-muted/70">{timeAgo(n.created_at)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        </div>
      </PageLoader>
  );
}

export default function Dashboard() {
  return (
    <AppShell>
      <DashboardContent />
    </AppShell>
  );
}