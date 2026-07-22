import { useState, useRef, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useRealTime } from "../contexts/RealTimeContext";
import { Skeleton } from "./Skeleton";
import { TIMING } from "../config"
import {
  IconMenu2,
  IconSearch,
  IconBell,
  IconChevronDown,
  IconSettings,
  IconLifebuoy,
  IconLogout,
  IconCircleFilled,
} from "@tabler/icons-react";
import api from "../api";

const TITLES = {
  "/dashboard": { title: "Dashboard", subtitle: "Your control center at a glance" },
  "/history": { title: "Match History", subtitle: "Every match you've been part of" },
  "/live": { title: "Live Queues", subtitle: "Real-time presence across servers" },
  "/preferences": { title: "Preferences", subtitle: "Fine-tune your matchmaking" },
  "/servers": { title: "Linked Servers", subtitle: "Servers in the matching pool" },
  "/support": { title: "Support", subtitle: "We're here to help" },
};

const NOTIF_FALLBACK_POLL_MS = TIMING.notifPollMs;

export default function Topbar({ user, onMenuClick }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const { unreadCount, setUnreadCount } = useRealTime();
  const profileRef = useRef(null);
  const notifRef = useRef(null);
  const meta = TITLES[pathname] || { title: "Dashboard", subtitle: "Welcome back" };

  // Close either dropdown when clicking outside of it
  useEffect(() => {
    const onClick = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) setProfileMenuOpen(false);
      if (notifRef.current && !notifRef.current.contains(e.target)) setNotifOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  // Realtime events push fresh notifications in elsewhere in the app
  // This poll is just a safety net in case a websocket event is missed
  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get("/users/me/notifications");
        setNotifications(res.data.notifications || []);
        setUnreadCount(res.data.unread_count || 0);
      } catch {
        // Non-critical so the bell just won't update until the next poll
      }
    };
    load();
    const id = setInterval(load, NOTIF_FALLBACK_POLL_MS);
    return () => clearInterval(id);
  }, [setUnreadCount]);

  const markRead = async (id) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
    setUnreadCount((prev) => Math.max(0, (prev ?? 1) - 1));
    try {
      await api.patch(`/users/me/notifications/${id}/read`);
    } catch {
      // Best-effort, worst case the badge is off until the next poll
    }
  };

  const markAllRead = async () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    setUnreadCount(0);
    try {
      await api.post("/users/me/notifications/read-all");
    } catch {
      // Best-effort, same as markRead
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  const userId = user?.user_id;
  const avatarUrl =
    user && userId
      ? user.avatar
        ? `https://cdn.discordapp.com/avatars/${userId}/${user.avatar}.png`
        : `https://cdn.discordapp.com/embed/avatars/${userId % 5}.png`
      : null;

  return (
    <header className="sticky top-0 z-30 shrink-0 border-b border-void-border bg-void-page/85 backdrop-blur-xl">
      <div className="flex h-16 items-center justify-between gap-4 px-4 lg:px-6">
        {/* Mobile hamburger + page title */}
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="rounded-lg p-2 text-muted hover:bg-void-hover hover:text-primary lg:hidden"
            aria-label="Open sidebar"
          >
            <IconMenu2 className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-[15px] font-bold tracking-tight text-primary leading-tight">{meta.title}</h1>
            <p className="hidden text-[11px] text-muted lg:block leading-tight">{meta.subtitle}</p>
          </div>
        </div>

        {/* Search + notifications + profile */}
        <div className="flex items-center gap-2">
          <div className="relative hidden md:block">
            <IconSearch className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
            <input
              type="text"
              placeholder="Search…"
              className="h-9 w-52 rounded-lg border border-void-border bg-void-raised/50 pl-8 pr-3 text-sm text-primary placeholder-muted transition-all focus:border-brand-400/50 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>

          <div className="relative" ref={notifRef}>
            <button
              onClick={() => setNotifOpen((v) => !v)}
              className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-void-border bg-void-raised/50 text-muted transition-all hover:border-brand-400/40 hover:text-primary"
              aria-label="Notifications"
            >
              <IconBell className="h-4 w-4" />
              {unreadCount > 0 && (
                <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-neon-400 ring-2 ring-void-page" />
              )}
            </button>

            {notifOpen && (
              <div className="absolute right-0 top-full mt-2 w-80 overflow-hidden rounded-2xl border border-void-border bg-void-card shadow-2xl shadow-black/60 backdrop-blur-xl animate-scale-in z-50">
                <div className="flex items-center justify-between border-b border-void-border px-4 py-3">
                  <p className="text-sm font-semibold text-primary">Notifications</p>
                  {unreadCount > 0 && (
                    <button onClick={markAllRead} className="text-xs font-medium text-brand-400 hover:text-brand-300">
                      Mark all read
                    </button>
                  )}
                </div>
                <div className="max-h-80 overflow-y-auto scroll-thin">
                  {notifications.length === 0 ? (
                    <p className="p-5 text-center text-sm text-muted">No notifications yet.</p>
                  ) : (
                    notifications.map((n) => (
                      <button
                        key={n.id}
                        onClick={() => !n.read && markRead(n.id)}
                        className="flex w-full items-start gap-2.5 border-b border-void-border/50 px-4 py-3 text-left transition-colors last:border-0 hover:bg-void-hover"
                      >
                        {!n.read && <IconCircleFilled className="mt-1.5 h-2 w-2 shrink-0 text-brand-400" />}
                        <div className={n.read ? "ml-[18px]" : ""}>
                          <p className="text-sm font-medium text-primary">{n.title}</p>
                          {n.body && <p className="mt-0.5 text-xs text-muted">{n.body}</p>}
                          <p className="mt-1 text-[11px] text-muted/70">{new Date(n.created_at).toLocaleString()}</p>
                        </div>
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {user ? (
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => setProfileMenuOpen((v) => !v)}
                className="flex h-9 items-center gap-2 rounded-lg border border-void-border bg-void-raised/50 py-1 pl-1.5 pr-2.5 transition-all hover:border-brand-400/40"
              >
                <img src={avatarUrl} alt="avatar" className="h-6 w-6 rounded-md object-cover" referrerPolicy="no-referrer" />
                <span className="hidden text-sm font-semibold text-primary sm:block">{user.username}</span>
                <IconChevronDown className={`h-3.5 w-3.5 text-muted transition-transform ${profileMenuOpen ? "rotate-180" : ""}`} />
              </button>

              {profileMenuOpen && (
                <div className="absolute right-0 top-full mt-2 w-56 overflow-hidden rounded-2xl border border-void-border bg-void-card shadow-2xl shadow-black/60 backdrop-blur-xl animate-scale-in z-50">
                  <div className="flex items-center gap-3 border-b border-void-border px-4 py-3">
                    <img src={avatarUrl} alt="" className="h-9 w-9 rounded-xl object-cover ring-1 ring-void-border" referrerPolicy="no-referrer" />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-primary">{user.username}</p>
                      {user.display_name && <p className="truncate text-xs text-muted">{user.display_name}</p>}
                    </div>
                  </div>
                  <div className="p-1.5">
                    <button
                      onClick={() => {
                        setProfileMenuOpen(false);
                        navigate("/preferences");
                      }}
                      className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-secondary transition-colors hover:bg-void-hover hover:text-primary"
                    >
                      <IconSettings className="h-4 w-4 text-muted" /> Preferences
                    </button>
                    <button
                      onClick={() => {
                        setProfileMenuOpen(false);
                        navigate("/support");
                      }}
                      className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-secondary transition-colors hover:bg-void-hover hover:text-primary"
                    >
                      <IconLifebuoy className="h-4 w-4 text-muted" /> Support
                    </button>
                    <div className="my-1 h-px bg-void-border" />
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-declined transition-colors hover:bg-declined/10"
                    >
                      <IconLogout className="h-4 w-4" /> Log out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Skeleton className="h-9 w-36 rounded-lg" />
          )}
        </div>
      </div>
    </header>
  );
}