import { Skeleton } from "./Skeleton";

/**
 * Wraps a page's content and swaps it for a generic skeleton while
 * `isLoading` is true. For lists where the loading state should mirror
 * the shape of real rows (e.g. match history, server cards), render
 * row-specific Skeleton placeholders directly in the page instead of
 * using this — this is meant for whole-page or whole-section loading
 */
export function PageLoader({ children, isLoading }) {
  if (isLoading) {
    return (
      <div className="space-y-4 p-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-6 w-full" />
      </div>
    );
  }
  return children;
}