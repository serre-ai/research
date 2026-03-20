'use client';

import { AlertTriangle } from 'lucide-react';

export default function RootErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-bg px-4 text-center">
      <AlertTriangle className="mb-4 h-12 w-12 text-text-muted" />
      <h2 className="font-mono text-xl font-semibold text-text-bright mb-2">Something went wrong</h2>
      <p className="font-mono text-sm text-text-secondary mb-1">{error.message}</p>
      {error.digest && (
        <p className="font-mono text-[10px] text-text-muted mb-6">Digest: {error.digest}</p>
      )}
      <div className="flex items-center gap-4">
        <button
          onClick={reset}
          className="font-mono text-sm border border-border px-4 py-2 text-text-bright hover:bg-bg-elevated transition-colors"
        >
          Try again
        </button>
        <a
          href="/"
          className="font-mono text-sm text-primary hover:text-primary-hover transition-colors"
        >
          Back to home
        </a>
      </div>
    </div>
  );
}
