/**
 * Plain centered spinner. Most pages use PageLoader/Skeleton for loading
 * states now — reach for this only when a lightweight, layout-agnostic
 * spinner is genuinely a better fit (e.g. inside a small modal or button)
 */
export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
    </div>
  );
}