import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { IconSwords, IconX } from "@tabler/icons-react";
import { useRealTime } from "../contexts/RealTimeContext";
import { TIMING } from "../config"

const AUTO_DISMISS_MS = TIMING.toastAutoDismissMs;

/**
 * Global "match found" toast. Listens for realtime match events and
 * surfaces a dismissible notification regardless of which page the
 * user is currently on. Mounted once in AppShell
 */
export default function Toast() {
  const { lastEvent } = useRealTime();
  const [visible, setVisible] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (lastEvent?.type === "match_recorded") {
      setVisible(true);
      const timer = setTimeout(() => setVisible(false), AUTO_DISMISS_MS);
      return () => clearTimeout(timer);
    }
  }, [lastEvent]);

  if (!visible) return null;

  return (
    <div className="fixed bottom-6 right-6 z-[100] w-80 animate-fade-in rounded-2xl border border-brand-400/30 bg-void-card/95 p-4 shadow-2xl shadow-black/60 backdrop-blur-xl">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-500/15 ring-1 ring-brand-500/30">
          <IconSwords className="h-4 w-4 text-brand-400" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-primary">Match found!</p>
          <p className="mt-0.5 text-xs text-muted">You've been matched — check your history for details.</p>
          <button
            onClick={() => {
              navigate("/history");
              setVisible(false);
            }}
            className="mt-2 text-xs font-medium text-brand-400 hover:text-brand-300"
          >
            View match →
          </button>
        </div>
        <button onClick={() => setVisible(false)} className="shrink-0 text-muted hover:text-primary" aria-label="Dismiss">
          <IconX className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}