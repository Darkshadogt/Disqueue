import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import {
  IconBrandDiscord,
  IconAlertTriangle,
  IconLifebuoy,
  IconBug,
  IconSettings,
  IconBook,
  IconArrowRight,
  IconChevronRight,
} from "@tabler/icons-react";

const COMMON_ISSUES = [
  "Bot not responding",
  "Commands not showing",
  "DM notifications not working",
  "Matchmaking not triggering",
  "Presence tracking issues",
];

const HELP_WITH = [
  "Server setup",
  "Permission configuration",
  "Troubleshooting errors",
  "Feature explanations",
  "Reporting bugs",
];

const RESOURCES = [
  { icon: IconBook, title: "Read the docs", desc: "Browse the full command list and setup guides.", link: "/commands", cta: "View commands" },
  { icon: IconSettings, title: "Server setup", desc: "Step-by-step instructions to add and configure Disqueue.", link: "/features", cta: "See features" },
  { icon: IconBug, title: "Report a bug", desc: "Found something broken? Let us know in the support server.", link: "#support-server", cta: "Join server" },
];

export default function Support() {
  return (
    <div className="min-h-screen bg-void-page text-primary overflow-x-hidden">
      <Navbar />

      {/* Header */}
      <section className="relative isolate overflow-hidden px-6 pt-40 lg:px-8 pb-12">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -top-20 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-brand-600/20 blur-[120px] animate-glow-pulse" />
        </div>
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-brand-400">Support</p>
          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            We're here to <span className="bg-gradient-to-r from-brand-400 to-neon-400 bg-clip-text text-transparent pb-1">help</span>
          </h1>
          <p className="mt-6 text-lg text-secondary">
            Need help with Disqueue? Get answers, report issues, or talk to the team and community.
          </p>
        </div>
      </section>

      {/* Support server CTA */}
      <section id="support-server" className="px-6 py-16 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <div className="relative overflow-hidden rounded-3xl border border-void-border bg-gradient-to-br from-void-card via-brand-900/40 to-void-card p-8 sm:p-12">
            <div className="pointer-events-none absolute inset-0 -z-10">
              <div className="absolute -top-16 left-1/3 h-56 w-56 rounded-full bg-brand-500/25 blur-3xl animate-glow-pulse" />
              <div className="absolute -bottom-10 right-1/4 h-48 w-48 rounded-full bg-neon-500/15 blur-3xl animate-glow-pulse [animation-delay:2s]" />
            </div>

            <div className="flex flex-col items-center text-center sm:flex-row sm:text-left">
              <div className="mb-6 flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-brand-500/15 ring-1 ring-brand-500/30 sm:mb-0 sm:mr-6">
                <IconLifebuoy className="h-8 w-8 text-brand-400" />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-primary">Join the official support server</h2>
                <p className="mt-3 max-w-xl text-secondary">
                  Our team and community members are available to help with bot setup, commands, troubleshooting, and
                  feature questions.
                </p>
              </div>
              {/* TODO: replace with the real invite link before launch */}
              <a
                href="https://discord.gg/YOUR_INVITE_HERE"
                target="_blank"
                rel="noopener noreferrer"
                className="group mt-6 inline-flex shrink-0 items-center gap-2 rounded-xl bg-brand-500 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/30 transition-all hover:bg-brand-400 hover:-translate-y-0.5 sm:mt-0 sm:ml-6"
              >
                <IconBrandDiscord className="h-5 w-5" />
                Join Discord
                <IconArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Resource cards */}
      <section className="px-6 py-16 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            {RESOURCES.map((resource) => (
              <Link
                key={resource.title}
                to={resource.link}
                className="group relative rounded-2xl border border-void-border bg-void-card/50 p-7 backdrop-blur-sm transition-all duration-300 hover:border-brand-400/40 hover:bg-void-raised/60 hover:-translate-y-1"
              >
                <div className="mb-5 inline-flex rounded-xl bg-brand-500/10 p-3 ring-1 ring-brand-500/20 transition-colors group-hover:bg-brand-500/20">
                  <resource.icon className="h-6 w-6 text-brand-400" />
                </div>
                <h3 className="text-lg font-semibold text-primary">{resource.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{resource.desc}</p>
                <span className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-brand-400 transition-colors group-hover:text-brand-200">
                  {resource.cta}
                  <IconChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Common issues / what we help with */}
      <section className="px-6 py-16 lg:px-8 lg:py-24 border-t border-void-border bg-void-card/20">
        <div className="mx-auto max-w-5xl">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="rounded-2xl border border-void-border bg-void-card/50 p-7 backdrop-blur-sm">
              <div className="mb-5 inline-flex rounded-xl bg-pending/10 p-3 ring-1 ring-pending/20">
                <IconAlertTriangle className="h-6 w-6 text-pending" />
              </div>
              <h3 className="text-lg font-semibold text-primary">Common issues</h3>
              <ul className="mt-4 space-y-2.5">
                {COMMON_ISSUES.map((issue) => (
                  <li key={issue} className="flex items-start gap-2.5 text-sm text-muted">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-pending/70" />
                    {issue}
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-2xl border border-void-border bg-void-card/50 p-7 backdrop-blur-sm">
              <div className="mb-5 inline-flex rounded-xl bg-match/10 p-3 ring-1 ring-match/20">
                <IconLifebuoy className="h-6 w-6 text-match" />
              </div>
              <h3 className="text-lg font-semibold text-primary">What we can help with</h3>
              <ul className="mt-4 space-y-2.5">
                {HELP_WITH.map((item) => (
                  <li key={item} className="flex items-start gap-2.5 text-sm text-muted">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-match/70" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
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