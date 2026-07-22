import { useEffect, useState } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import Toast from "./Toast";
import { ErrorState } from "./ErrorState";
import { PageLoader } from "./PageLoader";
import api from "../api";
import { RealTimeProvider } from "../contexts/RealTimeContext";
import { isLoggedIn } from "../utils/jwt";
import { STORAGE_KEYS } from "../config"

const SIDEBAR_COLLAPSED_KEY = STORAGE_KEYS.sidebarCollapsed;

function AppShellInner({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(
    () => localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === "true"
  );

  const toggleSidebarCollapsed = () => {
    setSidebarCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(next));
      return next;
    });
  };

  const fetchUser = () => {
    setLoading(true);
    setError(false);

    if (!isLoggedIn()) {
      localStorage.removeItem("token");
      window.location.href = "/";
      return;
    }

    api
      .get("/users/me")
      .then((res) => {
        setUser(res.data);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <PageLoader isLoading={loading}>
      {error ? (
        <ErrorState message="Unable to load your account." onRetry={fetchUser} />
      ) : (
        <div className="flex h-screen overflow-hidden bg-void-page text-primary">
          <Sidebar
            open={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            collapsed={sidebarCollapsed}
            onToggleCollapse={toggleSidebarCollapsed}
          />

          <div
            className={`flex flex-col flex-1 min-w-0 transition-all duration-300 ${
              sidebarCollapsed ? "lg:pl-[76px]" : "lg:pl-72"
            }`}
          >
            <Topbar user={user} onMenuClick={() => setSidebarOpen(true)} />
            <main className="flex-1 overflow-y-auto scroll-thin px-6 py-6 lg:px-8">{children}</main>
          </div>

          <Toast />
        </div>
      )}
    </PageLoader>
  );
}

/**
 * Shared authenticated-app layout: sidebar + topbar + content area
 * Fetches the current user once, gates the page behind auth, and wraps
 * everything in RealTimeProvider so nested pages can subscribe to
 * websocket events without each one opening its own connection
 */
export default function AppShell({ children }) {
  return (
    <RealTimeProvider>
      <AppShellInner>{children}</AppShellInner>
    </RealTimeProvider>
  );
}