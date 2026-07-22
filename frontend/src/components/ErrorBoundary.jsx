import { Component } from "react";
import { IconAlertTriangle } from "@tabler/icons-react";

/**
 * Top-level safety net for render/lifecycle errors that would otherwise
 * white-screen the app. Doesn't catch errors in event handlers or async
 * code — those need their own try/catch — only errors thrown during render
 */
export default class ErrorBoundary extends Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("Uncaught error in component tree:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen items-center justify-center bg-void-page p-6">
          <div className="max-w-md rounded-2xl border border-declined/30 bg-declined/5 p-8 text-center">
            <IconAlertTriangle className="mx-auto mb-4 h-8 w-8 text-declined" />
            <p className="font-semibold text-primary">Something went wrong</p>
            <p className="mt-1.5 text-sm text-muted">
              This page hit an unexpected error. Try reloading — if it keeps happening, that's a bug worth reporting.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="mt-5 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-400"
            >
              Reload
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}