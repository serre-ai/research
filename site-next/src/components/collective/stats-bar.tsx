'use client';

import { MessageSquare, Vote, Target, DollarSign } from 'lucide-react';
import { MetricCard } from '@/components/ui/metric-card';
import { Skeleton } from '@/components/ui/skeleton';
import type { CollectiveHealth } from '@/lib/collective-types';

interface StatsBarProps {
  health: CollectiveHealth | undefined;
  isLoading: boolean;
}

export function StatsBar({ health, isLoading }: StatsBarProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="border border-border bg-bg-elevated p-6 space-y-2">
            <Skeleton className="h-3 w-20" />
            <Skeleton className="h-7 w-12" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <MetricCard label="Active Threads" value={health?.active_threads ?? 0} icon={MessageSquare} />
      <MetricCard label="Pending Proposals" value={health?.pending_proposals ?? 0} icon={Vote} />
      <MetricCard label="Unresolved Predictions" value={health?.unresolved_predictions ?? 0} icon={Target} />
      <MetricCard
        label="Daily Spend"
        value={`$${(health?.collective_spend_today ?? 0).toFixed(2)}`}
        icon={DollarSign}
      />
    </div>
  );
}
