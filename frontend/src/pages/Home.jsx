import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import {
  IconBrandDiscord,
  IconBolt,
  IconUsersGroup,
  IconWorldCheck,
  IconArrowRight,
  IconPlayerPlay,
  IconMessage2,
  IconBell,
  IconChevronRight,
} from "@tabler/icons-react";

const HERO_STATS = [
  { value: "12k+", label: "Matches made" },
  { value: "3.2s", label: "Avg. wait time" },
  { value: "850+", label: "Active servers" },
];

const SUPPORTED_GAMES = [
  "Valorant",
  "League of Legends",
  "CS2",
  "Apex Legends",
  "Overwatch 2",
  "Rocket League",
  "Fortnite",
  "Minecraft",
];

const FEATURE_HIGHLIGHTS = [
  { icon: IconWorldCheck, title: "Real-time presence", desc: "Detects who's online and ready to play the moment they're available — no manual queueing." },
  { icon: IconUsersGroup, title: "Smart matchmaking", desc: "Intelligent queue logic pairs players by game, mode, and skill automatically." },
  { icon: IconBrandDiscord, title: "Discord-native", desc: "Lives entirely inside Discord. No second app, no browser tab, no friction." },
  { icon: IconBolt, title: "Instant invites", desc: "Match invites are sent the second a group is formed so players jump in immediately." },
  { icon: IconBell, title: "Smart notifications", desc: "Get pinged only when it matters — when a match is ready, not for every queue update." },
  { icon: IconMessage2, title: "Zero setup", desc: "Add the bot, connect your server, and you're ready. No configuration required." },
];

const HOW_IT_WORKS = [
  { step: "01", title: "Add the bot", desc: "Invite Disqueue to your server with one click. No permissions wizardry required." },
  { step: "02", title: "Players opt in", desc: "Members run /enable and pick their game. Disqueue handles the rest silently." },
  { step: "03", title: "Get matched", desc: "Disqueue forms groups from online players and sends invites the moment a lobby is ready." },
];

const MATCH_FLOW_STEPS = [
  "Detects 3 online Valorant players looking for a group",
  "Forms a balanced lobby based on queue mode + region",
  "DMs each player an invite link automatically",
  "Updates presence so others know the lobby is full",
];

const MOCK_QUEUE_PLAYERS = [
  { name: "nova", status: "Invite sent" },
  { name: "rift", status: "Invite sent" },
  { name: "echo", status: "Invite sent" },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-void-page text-primary overflow-x-hidden">
      <Navbar />

      {/* Hero */}
      <section className="relative isolate overflow-hidden px-6 pt-36 lg:px-8 pb-24">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -top-32 left-1/4 h-[32rem] w-[32rem] rounded-full bg-brand-600/25 blur-[120px] animate-glow-pulse" />
          <div className="absolute top-20 right-1/4 h-[28rem] w-[28rem] rounded-full bg-neon-500/15 blur-[120px] animate-glow-pulse [animation-delay:1.5s]" />
          <div className="absolute -bottom-20 left-1/3 h-[26rem] w-[26rem] rounded-full bg-accent-600/20 blur-[120px] animate-glow-pulse [animation-delay:3s]" />
        </div>
        <div className="pointer-events-none absolute inset-0 -z-10 opacity-[0.04] [background-image:linear-gradient(var(--color-void-border)_1px,transparent_1px),linear-gradient(90deg,var(--color-void-border)_1px,transparent_1px)] [background-size:60px_60px]" />

        <div className="mx-auto max-w-4xl text-center pt-16 sm:pt-24 lg:pt-28">
          <div className="inline-flex items-center gap-2 rounded-full border border-void-border bg-void-card/60 px-4 py-1.5 text-xs font-medium text-secondary backdrop-blur-sm animate-fade-in">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-match opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-match" />
            </span>
            Now in open beta — free for early servers
          </div>

          <h1 className="mt-8 text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl animate-fade-in [animation-delay:80ms]">
            Matchmaking for Discord,
            <span className="block bg-gradient-to-r from-brand-400 via-neon-400 to-accent-400 bg-clip-text text-transparent pb-2 leading-[1.1]">
              reimagined
            </span>
          </h1>

          <p className="mx-auto mt-8 max-w-2xl text-lg font-medium text-secondary sm:text-xl animate-fade-in [animation-delay:160ms]">
            Disqueue connects players fast with smart queues and real-time presence built directly into Discord. No
            lobbies, no friction — just matches.
          </p>

          <div className="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row animate-fade-in [animation-delay:240ms]">
            <a
              href="http://localhost:8000/auth/login"
              className="group inline-flex items-center gap-2 rounded-xl bg-brand-500 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/30 transition-all hover:bg-brand-400 hover:shadow-brand-500/50 hover:-translate-y-0.5"
            >
              <IconBrandDiscord className="h-5 w-5" />
              Get started
              <IconArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </a>
            <Link
              to="/features"
              className="group inline-flex items-center gap-2 rounded-xl border border-void-border bg-void-card/60 px-6 py-3.5 text-sm font-semibold text-secondary backdrop-blur-sm transition-all hover:border-brand-400/50 hover:text-primary hover:-translate-y-0.5"
            >
              <IconPlayerPlay className="h-4 w-4 text-brand-400" />
              Learn more
              <IconChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>

          <div className="mx-auto mt-20 grid max-w-3xl grid-cols-3 gap-4 sm:gap-8 animate-fade-in [animation-delay:320ms]">
            {HERO_STATS.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-bold text-primary sm:text-4xl">{stat.value}</div>
                <div className="mt-1 text-xs font-medium uppercase tracking-wider text-muted sm:text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Supported games marquee, rendered twice back-to-back so the
          CSS scroll animation loops seamlessly with no visible seam */}
      <section className="relative border-y border-void-border bg-void-card/40 py-10">
        <p className="mb-6 text-center text-xs font-semibold uppercase tracking-widest text-muted">
          Works with the games your community already plays
        </p>
        <div className="relative flex overflow-hidden [mask-image:linear-gradient(90deg,transparent,black_15%,black_85%,transparent)]">
          <div className="flex shrink-0 animate-marquee items-center gap-16 pr-16">
            {SUPPORTED_GAMES.map((game) => (
              <span key={game} className="text-lg font-semibold text-muted transition-colors hover:text-secondary whitespace-nowrap">
                {game}
              </span>
            ))}
          </div>
          <div className="flex shrink-0 animate-marquee items-center gap-16 pr-16" aria-hidden>
            {SUPPORTED_GAMES.map((game) => (
              <span key={game} className="text-lg font-semibold text-muted whitespace-nowrap">
                {game}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Feature highlights */}
      <section className="px-6 py-24 lg:px-8 lg:py-32">
        <div className="mx-auto max-w-6xl">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-semibold uppercase tracking-widest text-brand-400">Why Disqueue</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
              Everything matchmaking should have been
            </h2>
            <p className="mt-5 text-lg text-secondary">
              Stop juggling pings, lobbies, and "who wants to play?" messages. Disqueue handles it automatically.
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {FEATURE_HIGHLIGHTS.map((feature) => (
              <div
                key={feature.title}
                className="group relative rounded-2xl border border-void-border bg-void-card/50 p-6 backdrop-blur-sm transition-all duration-300 hover:border-brand-400/40 hover:bg-void-raised/60 hover:-translate-y-1"
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

      {/* How it works */}
      <section className="px-6 py-24 lg:px-8 lg:py-32 border-t border-void-border bg-void-card/20">
        <div className="mx-auto max-w-6xl">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-semibold uppercase tracking-widest text-brand-400">How it works</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
              From idle to in-game in three steps
            </h2>
          </div>

          <div className="relative mt-20 grid grid-cols-1 gap-12 md:grid-cols-3">
            <div className="pointer-events-none absolute left-0 right-0 top-8 hidden h-px bg-gradient-to-r from-transparent via-void-border to-transparent md:block" />
            {HOW_IT_WORKS.map((item) => (
              <div key={item.step} className="relative text-center">
                <div className="relative mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border border-void-border bg-void-raised text-xl font-bold text-brand-400 shadow-lg shadow-brand-900/40">
                  {item.step}
                  <div className="absolute inset-0 -z-10 rounded-2xl bg-brand-500/20 blur-md" />
                </div>
                <h3 className="text-xl font-semibold text-primary">{item.title}</h3>
                <p className="mx-auto mt-3 max-w-xs text-sm leading-relaxed text-muted">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Match flow preview */}
      <section className="px-6 py-24 lg:px-8 lg:py-32">
        <div className="mx-auto max-w-6xl">
          <div className="grid items-center gap-16 lg:grid-cols-2">
            <div>
              <p className="text-sm font-semibold uppercase tracking-widest text-brand-400">See it in action</p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
                A match flow that feels instant
              </h2>
              <p className="mt-5 text-lg text-secondary">
                Disqueue watches presence, forms balanced groups, and delivers invites — all before you finish your
                sentence. Here's what a typical match looks like.
              </p>

              <ul className="mt-8 space-y-4">
                {MATCH_FLOW_STEPS.map((line) => (
                  <li key={line} className="flex items-start gap-3">
                    <div className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-500/20 text-brand-400">
                      <IconChevronRight className="h-3.5 w-3.5" />
                    </div>
                    <span className="text-sm leading-relaxed text-secondary">{line}</span>
                  </li>
                ))}
              </ul>

              <Link
                to="/features"
                className="mt-8 inline-flex items-center gap-2 text-sm font-semibold text-brand-400 transition-colors hover:text-brand-200"
              >
                Explore all features
                <IconArrowRight className="h-4 w-4" />
              </Link>
            </div>

            {/* Mocked Discord panel illustrating a completed match */}
            <div className="relative">
              <div className="absolute -inset-4 -z-10 rounded-3xl bg-gradient-to-br from-brand-600/20 via-neon-500/10 to-accent-600/20 blur-2xl" />
              <div className="rounded-2xl border border-void-border bg-void-card/80 p-5 shadow-2xl shadow-brand-900/40 backdrop-blur-sm">
                <div className="mb-4 flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-declined/70" />
                  <span className="h-3 w-3 rounded-full bg-pending/70" />
                  <span className="h-3 w-3 rounded-full bg-match/70" />
                  <span className="ml-2 text-xs font-medium text-muted">#valorant-queue</span>
                </div>

                <div className="space-y-4">
                  <div className="rounded-lg bg-void-raised/60 p-3">
                    <div className="flex items-center gap-2">
                      <div className="h-6 w-6 rounded-full bg-brand-500/30" />
                      <span className="text-sm font-semibold text-primary">Disqueue</span>
                      <span className="text-xs text-muted">bot</span>
                      <span className="ml-auto text-xs text-muted">just now</span>
                    </div>
                    <p className="mt-2 text-sm text-secondary">
                      Found 3 players for <span className="text-brand-400">Valorant · Ranked</span>. Forming lobby…
                    </p>
                  </div>

                  {MOCK_QUEUE_PLAYERS.map((p) => (
                    <div key={p.name} className="flex items-center justify-between rounded-lg bg-void-raised/40 px-3 py-2.5">
                      <div className="flex items-center gap-2">
                        <div className="h-6 w-6 rounded-full bg-accent-500/30" />
                        <span className="text-sm font-medium text-primary">{p.name}</span>
                      </div>
                      <span className="text-xs font-medium text-match">{p.status}</span>
                    </div>
                  ))}

                  <div className="rounded-lg border border-brand-400/30 bg-brand-500/10 p-3">
                    <p className="text-sm font-semibold text-brand-200">Lobby ready — join the voice channel</p>
                    <p className="mt-1 text-xs text-muted">Match formed in 3.2s · Region: NA · Mode: Ranked</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-24 lg:px-8 lg:py-32">
        <div className="mx-auto max-w-5xl overflow-hidden rounded-3xl border border-void-border bg-gradient-to-br from-void-card via-brand-900/40 to-void-card p-12 text-center relative lg:p-16">
          <div className="pointer-events-none absolute inset-0 -z-10">
            <div className="absolute -top-16 left-1/2 h-64 w-64 -translate-x-1/2 rounded-full bg-brand-500/20 blur-3xl animate-glow-pulse" />
          </div>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
            Ready to find your next match?
          </h2>
          <p className="mx-auto mt-5 max-w-xl text-lg text-secondary">
            Add Disqueue to your server and let your community start matching in minutes. Free during open beta.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <a
              href="http://localhost:8000/auth/login"
              className="group inline-flex items-center gap-2 rounded-xl bg-brand-500 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/30 transition-all hover:bg-brand-400 hover:shadow-brand-500/50 hover:-translate-y-0.5"
            >
              <IconBrandDiscord className="h-5 w-5" />
              Add to your server
              <IconArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </a>
            <Link
              to="/support"
              className="inline-flex items-center gap-2 rounded-xl border border-void-border bg-void-card/60 px-6 py-3.5 text-sm font-semibold text-secondary backdrop-blur-sm transition-all hover:border-brand-400/50 hover:text-primary hover:-translate-y-0.5"
            >
              Get support
            </Link>
          </div>
        </div>
      </section>

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
    </div>
  );
}