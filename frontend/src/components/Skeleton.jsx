/**
 * Base pulsing placeholder block. Compose with className to match the
 * shape of whatever it's standing in for (e.g. "h-4 w-32" for a text
 * line, "h-10 w-10 rounded-xl" for an avatar)
 */
export function Skeleton({ className = "" }) {
  return <div className={`animate-pulse rounded-md bg-muted/20 ${className}`} />;
}