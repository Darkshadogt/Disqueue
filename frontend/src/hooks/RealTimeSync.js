import { useEffect, useRef } from "react";

import { WS_BASE_URL, TIMING } from "../config"
const INITIAL_RETRY_DELAY_MS = TIMING.wsInitialRetryMs;
const MAX_RETRY_DELAY_MS = TIMING.wsMaxRetryMs;

/**
 * Maintains a single websocket connection for the lifetime of the
 * component and reconnects with exponential backoff on drop. Also
 * tears down and re-opens the connection whenever the auth token
 * changes (login, logout, refresh), since a stale token would just
 * get rejected by the server
 *
 * `onMessage` is called with the parsed payload for every message.
 * It's stored in a ref so the effect doesn't need to re-run — and the
 * socket doesn't need to reconnect — just because the caller passed a
 * new inline callback on re-render
 */
export function useRealTimeSync(onMessage) {
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    let ws;
    let retryDelay = INITIAL_RETRY_DELAY_MS;
    let cancelled = false;

    function connect() {
      const token = localStorage.getItem("token");
      if (!token) return; // No token yet so the token-changed listener below will retry

      ws = new WebSocket(`${WS_BASE_URL}/ws?token=${token}`);

      ws.onopen = () => {
        retryDelay = INITIAL_RETRY_DELAY_MS;
      };

      ws.onmessage = (event) => {
        try {
          onMessageRef.current(JSON.parse(event.data));
        } catch {
          // Malformed payload — ignore rather than crash the socket
        }
      };

      ws.onclose = () => {
        if (cancelled) return;
        setTimeout(connect, retryDelay);
        retryDelay = Math.min(retryDelay * 2, MAX_RETRY_DELAY_MS);
      };

      ws.onerror = () => ws.close();
    }

    function isSocketOpen() {
      return ws && ws.readyState === WebSocket.OPEN;
    }

    const onTokenChanged = () => {
      if (isSocketOpen()) {
        ws.close();
      }

      retryDelay = INITIAL_RETRY_DELAY_MS;
      connect();
    };

    return () => {
      cancelled = true;
      window.removeEventListener("auth:token-changed", onTokenChanged);

      if (isSocketOpen()) {
        ws.close();
      }
    };
  }, []);
}