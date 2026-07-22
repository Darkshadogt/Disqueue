import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import {
  IconWorldCheck,
  IconUsersGroup,
  IconBrandDiscord,
  IconUserShare,
  IconChartDots,
  IconBolt,
  IconArrowRight,
  IconCheck,
  IconX,
} from "@tabler/icons-react";

const FEATURES = [
  { icon: IconWorldCheck, title: "Real-time presence", desc: "Detects who's online and ready to play the moment they're available — no manual queueing." },
  { icon: IconUsersGroup, title: "Smart matchmaking", desc: "Intelligent queue logic pairs players by game, mode, and skill automatically." },
  { icon: IconBrandDiscord, title: "Discord-native", desc: "Lives entirely inside Discord. No second app, no browser tab, no friction." },
  { icon: IconUserShare, title: "Instant invites", desc: "Match invites are sent the second a group is formed so players jump in immediately." },
  { icon: IconChartDots, title: "Activity insights", desc: "Track player activity, queue usage, and match history with clean analytics." },
  { icon: IconBolt, title: "Zero setup", desc: "Add the bot, connect your server, and you're ready. No configuration required." },
];

const COMPARE = [
  { label: "Manual pings & @here spam", without: true },
  { label: "Waiting for someone to make a lobby", without: true },
  { label: "Automatic presence detection", without: false },
  { label: "Balanced groups in seconds", without: false },
  { label: "Instant match invites via DM", without: false },
  { label: "Region & mode aware matching", without: false },
];

export default function Features() {
  return (
    <div className="min-h-screen bg-void-page text-primary overflow-x-hidden">
      <Navbar />

      {/* Header */}
      <section className="relative isolate overflow-hidden px-6 pt-40 lg:px-8 pb-16">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -top-20 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-brand-600/20 blur-[120px] animate-glow-pulse" />
        </div>
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-brand-400">Features</p>
          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            Powerful features built for{" "}
            <span className="bg-gradient-to-r from-brand-400 to-neon-400 bg-clip-text text-transparent pb-1">
              Discord communities
            </span>
          </h1>
          <p className="mt-6 text-lg text-secondary">
            Everything you need to match players quickly, fairly, and automatically.
          </p>
        </div>
      </section>

      {/* Feature grid */}
      <section className="px-6 py-16 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-6xl">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="group relative rounded-2xl border border-void-border bg-void-card/50 p-7 backdrop-blur-sm transition-all duration-300 hover:border-brand-400/40 hover:bg-void-raised/60 hover:-translate-y-1"
              >
                <div className="absolute inset-0 -z-10 rounded-2xl bg-gradient-to-br from-brand-600/0 to-neon-500/0 opacity-0 transition-opacity duration-300 group-hover:from-brand-600/10 group-hover:to-neon-500/5 group-hover:opacity-100" />
                <div className="mb-5 inline-flex rounded-xl bg-brand-500/10 p-3 ring-1 ring-brand-500/20 transition-colors group-hover:bg-brand-500/20">
                  <feature.icon className="h-6 w-6 text-brand-400" />
                </div>
                <h3 className="text-lg font-semibold text-primary">{feature.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Before/after comparison */}
      <section className="px-6 py-16 lg:px-8 lg:py-24 border-t border-void-border bg-void-card/20">
        <div className="mx-auto max-w-4xl">
          <div className="text-center">
            <p className="text-sm font-semibold uppercase tracking-widest text-brand-400">The difference</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Why communities switch</h2>
          </div>

          <div className="mt-12 overflow-hidden rounded-2xl border border-void-border bg-void-card/50 backdrop-blur-sm">
            <div className="grid grid-cols-3 border-b border-void-border bg-void-raised/40 px-6 py-4 text-sm font-semibold">
              <div className="text-secondary">Without Disqueue</div>
              <div className="text-secondary">With Disqueue</div>
              <div className="text-right text-muted">What changes</div>
            </div>
            {COMPARE.map((row) => (
              <div key={row.label} className="grid grid-cols-3 items-center border-b border-void-border/60 px-6 py-4 last:border-0">
                <div className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-declined/10 text-declined">
                    <IconX className="h-3 w-3" />
                  </span>
                  <span className="text-sm text-muted line-through">{row.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-match/10 text-match">
                    <IconCheck className="h-3 w-3" />
                  </span>
                  <span className="text-sm text-secondary">{row.label}</span>
                </div>
                <div className="text-right text-xs uppercase tracking-wider text-muted">
                  {row.without ? "Removed" : "Added"}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-5xl overflow-hidden rounded-3xl border border-void-border bg-gradient-to-br from-void-card via-brand-900/40 to-void-card p-12 text-center relative lg:p-16">
          <div className="pointer-events-none absolute inset-0 -z-10">
            <div className="absolute -top-16 left-1/2 h-64 w-64 -translate-x-1/2 rounded-full bg-brand-500/20 blur-3xl animate-glow-pulse" />
          </div>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">See it in your server</h2>
          <p className="mx-auto mt-5 max-w-xl text-lg text-secondary">
            Add Disqueue in under a minute and let your community start matching today.
          </p>
          <Link
            to="/"
            className="mt-8 inline-flex items-center gap-2 rounded-xl bg-brand-500 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/30 transition-all hover:bg-brand-400 hover:-translate-y-0.5"
          >
            Get started
            <IconArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      <Footer />
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