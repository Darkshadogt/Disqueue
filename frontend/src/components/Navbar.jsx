import { Link, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { IconBrandDiscord, IconMenu2, IconX } from "@tabler/icons-react";

const NAV_LINKS = [
  { to: "/", label: "Home" },
  { to: "/features", label: "Features" },
  { to: "/commands", label: "Commands" },
  { to: "/support", label: "Support" },
];

import { LOGIN_URL } from "../config"
const SCROLL_THRESHOLD_PX = 8;

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { pathname } = useLocation();

  const handleLogin = () => {
    window.location.href = LOGIN_URL;
  };

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > SCROLL_THRESHOLD_PX);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Lock body scroll while the mobile menu is open
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
        scrolled
          ? "border-b border-void-border bg-void-page/80 backdrop-blur-xl"
          : "border-b border-transparent bg-transparent"
      }`}
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
        <Link to="/" className="flex items-center">
          <img src="/logo.png" alt="Logo" className="h-15 w-15" />
          <span className="text-lg font-bold tracking-tight text-primary">Disqueue</span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden items-center gap-1 lg:flex">
          {NAV_LINKS.map((link) => {
            const active = pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`relative rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                  active ? "text-primary" : "text-secondary hover:text-primary"
                }`}
              >
                {link.label}
                {active && (
                  <span className="absolute inset-x-3 -bottom-px h-px bg-gradient-to-r from-transparent via-brand-400 to-transparent" />
                )}
              </Link>
            );
          })}
        </div>

        <div className="hidden lg:flex">
          <button
            onClick={handleLogin}
            className="group inline-flex items-center gap-2 rounded-xl border border-void-border bg-void-card/60 px-4 py-2 text-sm font-semibold text-secondary backdrop-blur-sm transition-all hover:border-brand-400/50 hover:text-primary hover:-translate-y-0.5"
          >
            <IconBrandDiscord className="h-4 w-4 text-brand-400 transition-colors group-hover:text-brand-300" />
            Log in
          </button>
        </div>

        <button
          type="button"
          onClick={() => setMobileOpen(true)}
          className="-mr-2 inline-flex items-center justify-center rounded-lg p-2 text-primary lg:hidden"
          aria-label="Open menu"
        >
          <IconMenu2 className="h-6 w-6" />
        </button>
      </nav>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="lg:hidden">
          <div
            className="fixed inset-0 z-50 bg-void-page/70 backdrop-blur-sm animate-fade-in"
            onClick={() => setMobileOpen(false)}
          />

          <div className="fixed inset-y-0 right-0 z-50 flex w-full max-w-sm flex-col border-l border-void-border bg-void-card p-6 shadow-2xl animate-fade-in">
            <div className="flex items-center justify-between">
              <span className="text-lg font-bold tracking-tight text-primary">Menu</span>
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                className="rounded-lg p-2 text-primary hover:bg-void-hover"
                aria-label="Close menu"
              >
                <IconX className="h-6 w-6" />
              </button>
            </div>

            <div className="mt-8 flex flex-col gap-1">
              {NAV_LINKS.map((link) => {
                const active = pathname === link.to;
                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    onClick={() => setMobileOpen(false)}
                    className={`rounded-xl px-4 py-3 text-base font-semibold transition-colors ${
                      active
                        ? "bg-brand-500/10 text-primary ring-1 ring-brand-500/20"
                        : "text-secondary hover:bg-void-hover hover:text-primary"
                    }`}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </div>

            <button
              onClick={handleLogin}
              className="mt-auto inline-flex items-center justify-center gap-2 rounded-xl bg-brand-500 px-4 py-3.5 text-base font-semibold text-white transition-all hover:bg-brand-400"
            >
              <IconBrandDiscord className="h-5 w-5" />
              Log in
            </button>
          </div>
        </div>
      )}
    </header>
  );
}