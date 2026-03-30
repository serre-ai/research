'use client';

import { useState } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Calendar } from 'lucide-react';
import { RitualCard } from '@/components/collective/ritual-card';
import { useUpcomingRituals, useRitualHistory, useStartRitual } from '@/hooks/use-rituals';
import type { RitualType } from '@/lib/ritual-types';

const RITUAL_TYPES: { label: string; value: string }[] = [
  { label: 'All Types', value: '' },
  { label: 'Standup', value: 'standup' },
  { label: 'Retrospective', value: 'retrospective' },
  { label: 'Pre-mortem', value: 'pre_mortem' },
  { label: 'Reading Club', value: 'reading_club' },
  { label: 'Calibration', value: 'calibration_review' },
  { label: 'Values Review', value: 'values_review' },
];

export default function RitualsPage() {
  const [historyTypeFilter, setHistoryTypeFilter] = useState('');

  const { data: upcoming, isLoading: upcomingLoading } = useUpcomingRituals();
  const { data: history, isLoading: historyLoading } = useRitualHistory(
    historyTypeFilter ? (historyTypeFilter as RitualType) : undefined,
  );
  const startRitual = useStartRitual();

  return (
    <Tabs defaultValue="upcoming">
      <TabsList>
        <TabsTrigger value="upcoming">Upcoming</TabsTrigger>
        <TabsTrigger value="history">History</TabsTrigger>
      </TabsList>

      <TabsContent value="upcoming">
        {upcomingLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="border border-border p-4 space-y-2">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-3 w-32" />
              </div>
            ))}
          </div>
        ) : upcoming && upcoming.length > 0 ? (
          <div className="space-y-4">
            {upcoming.map((ritual) => (
              <RitualCard
                key={ritual.id}
                ritual={ritual}
                onStart={(id) => startRitual.mutate(id)}
                isStarting={startRitual.isPending}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Calendar}
            message="No upcoming rituals"
            description="Rituals will appear here when scheduled"
          />
        )}
      </TabsContent>

      <TabsContent value="history">
        <div className="mb-4">
          <select
            value={historyTypeFilter}
            onChange={(e) => setHistoryTypeFilter(e.target.value)}
            className="bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
          >
            {RITUAL_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>

        {historyLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="border border-border p-4 space-y-2">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-3 w-32" />
              </div>
            ))}
          </div>
        ) : history && history.length > 0 ? (
          <div className="space-y-4">
            {history.map((ritual) => (
              <RitualCard key={ritual.id} ritual={ritual} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Calendar}
            message="No ritual history"
            description="Completed rituals will appear here"
          />
        )}
      </TabsContent>
    </Tabs>
  );
}
