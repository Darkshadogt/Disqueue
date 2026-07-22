import { Link } from "react-router-dom";
import { useState } from "react";
import Navbar from "../components/Navbar";
import {
  IconCategory,
  IconConnection,
  IconBan,
  IconUser,
  IconBell,
  IconSettings,
  IconCopy,
  IconSearch,
  IconCheck,
  IconArrowRight,
} from "@tabler/icons-react";

const COMMANDS = [
  { name: "/enable", desc: "Enable match notifications and open DMs.", cat: "matching" },
  { name: "/disable", desc: "Disable match notifications and stop receiving DMs.", cat: "matching" },
  { name: "/set-game-mode", desc: "Choose Casual, Ranked, or Any matchmaking mode.", cat: "matching" },
  { name: "/match-confirmation", desc: "Toggle whether you confirm matches or auto-accept.", cat: "matching" },
  { name: "/set-match-limit", desc: "Set how many matches you can receive per day.", cat: "matching" },
  { name: "/set-match-cooldown", desc: "Set how long you must wait between matches.", cat: "matching" },
  { name: "/status", desc: "See who is currently playing what game.", cat: "matching" },
  { name: "/match-history", desc: "View your recent matches.", cat: "matching" },
  { name: "/block", desc: "Block a user from being matched with you.", cat: "restrictions" },
  { name: "/unblock", desc: "Unblock a user so they can be matched with you again.", cat: "restrictions" },
  { name: "/blockid", desc: "Block a user by their Discord ID.", cat: "restrictions" },
  { name: "/unblockid", desc: "Unblock a user by their Discord ID.", cat: "restrictions" },
  { name: "/set-region", desc: "Set your region for ranked matchmaking.", cat: "restrictions" },
  { name: "/set-language", desc: "Set your preferred language for matching.", cat: "restrictions" },
  { name: "/set-name", desc: "Set your display name for matchmaking.", cat: "profile" },
  { name: "/set-bio", desc: "Set a short bio visible to matched players.", cat: "profile" },
  { name: "/preferences", desc: "View your current preferences and profile settings.", cat: "profile" },
  { name: "/set-timezone", desc: "Set your timezone for accurate matching.", cat: "time" },
  { name: "/set-dnd", desc: "Set quiet hours when you don't want to be matched.", cat: "time" },
  { name: "/unset-dnd", desc: "Clear your DND quiet hours.", cat: "time" },
  { name: "/friend-notifications", desc: "Get notified when friends start playing the same game.", cat: "time" },
  { name: "/reset", desc: "Reset all your user preferences.", cat: "system" },
];

const CATEGORIES = [
  { key: "all", label: "All", icon: IconCategory },
  { key: "matching", label: "Matching", icon: IconConnection },
  { key: "restrictions", label: "Restrictions", icon: IconBan },
  { key: "profile", label: "Profile", icon: IconUser },
  { key: "time", label: "Time & Notifications", icon: IconBell },
  { key: "system", label: "System", icon: IconSettings },
];

const TOAST_DURATION_MS = 1500;

export default function Commands() {
  const [category, setCategory] = useState("all");
  const [search, setSearch] = useState("");
  const [toast, setToast] = useState(false);

  const filtered = COMMANDS.filter((cmd) => {
    const matchesCategory = category === "all" || cmd.cat === category;
    const query = search.toLowerCase();
    const matchesSearch = cmd.name.toLowerCase().includes(query) || cmd.desc.toLowerCase().includes(query);
    return matchesCategory && matchesSearch;
  });

  const copyCommand = (text) => {
    navigator.clipboard.writeText(text);
    setToast(true);
    setTimeout(() => setToast(false), TOAST_DURATION_MS);
  };

  return (
    <div className="min-h-screen bg-void-page text-primary overflow-x-hidden">
      <Navbar />

      {/* Header */}
      <section className="relative isolate overflow-hidden px-6 pt-40 lg:px-8 pb-12">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -top-20 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-brand-600/20 blur-[120px] animate-glow-pulse" />
        </div>
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-brand-400">Commands</p>
          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            Every command,{" "}
            <span className="bg-gradient-to-r from-brand-400 to-neon-400 bg-clip-text text-transparent pb-1">
              one place
            </span>
          </h1>
          <p className="mt-6 text-lg text-secondary">
            Search and filter every Disqueue command. Click any command to copy it.
          </p>
        </div>
      </section>

      {/* Command browser */}
      <section className="px-6 py-16 lg:px-8 lg:py-20">
        <div className="mx-auto max-w-7xl grid grid-cols-1 lg:grid-cols-4 gap-8">
          <aside className="lg:col-span-1">
            <div className="sticky top-28 rounded-2xl border border-void-border bg-void-card/50 p-5 backdrop-blur-sm">
              <h2 className="text-xs font-semibold uppercase tracking-widest text-muted">Categories</h2>
              <div className="mt-4 flex flex-col gap-1.5">
                {CATEGORIES.map(({ key, label, icon: Icon }) => {
                  const active = category === key;
                  const count = key === "all" ? COMMANDS.length : COMMANDS.filter((c) => c.cat === key).length;
                  return (
                    <button
                      key={key}
                      onClick={() => setCategory(key)}
                      className={`flex items-center justify-between rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                        active
                          ? "bg-brand-500/15 text-primary ring-1 ring-brand-500/30"
                          : "text-secondary hover:bg-void-hover hover:text-primary"
                      }`}
                    >
                      <span className="flex items-center gap-2.5">
                        <Icon className={`h-4 w-4 ${active ? "text-brand-400" : "text-muted"}`} />
                        {label}
                      </span>
                      <span className={`rounded-md px-1.5 py-0.5 text-xs ${active ? "bg-brand-500/20 text-brand-200" : "bg-void-raised text-muted"}`}>
                        {count}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </aside>

          <div className="lg:col-span-3">
            <div className="relative mb-8">
              <IconSearch className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted" />
              <input
                type="text"
                placeholder="Search commands…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full rounded-2xl border border-void-border bg-void-card/50 py-4 pl-12 pr-4 text-sm text-primary placeholder-muted backdrop-blur-sm transition-colors focus:border-brand-400/50 focus:outline-none focus:ring-2 focus:ring-brand-500/30"
              />
            </div>

            <div className="mb-4 text-sm text-muted">
              {filtered.length} {filtered.length === 1 ? "command" : "commands"}
            </div>

            <div className="grid grid-cols-1 gap-4">
              {filtered.map((cmd) => (
                <div
                  key={cmd.name}
                  className="group flex items-start justify-between gap-4 rounded-2xl border border-void-border bg-void-card/50 p-5 backdrop-blur-sm transition-all hover:border-brand-400/40 hover:bg-void-raised/60"
                >
                  <div className="min-w-0">
                    <code className="text-base font-semibold text-brand-400">{cmd.name}</code>
                    <p className="mt-1.5 text-sm leading-relaxed text-muted">{cmd.desc}</p>
                  </div>
                  <button
                    onClick={() => copyCommand(cmd.name)}
                    className="shrink-0 rounded-lg p-2.5 text-muted transition-all hover:bg-brand-500/10 hover:text-brand-400"
                    aria-label={`Copy ${cmd.name}`}
                  >
                    <IconCopy className="h-4 w-4" />
                  </button>
                </div>
              ))}

              {filtered.length === 0 && (
                <div className="rounded-2xl border border-void-border bg-void-card/40 p-12 text-center">
                  <p className="text-secondary">No commands match your search.</p>
                  <button
                    onClick={() => {
                      setSearch("");
                      setCategory("all");
                    }}
                    className="mt-4 text-sm font-semibold text-brand-400 hover:text-brand-200"
                  >
                    Clear filters
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-5xl overflow-hidden rounded-3xl border border-void-border bg-gradient-to-br from-void-card via-brand-900/40 to-void-card p-12 text-center relative lg:p-16">
          <div className="pointer-events-none absolute inset-0 -z-10">
            <div className="absolute -top-16 left-1/2 h-64 w-64 -translate-x-1/2 rounded-full bg-brand-500/20 blur-3xl animate-glow-pulse" />
          </div>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Ready to try them out?</h2>
          <p className="mx-auto mt-5 max-w-xl text-lg text-secondary">
            Add Disqueue to your server and run your first command in under a minute.
          </p>
          <a
            href="http://localhost:8000/auth/login"
            className="mt-8 inline-flex items-center gap-2 rounded-xl bg-brand-500 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/30 transition-all hover:bg-brand-400 hover:-translate-y-0.5"
          >
            Get started
            <IconArrowRight className="h-4 w-4" />
          </a>
        </div>
      </section>

      <Footer />

      {toast && (
        <div className="fixed bottom-8 left-1/2 z-50 -translate-x-1/2 animate-fade-in">
          <div className="flex items-center gap-2 rounded-xl border border-brand-400/30 bg-void-card/95 px-4 py-3 text-sm font-medium text-primary shadow-2xl backdrop-blur-xl">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-match/15 text-match">
              <IconCheck className="h-3 w-3" />
            </span>
            Command copied to clipboard
          </div>
        </div>
      )}
    </div>
  );
}

function Footer() {
  return (
    <footer className="border-t border-void-border bg-void-page/40">
      <div className="mx-auto max-w-7xl px-6 lg:px-8 py-12">
        <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-center">
          <p className="text-sm text-muted">© {new Date().getFullYear()} Disqueue. All rights reserved.</p>
          <div className="flex items-center gap-6 text-sm text-muted">
            <Link to="/terms" className="hover:text-secondary transition-colors">
              Terms &amp; Conditions
            </Link>
            <Link to="/privacy" className="hover:text-secondary transition-colors">
              Privacy Policy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}