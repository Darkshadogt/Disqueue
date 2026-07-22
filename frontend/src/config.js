export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

// Discord OAuth login, served by the backend
export const LOGIN_URL = `${API_BASE_URL}/auth/login`;

// Where an unauthenticated or logged-out user gets sent
export const HOME_PATH = "/";
export const DASHBOARD_PATH = "/dashboard";

// localStorage keys, kept here so a rename doesn't require hunting
// through every file that reads/writes one
export const STORAGE_KEYS = {
  token: "token",
  sidebarCollapsed: "disqueue:sidebarCollapsed",
};

// Shared timing constants used by more than one component/hook
export const TIMING = {
  wsInitialRetryMs: 1000,
  wsMaxRetryMs: 15000,
  notifPollMs: 60000,
  toastAutoDismissMs: 6000,
};