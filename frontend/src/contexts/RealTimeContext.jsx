import { createContext, useContext, useState, useCallback } from "react";
import { useRealTimeSync } from "../hooks/RealTimeSync";

const RealTimeContext = createContext(null);

export function RealTimeProvider({ children }) {
  const [preferences, setPreferences] = useState(null);
  const [unreadCount, setUnreadCount] = useState(null);
  const [lastEvent, setLastEvent] = useState(null);

  const handleMessage = useCallback((msg) => {
    setLastEvent(msg);
    if (msg.type === "preferences_updated") setPreferences(msg.data);
    if (msg.type === "notification_created") setUnreadCount(msg.unread_count);
  }, []);

  useRealTimeSync(handleMessage);

  return (
    <RealTimeContext.Provider value={{ preferences, setPreferences, unreadCount, setUnreadCount, lastEvent }}>
      {children}
    </RealTimeContext.Provider>
  );
}

export function useRealTime() {
  const ctx = useContext(RealTimeContext);
  if (!ctx) throw new Error("useRealTime must be used inside RealTimeProvider");
  return ctx;
}