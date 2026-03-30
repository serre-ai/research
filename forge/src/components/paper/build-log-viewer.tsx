'use client';

import { TuiSkeleton } from '@/components/tui';
import { TerminalOutput } from '@/components/terminal-output';
import { usePaperLog } from '@/hooks';

export function BuildLogViewer() {
  const { data, isLoading } = usePaperLog();

  if (isLoading) {
    return (
      <div className="space-y-1">
        {Array.from({ length: 8 }).map((_, i) => (
          <TuiSkeleton key={i} width={50} />
        ))}
      </div>
    );
  }

  if (!data) {
    return <span className="text-text-muted">no build log available</span>;
  }

  return (
    <TerminalOutput
      content={data}
      className="h-96 overflow-y-auto"
    />
  );
}
