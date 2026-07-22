import { useEffect, useMemo, useState } from "react";
import AppShell from "../components/AppShell";
import { Skeleton } from "../components/Skeleton";
import { ErrorState } from "../components/ErrorState";
import api from "../api";
import { Dropdown, DateRangePicker } from "../components/ui";
import { useRealTime } from "../contexts/RealTimeContext";
import {
  IconChevronDown,
  IconChevronUp,
  IconSwords,
  IconCrosshair,
  IconClock,
  IconRefresh,
  IconFilter,
  IconCircleFilled,
  IconHistory,
  IconTrendingUp,
} from "@tabler/icons-react";

const MATCH_TYPE_OPTIONS = [
  { value: "all", label: "All matches" },
  { value: "cross", label: "Cross-server only" },
  { value: "same", label: "Same-server only" },
];

const BUCKET_ORDER = ["Today", "Yesterday", "This week", "This month", "Older"];

function startOfDay(d) {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
}

function dateBucket(iso) {
  const today = startOfDay(new Date());
  const d = startOfDay(new Date(iso));
  const diffDays = Math.round((today - d) / 86400000);
  if (diffDays <= 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return "This week";
  if (diffDays < 30) return "This month";
  return "Older";
}

// Row-shaped placeholder shown while matches are loading, so the skeleton
// matches the real timeline entry instead of a generic block
function HistoryRowSkeleton() {
  return (
    <div className="relative pl-6">
      <div className="absolute -left-6 top-5 z-10 h-[18px] w-[18px] rounded-full bg-void-border ring-4 ring-void-page" />
      <div className="flex items-center justify-between gap-4 rounded-2xl border border-void-border bg-void-card/50 p-4">
        <div className="flex items-center gap-3.5">
          <Skeleton className="h-10 w-10 rounded-xl" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-20" />
          </div>
        </div>
        <Skeleton className="h-5 w-5 rounded" />
      </div>
    </div>
  );
}

export function HistoryContent() {
  const [matches, setMatches] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { lastEvent } = useRealTime();

  const [gameFilter, setGameFilter] = useState("");
  const [crossServerFilter, setCrossServerFilter] = useState("all");
  const [dateRange, setDateRange] = useState({ from: "", to: "" });

  const loadMatches = async () => {
    try {
      setLoading(true);
      const res = await api.get("/users/me/matches");
      setMatches(Array.isArray(res.data) ? res.data : []);
      setError(null);
    } catch {
      setError("Failed to load match history.");
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMatches();
  }, []);

  useEffect(() => {
    if (lastEvent?.type === "match_recorded") {
      api.get("/users/me/matches")
        .then((res) => setMatches(Array.isArray(res.data) ? res.data : []))
        .catch(() => {});
    }
  }, [lastEvent]);

  const toggleExpand = (id) => setExpanded((prev) => (prev === id ? null : id));

  const gameOptions = useMemo(
    () => [
      { value: "", label: "All games" },
      ...[...new Set(matches.map((m) => m.game_name))].map((g) => ({ value: g, label: g })),
    ],
    [matches]
  );

  const filteredMatches = matches.filter((m) => {
    const matchDate = new Date(m.matched_at);
    const gameOk = gameFilter ? m.game_name === gameFilter : true;
    const crossServerOk =
      crossServerFilter === "all" ? true : crossServerFilter === "cross" ? m.cross_server === true : m.cross_server === false;
    const dateOk =
      (!dateRange.from || matchDate >= new Date(dateRange.from)) &&
      (!dateRange.to || matchDate <= new Date(dateRange.to));
    return gameOk && crossServerOk && dateOk;
  });

  const grouped = useMemo(() => {
    const map = {};
    for (const m of filteredMatches) {
      const bucket = dateBucket(m.matched_at);
      (map[bucket] ||= []).push(m);
    }
    return BUCKET_ORDER.filter((b) => map[b]?.length).map((b) => ({ bucket: b, items: map[b] }));
  }, [filteredMatches]);

  const hasFilters = gameFilter || crossServerFilter !== "all" || dateRange.from || dateRange.to;

  const clearFilters = () => {
    setGameFilter("");
    setCrossServerFilter("all");
    setDateRange({ from: "", to: "" });
  };

  const stats = useMemo(() => {
    const total = matches.length;
    const cross = matches.filter((m) => m.cross_server).length;
    const avgWait = total ? Math.round(matches.reduce((s, m) => s + (m.wait_time || 0), 0) / total) : 0;
    const uniqueGames = new Set(matches.map((m) => m.game_name)).size;
    return { total, cross, avgWait, uniqueGames };
  }, [matches]);

  if (error) {
    return (
      <ErrorState message={error} onRetry={loadMatches} />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <button
          onClick={loadMatches}
          className="inline-flex items-center gap-2 rounded-xl border border-void-border bg-void-card/60 px-3.5 py-2 text-sm font-medium text-secondary transition-all hover:border-brand-400/40 hover:text-primary"
        >
          <IconRefresh className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {/* Summary strip */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div className="flex items-center gap-3 rounded-2xl border border-void-border bg-void-card/50 px-4 py-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-500/10 ring-1 ring-brand-500/20">
            <IconHistory className="h-4 w-4 text-brand-400" />
          </div>
          <div>
            <p className="text-lg font-bold leading-tight text-primary tabular-nums">{stats.total}</p>
            <p className="text-[11px] text-muted leading-tight">Total matches</p>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-2xl border border-void-border bg-void-card/50 px-4 py-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-neon-500/10 ring-1 ring-neon-500/20">
            <IconCrosshair className="h-4 w-4 text-neon-400" />
          </div>
          <div>
            <p className="text-lg font-bold leading-tight text-primary tabular-nums">{stats.cross}</p>
            <p className="text-[11px] text-muted leading-tight">Cross-server</p>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-2xl border border-void-border bg-void-card/50 px-4 py-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent-500/10 ring-1 ring-accent-500/20">
            <IconClock className="h-4 w-4 text-accent-400" />
          </div>
          <div>
            <p className="text-lg font-bold leading-tight text-primary tabular-nums">{stats.avgWait}s</p>
            <p className="text-[11px] text-muted leading-tight">Avg. wait</p>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-2xl border border-void-border bg-void-card/50 px-4 py-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-match/10 ring-1 ring-match/20">
            <IconTrendingUp className="h-4 w-4 text-match" />
          </div>
          <div>
            <p className="text-lg font-bold leading-tight text-primary tabular-nums">{stats.uniqueGames}</p>
            <p className="text-[11px] text-muted leading-tight">Unique games</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="rounded-2xl border border-void-border bg-gradient-to-b from-void-card/60 to-void-card/30 p-5 backdrop-blur-sm">
        <div className="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted">
          <IconFilter className="h-3.5 w-3.5" />
          Filters
          {hasFilters && (
            <button
              onClick={clearFilters}
              className="ml-auto rounded-md px-2 py-0.5 text-[11px] font-medium normal-case tracking-normal text-brand-400 transition-colors hover:bg-brand-500/10"
            >
              Clear all
            </button>
          )}
        </div>
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-muted">Game</label>
            <Dropdown value={gameFilter} onChange={setGameFilter} options={gameOptions} placeholder="All games" />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-muted">Match type</label>
            <Dropdown value={crossServerFilter} onChange={setCrossServerFilter} options={MATCH_TYPE_OPTIONS} />
          </div>
          <div className="md:col-span-2 lg:col-span-1">
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-muted">Date range</label>
            <DateRangePicker value={dateRange} onChange={setDateRange} />
          </div>
        </div>
      </div>

      {loading && (
        <div className="space-y-8">
          {[0, 1].map((g) => (
            <section key={g}>
              <div className="mb-3 flex items-center gap-3">
                <Skeleton className="h-4 w-20" />
                <div className="h-px flex-1 bg-gradient-to-r from-void-border to-transparent" />
              </div>
              <div className="space-y-3">
                {[0, 1, 2].map((i) => (
                  <HistoryRowSkeleton key={i} />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}

      {!loading && filteredMatches.length === 0 && (
        <div className="relative overflow-hidden rounded-2xl border border-void-border bg-void-card/40 p-16 text-center">
          <div className="pointer-events-none absolute left-1/2 top-0 h-40 w-40 -translate-x-1/2 rounded-full bg-brand-500/5 blur-3xl" />
          <div className="relative mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-void-raised to-void-card ring-1 ring-void-border">
            <IconSwords className="h-7 w-7 text-muted" />
          </div>
          <p className="relative font-semibold text-primary">No matches found</p>
          <p className="relative mx-auto mt-1.5 max-w-sm text-sm text-muted">Try adjusting your filters or check back later.</p>
        </div>
      )}

      {!loading && grouped.length > 0 && (
        <div className="space-y-8">
          {grouped.map(({ bucket, items }) => (
            <section key={bucket}>
              <div className="mb-3 flex items-center gap-3">
                <h2 className="text-sm font-semibold uppercase tracking-widest text-muted">{bucket}</h2>
                <span className="rounded-full bg-void-card/60 px-2 py-0.5 text-xs text-muted ring-1 ring-void-border">
                  {items.length}
                </span>
                <div className="h-px flex-1 bg-gradient-to-r from-void-border to-transparent" />
              </div>

              <div className="relative pl-6">
                <div className="absolute left-[9px] top-2 bottom-2 w-px bg-void-border" />
                <div className="space-y-3">
                  {items.map((match) => {
                    const isOpen = expanded === match.id;
                    return (
                      <div key={match.id} className="relative">
                        <span
                          className={`absolute -left-6 top-5 z-10 flex h-[18px] w-[18px] items-center justify-center rounded-full ring-4 ring-void-page transition-colors ${
                            isOpen ? "bg-brand-400" : "bg-void-border"
                          }`}
                        >
                          {isOpen && <IconCircleFilled className="h-2 w-2 text-void-page" />}
                        </span>

                        <div
                          className={`overflow-hidden rounded-2xl border bg-void-card/50 backdrop-blur-sm transition-all ${
                            isOpen ? "border-brand-400/40" : "border-void-border hover:border-void-border/80"
                          }`}
                        >
                          <button
                            onClick={() => toggleExpand(match.id)}
                            className="flex w-full items-center justify-between gap-4 p-4 text-left"
                          >
                            <div className="flex items-center gap-3.5">
                              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-500/10 ring-1 ring-brand-500/20">
                                <IconSwords className="h-5 w-5 text-brand-400" />
                              </div>
                              <div className="min-w-0">
                                <p className="truncate font-semibold text-primary">{match.game_name}</p>
                                <p className="text-sm text-muted">
                                  {new Date(match.matched_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                                </p>
                              </div>
                            </div>

                            <div className="flex items-center gap-3">
                              {match.cross_server && (
                                <span className="hidden items-center gap-1.5 rounded-full bg-brand-500/10 px-2.5 py-1 text-xs font-medium text-brand-400 ring-1 ring-brand-500/30 sm:inline-flex">
                                  <IconCrosshair className="h-3 w-3" />
                                  Cross-server
                                </span>
                              )}
                              <span className="text-muted transition-transform">
                                {isOpen ? <IconChevronUp className="h-5 w-5" /> : <IconChevronDown className="h-5 w-5" />}
                              </span>
                            </div>
                          </button>

                          {isOpen && (
                            <div className="border-t border-void-border p-4 animate-fade-in">
                              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                <div className="flex items-center gap-3">
                                  <img
                                    src={match.user_avatar}
                                    alt="avatar"
                                    className="h-11 w-11 rounded-full object-cover ring-2 ring-void-border"
                                    referrerPolicy="no-referrer"
                                  />
                                  <div>
                                    <p className="text-xs uppercase tracking-wider text-muted">Matched with</p>
                                    <p className="font-medium text-primary">{match.user_display_name || "Unknown user"}</p>
                                  </div>
                                </div>

                                <div className="flex items-center gap-3">
                                  <div className="flex h-11 w-11 items-center justify-center rounded-full bg-accent-500/10 ring-1 ring-accent-500/20">
                                    <IconClock className="h-5 w-5 text-accent-400" />
                                  </div>
                                  <div>
                                    <p className="text-xs uppercase tracking-wider text-muted">Your queue wait</p>
                                    <p className="font-medium text-primary">
                                      {match.wait_time != null ? `${match.wait_time}s` : "—"}
                                    </p>
                                  </div>
                                </div>
                              </div>

                              {match.cross_server && (
                                <div className="mt-4 sm:hidden">
                                  <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-500/10 px-2.5 py-1 text-xs font-medium text-brand-400 ring-1 ring-brand-500/30">
                                    <IconCrosshair className="h-3 w-3" />
                                    Cross-server match
                                  </span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}

export default function History() {
  return (
    <AppShell>
      <HistoryContent />
    </AppShell>
  );
}