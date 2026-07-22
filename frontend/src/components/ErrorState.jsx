/**
 * Generic inline error display used for failed data fetches across the app
 * Pass `onRetry` to show a retry button, or omit it for a message-only state
 */
export function ErrorState({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center p-6 text-center">
      <p className="mb-3 text-sm text-muted">{message || "Something went wrong."}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded-md bg-brand-500 px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-brand-400"
        >
          Retry
        </button>
      )}
    </div>
  );
}