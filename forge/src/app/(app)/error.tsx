'use client';

import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <AlertTriangle className="mb-4 h-12 w-12 text-text-muted" />
      <h2 className="font-mono text-xl font-semibold text-text-bright mb-2">Something went wrong</h2>
      <p className="font-mono text-sm text-text-secondary mb-1">{error.message}</p>
      {error.digest && (
        <p className="font-mono text-[10px] text-text-muted mb-6">Digest: {error.digest}</p>
      )}
      <Button variant="outline" size="sm" onClick={reset}>
        Try again
      </Button>
    </div>
  );
}
