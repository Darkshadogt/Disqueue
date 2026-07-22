import { useEffect, useState } from "react";

/**
 * OAuth redirect target. Discord sends the user back here with the
 * access token in the query string; we stash it and hand off to the
 * dashboard. This is a plain redirect page, not a route the user should
 * ever land on directly
 */
export default function Callback() {
  const [error, setError] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("access_token");

    if (!token) {
      setError(true);
      return;
    }

    localStorage.setItem("token", token);
    // Notify other tabs/components (e.g. the API client) that auth state changed
    window.dispatchEvent(new Event("auth:token-changed"));

    // Full reload rather than router navigation so every provider
    // (api client, websocket, etc.) re-initializes with the new token
    window.location.replace("/dashboard");
  }, []);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-void-page text-center text-secondary">
        <div>
          <p>Something went wrong signing you in.</p>
          <a href="http://localhost:8000/auth/login" className="text-brand-400 underline">
            Try again
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-void-page text-secondary">
      Signing you in…
    </div>
  );
}