'use client';

import { use } from 'react';
import { GitBranch } from 'lucide-react';
import { useDecisions } from '@/hooks';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function DecisionSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="border-b border-border pb-4 last:border-0 last:pb-0"
        >
          <div className="flex gap-6">
            <Skeleton className="h-3 w-20 shrink-0" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-full" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function DecisionsPage({
  params,
}: {
  params: Promise<{ name: string }>;
}) {
  const { name } = use(params);
  const { data: decisions, isLoading, error } = useDecisions(name);

  return (
    <div>
      {isLoading ? (
        <Card>
          <DecisionSkeleton />
        </Card>
      ) : error ? (
        <Card>
          <p className="text-sm text-[--color-status-error]">
            Failed to load decisions: {error.message}
          </p>
        </Card>
      ) : decisions && decisions.length > 0 ? (
        <Card>
          <div className="space-y-0">
            {decisions.map((decision, i) => (
              <div
                key={`${decision.date}-${i}`}
                className="border-b border-border py-4 first:pt-0 last:border-0 last:pb-0"
              >
                <div className="flex gap-6">
                  <div className="shrink-0 pt-0.5">
                    <span className="font-mono text-xs tabular-nums text-text-muted">
                      {formatDate(decision.date)}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-mono text-sm font-semibold text-text-bright">
                      {decision.decision}
                    </p>
                    <p className="mt-1 text-xs leading-relaxed text-text-secondary">
                      {decision.rationale}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      ) : (
        <EmptyState
          icon={GitBranch}
          message="No decisions recorded"
          description="Decisions made during research sessions will appear here"
        />
      )}
    </div>
  );
}
