'use client';

import { TuiSkeleton } from '@/components/tui';
import type { CollectiveHealth } from '@/lib/collective-types';

interface StatsBarProps {
  health: CollectiveHealth | undefined;
  isLoading: boolean;
}

export function StatsBar({ health, isLoading }: StatsBarProps) {
  if (isLoading) {
    return (
      <div className="flex flex-wrap gap-x-6 gap-y-1">
        {Array.from({ length: 4 }).map((_, i) => (
          <TuiSkeleton key={i} width={18} />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-x-6 gap-y-1">
      <span><span className="text-text-bright">{health?.active_threads ?? 0}</span> <span className="text-text-muted">threads</span></span>
      <span><span className="text-text-bright">{health?.pending_proposals ?? 0}</span> <span className="text-text-muted">proposals</span></span>
      <span><span className="text-text-bright">{health?.unresolved_predictions ?? 0}</span> <span className="text-text-muted">predictions</span></span>
      <span><span className="text-text-muted">spend </span><span className="text-text-bright">${(health?.collective_spend_today ?? 0).toFixed(2)}</span></span>
    </div>
  );
}
