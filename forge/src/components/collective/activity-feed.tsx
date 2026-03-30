'use client';

import { TuiSkeleton } from '@/components/tui';
import { ActivityItem } from './activity-item';
import type { DomainEvent } from '@/lib/collective-types';

interface ActivityFeedProps {
  events: DomainEvent[] | undefined;
  isLoading: boolean;
}

export function ActivityFeed({ events, isLoading }: ActivityFeedProps) {
  if (isLoading) {
    return (
      <div className="space-y-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <TuiSkeleton key={i} width={30} />
        ))}
      </div>
    );
  }

  if (!events || events.length === 0) {
    return <span className="text-text-muted">no recent activity</span>;
  }

  return (
    <div className="max-h-[480px] overflow-y-auto space-y-0">
      {events.map((event) => (
        <div key={event.id} className="border-b border-border py-1 last:border-0">
          <ActivityItem event={event} />
        </div>
      ))}
    </div>
  );
}
