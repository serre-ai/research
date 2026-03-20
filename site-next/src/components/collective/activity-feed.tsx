'use client';

import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Radio } from 'lucide-react';
import { ActivityItem } from './activity-item';
import type { DomainEvent } from '@/lib/collective-types';

interface ActivityFeedProps {
  events: DomainEvent[] | undefined;
  isLoading: boolean;
}

export function ActivityFeed({ events, isLoading }: ActivityFeedProps) {
  if (isLoading) {
    return (
      <Card className="space-y-3">
        <Label>Recent Activity</Label>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <Skeleton className="h-6 w-6" />
            <Skeleton className="h-3 w-full" />
          </div>
        ))}
      </Card>
    );
  }

  return (
    <Card>
      <Label>Recent Activity</Label>
      {events && events.length > 0 ? (
        <div className="mt-3 max-h-[480px] overflow-y-auto divide-y divide-border">
          {events.map((event) => (
            <ActivityItem key={event.id} event={event} />
          ))}
        </div>
      ) : (
        <EmptyState icon={Radio} message="No recent activity" className="py-8" />
      )}
    </Card>
  );
}
