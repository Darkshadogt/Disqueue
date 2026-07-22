import { useEffect, useState } from "react";
import AppShell from "../components/AppShell";
import api from "../api";
import { useRealTime } from "../contexts/RealTimeContext";
import { Dropdown } from "../components/ui";
import {
  IconSwitchVertical,
  IconBell,
  IconUserCheck,
  IconUsers,
  IconDeviceGamepad,
  IconClock,
  IconWorld,
  IconGlobe,
  IconMapPin,
  IconId,
  IconNote,
  IconBan,
  IconLoader2,
  IconAlertTriangle,
} from "@tabler/icons-react";

const GAME_MODES = [
  { value: "any", label: "Any" },
  { value: "casual", label: "Casual" },
  { value: "ranked", label: "Ranked" },
];

const TIMEZONES = ["UTC", "EST", "CST", "MST", "PST", "AKST", "HST", "GMT", "CET", "IST", "JST", "AEST"].map((v) => ({
  value: v,
  label: v,
}));

const LANGUAGES = ["en", "es", "fr", "de", "ja", "ko", "pt", "zh"].map((v) => ({ value: v, label: v.toUpperCase() }));

const REGIONS = ["na", "eu", "asia", "sa", "oce", "me"].map((v) => ({ value: v, label: v.toUpperCase() }));

const DND_OPTIONS = [
  { value: "", label: "Off" },
  ...Array.from({ length: 24 }, (_, h) => ({
    value: String(h),
    label: `${h.toString().padStart(2, "0")}:00`,
  })),
];

const inputBase =
  "w-full rounded-xl border bg-void-raised/40 px-3.5 py-2.5 text-sm text-primary placeholder-muted transition-all duration-200 " +
  "border-void-border hover:border-void-border/80 " +
  "focus:border-brand-400/60 focus:bg-void-raised/60 focus:outline-none focus:ring-2 focus:ring-brand-500/25 " +
  "shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]";

/**
 * Preferences page body, split out from the AppShell wrapper below so it
 * can be unit tested or reused (e.g. in a settings modal) without dragging
 * the sidebar/topbar chrome along with it
 */
export function PreferencesContent() {
  const { preferences: prefs, setPreferences: setPrefs } = useRealTime();
  const [loading, setLoading] = useState(!prefs);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(null); // column name currently being persisted, or null

  useEffect(() => {
    const loadPrefs = async () => {
      try {
        const res = await api.get("/users/me/preferences");
        setPrefs(res.data);
        setError(null);
      } catch {
        setError("Failed to load preferences.");
      } finally {
        setLoading(false);
      }
    };

    loadPrefs();
  }, []);

  const updatePref = async (column, value) => {
    setPrefs((prev) => ({ ...prev, [column]: value }));
    setSaving(column);
    try {
      await api.patch("/users/me/preferences", { [column]: value });
    } catch {
      setError(`Failed to save ${column}.`);
    } finally {
      setSaving(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-20 animate-pulse rounded-2xl border border-void-border bg-void-card/40" />
        ))}
      </div>
    );
  }

  if (error && !prefs) {
    return (
      <div className="flex items-center gap-3 rounded-2xl border border-declined/30 bg-declined/5 p-5">
        <IconAlertTriangle className="h-5 w-5 shrink-0 text-declined" />
        <p className="text-sm text-declined">{error}</p>
      </div>
    );
  }

  if (!prefs) {
    return <p className="text-sm text-muted">No preferences found. Try refreshing the page.</p>;
  }

  return (
    <div className="space-y-6 animate-fade-in mt-10">
      {/* Save errors surface here without blocking the rest of the form */}
      {error && (
        <div className="flex items-center gap-3 rounded-2xl border border-declined/30 bg-declined/5 p-4">
          <IconAlertTriangle className="h-5 w-5 shrink-0 text-declined" />
          <p className="text-sm text-declined">{error}</p>
        </div>
      )}

      {prefs.blocked_user_count > 0 && (
        <div className="flex items-center gap-2.5 rounded-2xl border border-void-border bg-void-card/40 p-4">
          <IconBan className="h-4 w-4 shrink-0 text-muted" />
          <p className="text-sm text-muted">
            {prefs.blocked_user_count} blocked {prefs.blocked_user_count === 1 ? "user" : "users"}
          </p>
        </div>
      )}

      <div className="mx-auto max-w-3xl space-y-8">
        <Section title="Notifications & Behavior">
          <ToggleRow
            icon={IconSwitchVertical}
            label="Matchmaking enabled"
            desc="Turn off to stop receiving match DMs entirely."
            value={prefs.enabled}
            saving={saving === "enabled"}
            onChange={(v) => updatePref("enabled", v)}
          />
          <ToggleRow
            icon={IconBell}
            label="Allow match DMs"
            desc="Required for Disqueue to notify you of matches."
            value={prefs.dm_enabled}
            saving={saving === "dm_enabled"}
            onChange={(v) => updatePref("dm_enabled", v)}
          />
          <ToggleRow
            icon={IconUserCheck}
            label="Require confirmation"
            desc="Review each match before it's finalized."
            value={prefs.match_confirmation_required}
            saving={saving === "match_confirmation_required"}
            onChange={(v) => updatePref("match_confirmation_required", v)}
          />
          <ToggleRow
            icon={IconUsers}
            label="Friend notifications"
            desc="Notify you when friends start playing the same game."
            value={prefs.friend_online_enabled}
            saving={saving === "friend_online_enabled"}
            onChange={(v) => updatePref("friend_online_enabled", v)}
          />
        </Section>

        <Section title="Matching">
          <FieldRow icon={IconDeviceGamepad} label="Game mode">
            <Dropdown value={prefs.game_mode || "any"} onChange={(v) => updatePref("game_mode", v)} options={GAME_MODES} />
          </FieldRow>

          <FieldRow icon={IconClock} label="Cooldown between matches (minutes)">
            <NumberInput
              value={prefs.match_cooldown ?? 2}
              onChange={(v) => updatePref("match_cooldown", parseInt(v, 10) || 0)}
              saving={saving === "match_cooldown"}
            />
          </FieldRow>

          <FieldRow icon={IconClock} label="Daily match limit (blank = unlimited)">
            <NumberInput
              value={prefs.match_limit ?? ""}
              onChange={(v) => updatePref("match_limit", v === "" ? null : parseInt(v, 10))}
              saving={saving === "match_limit"}
            />
          </FieldRow>

          <FieldRow icon={IconClock} label="Do not disturb hours">
            <div className="flex items-center gap-2 sm:gap-3">
              <Dropdown
                value={prefs.dnd_start != null ? String(prefs.dnd_start) : ""}
                onChange={(v) => updatePref("dnd_start", v === "" ? null : parseInt(v, 10))}
                options={DND_OPTIONS}
                className="w-full"
              />
              <span className="shrink-0 text-sm text-muted">to</span>
              <Dropdown
                value={prefs.dnd_end != null ? String(prefs.dnd_end) : ""}
                onChange={(v) => updatePref("dnd_end", v === "" ? null : parseInt(v, 10))}
                options={DND_OPTIONS}
                className="w-full"
              />
            </div>
          </FieldRow>
        </Section>

        <Section title="Profile & Locale">
          <FieldRow icon={IconWorld} label="Timezone">
            <Dropdown value={prefs.timezone || "UTC"} onChange={(v) => updatePref("timezone", v)} options={TIMEZONES} />
          </FieldRow>

          <FieldRow icon={IconId} label="Display name" hint="Shown to matched players">
            <TextInput
              value={prefs.display_name || ""}
              onChange={(v) => updatePref("display_name", v)}
              saving={saving === "display_name"}
              maxLength={32}
              placeholder="Your display name"
            />
          </FieldRow>

          <FieldRow icon={IconNote} label="Bio" hint="Short intro for your match profile">
            <TextArea
              value={prefs.bio || ""}
              onChange={(v) => updatePref("bio", v)}
              saving={saving === "bio"}
              maxLength={190}
              placeholder="Tell others a bit about yourself…"
            />
          </FieldRow>

          <FieldRow icon={IconGlobe} label="Language">
            <Dropdown value={prefs.language || ""} onChange={(v) => updatePref("language", v)} options={LANGUAGES} />
          </FieldRow>

          <FieldRow icon={IconMapPin} label="Region">
            <Dropdown value={prefs.region || ""} onChange={(v) => updatePref("region", v)} options={REGIONS} />
          </FieldRow>
        </Section>
      </div>
    </div>
  );
}

export default function Preferences() {
  return (
    <AppShell>
      <PreferencesContent />
    </AppShell>
  );
}

/* ───── Section + reusable field controls ───── */

function Section({ title, children }) {
  return (
    <section>
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted">{title}</h2>
      <div className="group relative rounded-2xl border border-void-border bg-void-card/50 divide-y divide-void-border transition-colors hover:border-brand-400/30">
        {children}
      </div>
    </section>
  );
}

function ToggleRow({ icon: Icon, label, desc, value, saving, onChange }) {
  return (
    <div className="flex items-center justify-between gap-4 p-5">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-void-raised ring-1 ring-void-border">
          <Icon className="h-4 w-4 text-muted" />
        </div>
        <div>
          <p className="font-medium text-primary">{label}</p>
          <p className="text-sm text-muted">{desc}</p>
        </div>
      </div>

      <button
        type="button"
        role="switch"
        aria-checked={!!value}
        onClick={() => onChange(!value)}
        className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-all duration-200 ${
          value ? "bg-gradient-to-r from-brand-500 to-neon-500 shadow-lg shadow-brand-600/30" : "bg-void-raised ring-1 ring-void-border"
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
            value ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
    </div>
  );
}

function FieldRow({ icon: Icon, label, hint, children }) {
  return (
    <div className="flex flex-col gap-2 p-5 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-void-raised ring-1 ring-void-border">
          <Icon className="h-4 w-4 text-muted" />
        </div>
        <div>
          <p className="font-medium text-primary">{label}</p>
          {hint && <p className="text-sm text-muted">{hint}</p>}
        </div>
      </div>
      <div className="sm:w-72 sm:max-w-[55%]">{children}</div>
    </div>
  );
}

function NumberInput({ value, onChange, saving }) {
  return (
    <div className="relative">
      <input type="number" value={value ?? ""} onChange={(e) => onChange(e.target.value)} className={inputBase} />
      {saving && (
        <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2">
          <IconLoader2 className="h-4 w-4 animate-spin text-brand-400" />
        </div>
      )}
    </div>
  );
}

function TextInput({ value, onChange, saving, maxLength, placeholder }) {
  const len = (value || "").length;
  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        maxLength={maxLength}
        placeholder={placeholder}
        className={inputBase}
      />
      <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center gap-1.5">
        {saving && <IconLoader2 className="h-4 w-4 animate-spin text-brand-400" />}
        {!saving && maxLength && len > 0 && (
          <span className={`text-xs tabular-nums ${len > maxLength * 0.9 ? "text-pending" : "text-muted"}`}>
            {len}/{maxLength}
          </span>
        )}
      </div>
    </div>
  );
}

function TextArea({ value, onChange, saving, maxLength, placeholder }) {
  const len = (value || "").length;
  return (
    <div className="relative">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        maxLength={maxLength}
        placeholder={placeholder}
        rows={3}
        className={`${inputBase} resize-none pr-16`}
      />
      <div className="pointer-events-none absolute right-3 top-3 flex items-center gap-1.5">
        {saving && <IconLoader2 className="h-4 w-4 animate-spin text-brand-400" />}
        {!saving && maxLength && len > 0 && (
          <span className={`text-xs tabular-nums ${len > maxLength * 0.9 ? "text-pending" : "text-muted"}`}>
            {len}/{maxLength}
          </span>
        )}
      </div>
    </div>
  );
}