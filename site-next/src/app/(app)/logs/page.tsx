'use client';

import { useState } from 'react';
import { ScrollText, Inbox } from 'lucide-react';
import { useEvents, useDeadLetters, useRetryDeadLetter } from '@/hooks';
import { PageHeader } from '@/components/ui/page-header';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { EmptyState } from '@/components/ui/empty-state';
import { EventTable } from '@/components/logs/event-table';
import { DeadLetterCard } from '@/components/logs/dead-letter-card';

const EVENT_TYPES = [
  { label: 'All Events', value: '' },
  { label: 'forum.post', value: 'forum.post' },
  { label: 'prediction.created', value: 'prediction.created' },
  { label: 'session.started', value: 'session.started' },
  { label: 'session.completed', value: 'session.completed' },
  { label: 'knowledge.claim', value: 'knowledge.claim' },
  { label: 'governance.vote', value: 'governance.vote' },
];

const LIMIT_OPTIONS = [20, 50, 100];

export default function LogsPage() {
  const [eventType, setEventType] = useState('');
  const [limit, setLimit] = useState(20);

  const { data: events, isLoading: eventsLoading } = useEvents({
    type: eventType || undefined,
    limit,
  });
  const { data: deadLetters, isLoading: deadLettersLoading } = useDeadLetters();
  const retryMutation = useRetryDeadLetter();

  return (
    <div>
      <PageHeader
        title="Event Logs"
        subtitle="System events and dead letter queue"
      >
        <ScrollText className="h-5 w-5 text-text-muted" />
      </PageHeader>

      <Tabs defaultValue="events">
        <TabsList>
          <TabsTrigger value="events">Events</TabsTrigger>
          <TabsTrigger value="dead-letters">Dead Letters</TabsTrigger>
        </TabsList>

        <TabsContent value="events">
          {/* Filters */}
          <div className="mb-4 flex items-center gap-4">
            <select
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              className="border border-border bg-bg-elevated px-3 py-1.5 font-mono text-xs text-text-bright focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {EVENT_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>

            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="border border-border bg-bg-elevated px-3 py-1.5 font-mono text-xs text-text-bright focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {LIMIT_OPTIONS.map((l) => (
                <option key={l} value={l}>
                  {l} rows
                </option>
              ))}
            </select>
          </div>

          {!eventsLoading && events?.length === 0 ? (
            <EmptyState
              icon={ScrollText}
              message="No events found"
              description="Events will appear here as the system processes them."
            />
          ) : (
            <EventTable events={events ?? []} isLoading={eventsLoading} />
          )}
        </TabsContent>

        <TabsContent value="dead-letters">
          {deadLettersLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-28 animate-pulse rounded border border-border bg-bg-elevated" />
              ))}
            </div>
          ) : deadLetters && deadLetters.length > 0 ? (
            <div className="space-y-4">
              {deadLetters.map((dl) => (
                <DeadLetterCard
                  key={dl.id}
                  deadLetter={dl}
                  onRetry={(id) => retryMutation.mutate(id)}
                  isRetrying={retryMutation.isPending}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              icon={Inbox}
              message="No dead letters"
              description="Failed events will appear here for retry."
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
