import { useEffect, useRef, useState } from "react";
import { IconChevronDown, IconCheck, IconCalendar, IconArrowRight, IconChevronLeft, IconChevronRight } from "@tabler/icons-react";

const inputBase =
  "w-full rounded-xl border bg-void-raised/40 px-3.5 py-2.5 text-sm text-primary placeholder-muted transition-all duration-200 " +
  "border-void-border hover:border-void-border/80 " +
  "focus:border-brand-400/60 focus:bg-void-raised/60 focus:outline-none focus:ring-2 focus:ring-brand-500/25 " +
  "shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]";

export function Input({ value, onChange, type = "text", placeholder, className = "" }) {
  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className={`${inputBase} ${className}`}
    />
  );
}

export function Select({ value, onChange, children, className = "" }) {
  return (
    <select value={value} onChange={onChange} className={`${inputBase} ${className}`}>
      {children}
    </select>
  );
}

const STATUS_TONES = {
  neutral: "bg-void-raised text-secondary ring-void-border",
  brand: "bg-brand-500/10 text-brand-400 ring-brand-500/30",
  success: "bg-match/10 text-match ring-match/20",
  warning: "bg-pending/10 text-pending ring-pending/20",
  error: "bg-declined/10 text-declined ring-declined/20",
};

export function StatusPill({ tone = "neutral", children }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${STATUS_TONES[tone]}`}>
      {children}
    </span>
  );
}

/**
 * Themed dropdown that replaces the native <select> so it matches the
 * rest of the design system. Supports keyboard nav (arrows/enter/escape)
 * options: [{ value, label }]
 */
export function Dropdown({ value, onChange, options, placeholder = "Select…", className = "", menuClassName = "" }) {
  const [open, setOpen] = useState(false);
  const [highlight, setHighlight] = useState(-1);
  const ref = useRef(null);

  useEffect(() => {
    const onClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const selected = options.find((o) => o.value === value);
  const displayLabel = selected ? selected.label : placeholder;

  const openMenu = () => {
    setOpen(true);
    setHighlight(options.findIndex((o) => o.value === value));
  };

  const onKeyDown = (e) => {
    if (!open) {
      if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
        e.preventDefault();
        openMenu();
      }
      return;
    }
    if (e.key === "Escape") {
      setOpen(false);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(h + 1, options.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (highlight >= 0) {
        onChange(options[highlight].value);
        setOpen(false);
      }
    }
  };

  return (
    <div ref={ref} className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => (open ? setOpen(false) : openMenu())}
        onKeyDown={onKeyDown}
        className={`flex w-full items-center justify-between gap-2 rounded-xl border px-3.5 py-2.5 text-sm transition-all duration-200 ${
          open
            ? "border-brand-400/60 bg-void-raised/60 ring-2 ring-brand-500/25"
            : "border-void-border bg-void-raised/40 hover:border-void-border/80 hover:bg-void-raised/55"
        } shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]`}
      >
        <span className={selected ? "text-primary" : "text-muted"}>{displayLabel}</span>
        <IconChevronDown className={`h-4 w-4 shrink-0 text-muted transition-transform duration-200 ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div
          className={`scroll-thin absolute z-50 mt-2 max-h-60 w-full overflow-y-auto rounded-xl border border-void-border bg-void-card p-1.5 shadow-2xl shadow-black/40 animate-scale-in ${menuClassName}`}
        >
          {options.map((opt, i) => {
            const isSelected = opt.value === value;
            const isHighlighted = i === highlight;
            return (
              <button
                key={String(opt.value)}
                type="button"
                onClick={() => {
                  onChange(opt.value);
                  setOpen(false);
                }}
                onMouseEnter={() => setHighlight(i)}
                className={`flex w-full items-center justify-between gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                  isSelected ? "bg-brand-500/15 text-primary" : isHighlighted ? "bg-void-hover text-primary" : "text-secondary hover:bg-void-hover hover:text-primary"
                }`}
              >
                <span className="truncate">{opt.label}</span>
                {isSelected && <IconCheck className="h-4 w-4 shrink-0 text-brand-400" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function toIso(d) {
  const y = d.getFullYear();
  const m = (d.getMonth() + 1).toString().padStart(2, "0");
  const day = d.getDate().toString().padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function formatDate(iso) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

const DAY_LABELS = ["S", "M", "T", "W", "T", "F", "S"];
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

// Builds a 6-week (42 cell) grid for the given month, padded with the
// trailing days of the previous month and leading days of the next
function buildCalendarCells(year, month) {
  const firstWeekday = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const prevMonthDays = new Date(year, month, 0).getDate();

  const cells = [];
  for (let i = firstWeekday - 1; i >= 0; i--) {
    cells.push({ day: prevMonthDays - i, otherMonth: true, date: new Date(year, month - 1, prevMonthDays - i) });
  }
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ day: d, otherMonth: false, date: new Date(year, month, d) });
  }
  const remaining = 42 - cells.length;
  for (let d = 1; d <= remaining; d++) {
    cells.push({ day: d, otherMonth: true, date: new Date(year, month + 1, d) });
  }
  return cells;
}

function Calendar({ value, activeField, onPick }) {
  const [viewMonth, setViewMonth] = useState(() => {
    const ref = value.from ? new Date(value.from) : value.to ? new Date(value.to) : new Date();
    return new Date(ref.getFullYear(), ref.getMonth(), 1);
  });

  const year = viewMonth.getFullYear();
  const month = viewMonth.getMonth();
  const cells = buildCalendarCells(year, month);

  const fromMs = value.from ? new Date(value.from).getTime() : null;
  const toMs = value.to ? new Date(value.to).getTime() : null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const todayMs = today.getTime();

  return (
    <div className="w-72 rounded-2xl border border-void-border bg-void-card p-4 shadow-2xl shadow-black/50 animate-scale-in">
      <div className="mb-1 flex items-center justify-between">
        <button
          type="button"
          onClick={() => setViewMonth(new Date(year, month - 1, 1))}
          className="flex h-7 w-7 items-center justify-center rounded-lg text-muted transition-colors hover:bg-void-hover hover:text-primary"
        >
          <IconChevronLeft className="h-4 w-4" />
        </button>
        <span className="text-sm font-semibold text-primary">
          {MONTHS[month]} {year}
        </span>
        <button
          type="button"
          onClick={() => setViewMonth(new Date(year, month + 1, 1))}
          className="flex h-7 w-7 items-center justify-center rounded-lg text-muted transition-colors hover:bg-void-hover hover:text-primary"
        >
          <IconChevronRight className="h-4 w-4" />
        </button>
      </div>

      <p className="mb-3 text-center text-xs text-muted">
        {activeField === "from" ? "Select start date" : "Select end date"}
      </p>

      <div className="mb-1.5 grid grid-cols-7 gap-1">
        {DAY_LABELS.map((d, i) => (
          <div key={i} className="text-center text-[11px] font-medium text-muted">
            {d}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {cells.map((cell, i) => {
          const cellMs = cell.date.getTime();
          const isToday = cellMs === todayMs;
          const isFrom = fromMs && cellMs === fromMs;
          const isTo = toMs && cellMs === toMs;
          const inRange = fromMs && toMs && cellMs > fromMs && cellMs < toMs;
          const isEndpoint = isFrom || isTo;

          return (
            <button
              key={i}
              type="button"
              onClick={() => onPick(toIso(cell.date))}
              className={`relative flex h-8 items-center justify-center rounded-lg text-sm transition-all
                ${cell.otherMonth ? "text-muted/35" : "text-secondary"}
                ${isEndpoint ? "bg-brand-500 font-semibold text-white" : ""}
                ${inRange ? "bg-brand-500/15 text-primary" : ""}
                ${!isEndpoint && !inRange && !cell.otherMonth ? "hover:bg-void-hover hover:text-primary" : ""}
                ${isToday && !isEndpoint ? "ring-1 ring-brand-500/40" : ""}
              `}
            >
              {cell.day}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/**
 * Date range picker with quick presets and a custom calendar popover
 * value: { from: "", to: "" } (ISO date strings, yyyy-mm-dd)
 */
export function DateRangePicker({ value, onChange }) {
  const [openField, setOpenField] = useState(null); // "from" | "to" | null
  const ref = useRef(null);

  useEffect(() => {
    const onClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpenField(null);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const daysAgo = (n) => {
    const d = new Date(today);
    d.setDate(d.getDate() - n);
    return toIso(d);
  };

  const presets = [
    { label: "All time", from: "", to: "" },
    { label: "Today", from: toIso(today), to: toIso(today) },
    { label: "7 days", from: daysAgo(7), to: toIso(today) },
    { label: "30 days", from: daysAgo(30), to: toIso(today) },
    { label: "90 days", from: daysAgo(90), to: toIso(today) },
  ];
  const activePreset = presets.find((p) => p.from === value.from && p.to === value.to);

  const handlePick = (iso) => {
    if (openField === "from") {
      onChange({ from: iso, to: "" });
      setOpenField("to");
      return;
    }
    // Picking an end date earlier than the start restarts the range
    // from that date instead of producing an inverted range
    const fromMs = value.from ? new Date(value.from).getTime() : null;
    const pickMs = new Date(iso).getTime();
    if (fromMs && pickMs < fromMs) {
      onChange({ from: iso, to: "" });
    } else {
      onChange({ from: value.from || iso, to: iso });
      setOpenField(null);
    }
  };

  const triggerClass = (isActive) =>
    `flex flex-1 items-center gap-2 rounded-xl border px-3.5 py-2.5 text-sm transition-all duration-200 ${
      isActive
        ? "border-brand-400/60 bg-void-raised/60 ring-2 ring-brand-500/25"
        : "border-void-border bg-void-raised/40 hover:border-void-border/80 hover:bg-void-raised/55"
    }`;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-1.5">
        {presets.map((p) => {
          const isActive = activePreset === p;
          return (
            <button
              key={p.label}
              type="button"
              onClick={() => {
                onChange({ from: p.from, to: p.to });
                setOpenField(null);
              }}
              className={`rounded-full px-3 py-1.5 text-xs font-medium transition-all ${
                isActive
                  ? "bg-brand-500/15 text-brand-300 ring-1 ring-brand-500/30"
                  : "bg-void-raised/50 text-secondary ring-1 ring-void-border hover:bg-void-hover hover:text-primary"
              }`}
            >
              {p.label}
            </button>
          );
        })}
      </div>

      <div ref={ref} className="relative">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setOpenField(openField === "from" ? null : "from")}
            className={triggerClass(openField === "from")}
          >
            <IconCalendar className="h-4 w-4 shrink-0 text-muted" />
            <span className={value.from ? "text-primary" : "text-muted"}>{value.from ? formatDate(value.from) : "From"}</span>
          </button>
          <IconArrowRight className="h-4 w-4 shrink-0 text-muted" />
          <button
            type="button"
            onClick={() => setOpenField(openField === "to" ? null : "to")}
            className={triggerClass(openField === "to")}
          >
            <IconCalendar className="h-4 w-4 shrink-0 text-muted" />
            <span className={value.to ? "text-primary" : "text-muted"}>{value.to ? formatDate(value.to) : "To"}</span>
          </button>
        </div>

        {openField && (
          <div className="absolute top-full left-0 z-50 mt-2">
            <Calendar value={value} activeField={openField} onPick={handlePick} />
          </div>
        )}
      </div>
    </div>
  );
}