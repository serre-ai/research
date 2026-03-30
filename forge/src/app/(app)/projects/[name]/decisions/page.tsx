'use client';

import { use } from 'react';
import { useDecisions } from '@/hooks';
import { TuiBox, TuiSkeleton } from '@/components/tui';

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toISOString().slice(0, 10);
}

export default function DecisionsPage({
  params,
}: {
  params: Promise<{ name: string }>;
}) {
  const { name } = use(params);
  const { data: decisions, isLoading, error } = useDecisions(name);

  if (isLoading) {
    return (
      <TuiBox title="DECISIONS">
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex gap-4">
              <TuiSkeleton width={10} />
              <TuiSkeleton width={40} />
            </div>
          ))}
        </div>
      </TuiBox>
    );
  }

  if (error) {
    return (
      <TuiBox title="DECISIONS" variant="error">
        <span className="text-text-secondary">failed to load: {error.message}</span>
      </TuiBox>
    );
  }

  if (!decisions || decisions.length === 0) {
    return (
      <TuiBox title="DECISIONS">
        <span className="text-text-muted">no decisions recorded</span>
      </TuiBox>
    );
  }

  return (
    <TuiBox title="DECISIONS">
      {decisions.map((decision, i) => (
        <div
          key={`${decision.date}-${i}`}
          className="border-b border-border py-2 first:pt-0 last:border-0 last:pb-0"
        >
          <div className="flex gap-4">
            <span className="shrink-0 tabular-nums text-text-muted">
              {formatDate(decision.date)}
            </span>
            <div className="flex-1 min-w-0">
              <span className="text-text-bright">{decision.decision}</span>
              <p className="mt-0.5 text-text-secondary">{decision.rationale}</p>
            </div>
          </div>
        </div>
      ))}
    </TuiBox>
  );
}
