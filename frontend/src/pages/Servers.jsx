import { useEffect, useState } from "react";
import AppShell from "../components/AppShell";
import { Skeleton } from "../components/Skeleton";
import { ErrorState } from "../components/ErrorState";
import api from "../api";
import { IconServer, IconShieldCheck, IconUsers } from "@tabler/icons-react";
import { LOGIN_URL } from "../config"

// Row-shaped placeholder for a server card, shown while the list loads
function ServerRowSkeleton() {
  return (
    <div className="rounded-2xl border border-void-border bg-void-card/50 p-5">
      <div className="flex items-center gap-4">
        <Skeleton className="h-12 w-12 rounded-xl" />
        <div className="min-w-0 flex-1 space-y-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-5 w-20 rounded-full" />
        </div>
      </div>
    </div>
  );
}

export function ServersContent() {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sessionExpired, setSessionExpired] = useState(false);

  const loadServers = async () => {
    try {
      setLoading(true);
      const res = await api.get("/users/me/servers");
      setServers(Array.isArray(res.data) ? res.data : []);
      setError(null);
      setSessionExpired(false);
    } catch (err) {
      if (err.response?.status === 401) {
        setSessionExpired(true);
        setError("Your Discord session expired. Please log in again.");
      } else {
        setError("Failed to load linked servers.");
      }
      setServers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadServers();
  }, []);

  const adminCount = servers.filter((s) => s.is_admin).length;

  if (error) {
    return (
      <ErrorState
        message={error}
        onRetry={sessionExpired ? () => (window.location.href = LOGIN_URL) : loadServers}
      />
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {!loading && servers.length > 0 && (
        <div className="flex justify-end gap-3">
          <div className="rounded-2xl border border-void-border bg-void-card/50 px-4 py-2.5 text-center">
            <p className="text-xl font-bold text-primary tabular-nums">{servers.length}</p>
            <p className="text-[11px] text-muted">Total</p>
          </div>
          <div className="rounded-2xl border border-brand-400/20 bg-brand-500/5 px-4 py-2.5 text-center">
            <p className="text-xl font-bold text-brand-400 tabular-nums">{adminCount}</p>
            <p className="text-[11px] text-muted">Admin</p>
          </div>
        </div>
      )}

      {loading && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <ServerRowSkeleton key={i} />
          ))}
        </div>
      )}

      {!loading && servers.length === 0 && (
        <div className="relative overflow-hidden rounded-2xl border border-void-border bg-void-card/40 p-16 text-center">
          <div className="pointer-events-none absolute left-1/2 top-0 h-40 w-40 -translate-x-1/2 rounded-full bg-brand-500/5 blur-3xl" />
          <div className="relative mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-void-raised to-void-card ring-1 ring-void-border">
            <IconServer className="h-7 w-7 text-muted" />
          </div>
          <p className="relative font-semibold text-primary">No linked servers found</p>
        </div>
      )}

      {!loading && servers.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {servers.map((server) => (
            <div
              key={server.id}
              className="group relative overflow-hidden rounded-2xl border border-void-border bg-void-card/50 p-5 backdrop-blur-sm transition-all hover:border-brand-400/40 hover:-translate-y-1 hover:shadow-xl hover:shadow-brand-600/10"
            >
              <div className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full bg-brand-500/10 opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-100" />

              <div className="relative flex items-center gap-4">
                {server.icon ? (
                  <img
                    src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png`}
                    alt=""
                    className="h-12 w-12 shrink-0 rounded-xl object-cover ring-1 ring-void-border"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-void-raised to-void-card ring-1 ring-void-border">
                    <IconServer className="h-5 w-5 text-muted" />
                  </div>
                )}

                <div className="min-w-0 flex-1">
                  <p className="truncate font-semibold text-primary">{server.name}</p>
                  {server.is_admin ? (
                    <span className="mt-1.5 inline-flex items-center gap-1.5 rounded-full bg-brand-500/10 px-2.5 py-1 text-xs font-medium text-brand-400 ring-1 ring-brand-500/30">
                      <IconShieldCheck className="h-3.5 w-3.5" />
                      Admin
                    </span>
                  ) : (
                    <span className="mt-1.5 inline-flex items-center gap-1.5 rounded-full bg-void-raised px-2.5 py-1 text-xs font-medium text-muted ring-1 ring-void-border">
                      <IconUsers className="h-3.5 w-3.5" />
                      Member
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Servers() {
  return (
    <AppShell>
      <ServersContent />
    </AppShell>
  );
}