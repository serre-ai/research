'use client';

import { useState } from 'react';
import { useEvents, useDeadLetters, useRetryDeadLetter } from '@/hooks';
import { TuiPanel, TuiList, TuiBadge } from '@/components/tui';
import { formatDate } from '@/lib/dashboard-helpers';

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

  const eventList = events ?? [];
  const deadLetterList = deadLetters ?? [];

  return (
    <>
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 mb-3">
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

      {/* Events */}
      <TuiPanel
        id="activity-log"
        title="ACTIVITY LOG"
        order={1}
        itemCount={eventList.length}
        className="mb-3"
      >
        <TuiList
          panelId="activity-log"
          items={eventList}
          keyFn={(e) => e.id}
          emptyMessage={eventsLoading ? 'loading...' : 'no activity'}
          renderItem={(e, _i, active) => (
            <div className="flex items-center justify-between gap-4">
              <span className="flex items-center gap-2">
                <TuiBadge color="accent">{e.event_type}</TuiBadge>
                <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                  {e.agent ?? (e.payload?.project as string) ?? 'system'}
                </span>
              </span>
              <span className="shrink-0 text-text-muted">{formatDate(e.created_at)}</span>
            </div>
          )}
        />
      </TuiPanel>

      {/* Dead Letters */}
      <TuiPanel
        id="dead-letters"
        title="DEAD LETTERS"
        order={2}
        itemCount={deadLetterList.length}
        onActivateItem={(idx) => retryMutation.mutate(deadLetterList[idx].id)}
        keyHints={[{ key: 'Enter', label: 'Retry' }]}
      >
        <TuiList
          panelId="dead-letters"
          items={deadLetterList}
          keyFn={(dl) => dl.id}
          onActivate={(dl) => retryMutation.mutate(dl.id)}
          emptyMessage={deadLettersLoading ? 'loading...' : 'no dead letters'}
          renderItem={(dl, _i, active) => (
            <div>
              <div className="flex items-center justify-between gap-4">
                <span className="flex items-center gap-2">
                  <TuiBadge color="error">{dl.event_type}</TuiBadge>
                  <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                    {dl.error}
                  </span>
                </span>
                <span className="shrink-0 text-text-muted">{formatDate(dl.created_at)}</span>
              </div>
              <span className="text-text-muted">
                attempts: {dl.attempts} | last: {formatDate(dl.last_attempt_at)}
              </span>
            </div>
          )}
        />
      </TuiPanel>
    </>
  );
}
