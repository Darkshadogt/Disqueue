import { NavLink, useNavigate } from "react-router-dom";
import {
  IconLayoutDashboard,
  IconHistory,
  IconActivity,
  IconAdjustments,
  IconServer,
  IconLogout,
  IconX,
  IconChevronsLeft,
  IconChevronsRight,
} from "@tabler/icons-react";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: IconLayoutDashboard },
  { to: "/live", label: "Live", icon: IconActivity },
  { to: "/history", label: "History", icon: IconHistory },
  { to: "/servers", label: "Linked Servers", icon: IconServer },
  { to: "/preferences", label: "Preferences", icon: IconAdjustments },
];

export default function Sidebar({ open, onClose, collapsed, onToggleCollapse }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div className="fixed inset-0 z-40 bg-void-page/70 backdrop-blur-sm lg:hidden" onClick={onClose} />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex h-screen flex-col border-r border-void-border bg-void-card/90 backdrop-blur-xl transition-all duration-300
          ${collapsed ? "w-[76px]" : "w-72"}
          ${open ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}
      >
        {/* Logo + collapse toggle */}
        <div
          className={`flex shrink-0 items-center border-b border-void-border py-4 ${
            collapsed ? "flex-col gap-2 px-3" : "justify-between px-5"
          }`}
        >
          <div className="flex items-center overflow-hidden">
            <img src="/logo.png" alt="Logo" className="h-13 w-13" />
            {!collapsed && <span className="whitespace-nowrap text-lg font-bold tracking-tight text-primary">Disqueue</span>}
          </div>

          {!collapsed ? (
            <div className="flex items-center gap-1">
              <button
                onClick={onToggleCollapse}
                className="hidden rounded-lg p-1.5 text-muted transition-colors hover:bg-void-hover hover:text-primary lg:block"
                aria-label="Collapse sidebar"
                title="Collapse sidebar"
              >
                <IconChevronsLeft className="h-5 w-5" />
              </button>
              <button
                onClick={onClose}
                className="rounded-lg p-1.5 text-muted hover:bg-void-hover hover:text-primary lg:hidden"
                aria-label="Close sidebar"
              >
                <IconX className="h-5 w-5" />
              </button>
            </div>
          ) : (
            <button
              onClick={onToggleCollapse}
              className="hidden rounded-lg p-1.5 text-muted transition-colors hover:bg-void-hover hover:text-primary lg:block"
              aria-label="Expand sidebar"
              title="Expand sidebar"
            >
              <IconChevronsRight className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Nav links */}
        <nav className="flex flex-1 flex-col gap-1 px-3 py-4">
          {!collapsed && (
            <p className="mb-1 px-3 text-[11px] font-semibold uppercase tracking-widest text-muted">Menu</p>
          )}
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              title={collapsed ? label : undefined}
              className={({ isActive }) =>
                `group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150 ${
                  collapsed ? "justify-center" : ""
                } ${
                  isActive
                    ? "bg-brand-500/15 text-primary shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]"
                    : "text-secondary hover:bg-void-hover hover:text-primary"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute left-0 top-1/2 h-6 w-[3px] -translate-y-1/2 rounded-r-full bg-gradient-to-b from-brand-400 to-neon-400" />
                  )}
                  <Icon
                    className={`h-5 w-5 shrink-0 transition-colors ${
                      isActive ? "text-brand-400" : "text-muted group-hover:text-secondary"
                    }`}
                  />
                  {!collapsed && <span className="truncate">{label}</span>}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Logout */}
        <div className="shrink-0 border-t border-void-border p-3">
          <button
            onClick={handleLogout}
            title={collapsed ? "Log out" : undefined}
            className={`flex w-full items-center gap-2 rounded-xl border border-void-border/60 bg-void-raised/40 py-2.5 text-sm font-semibold text-muted transition-all hover:border-declined/40 hover:bg-declined/5 hover:text-declined ${
              collapsed ? "justify-center px-2" : "justify-center px-4"
            }`}
          >
            <IconLogout className="h-4 w-4 shrink-0" />
            {!collapsed && <span>Log out</span>}
          </button>
        </div>
      </aside>
    </>
  );
}