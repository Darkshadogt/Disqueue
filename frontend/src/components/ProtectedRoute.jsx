import { isLoggedIn } from "../utils/jwt";

import { LOGIN_URL } from "../config"

/**
 * Route guard for authenticated pages. Uses the same isLoggedIn() check
 * as AppShell (which also validates token expiry, not just presence) so
 * a stale token can't slip past this guard only to get bounced a moment
 * later once AppShell fetches the user
 */
export default function ProtectedRoute({ children }) {
  if (!isLoggedIn()) {
    window.location.href = LOGIN_URL;
    return null;
  }

  return children;
}