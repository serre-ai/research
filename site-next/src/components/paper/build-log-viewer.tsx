'use client';

import { FileText } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { TerminalOutput } from '@/components/terminal-output';
import { usePaperLog } from '@/hooks';

export function BuildLogViewer() {
  const { data, isLoading } = usePaperLog();

  if (isLoading) {
    return <Skeleton className="h-64" />;
  }

  if (!data) {
    return (
      <EmptyState
        icon={FileText}
        message="No build log available"
      />
    );
  }

  return (
    <TerminalOutput
      content={data}
      className="h-96 overflow-y-auto"
    />
  );
}
