'use client';

import { useState } from 'react';
import { TuiPanel, TuiList, TuiBadge } from '@/components/tui';
import { useBacklog } from '@/hooks/use-backlog';
import type { BacklogTicket, TicketPriority } from '@/lib/backlog-types';

const PRIORITY_COLOR: Record<TicketPriority, 'error' | 'warn' | 'accent' | 'muted'> = {
  critical: 'error',
  high: 'warn',
  medium: 'accent',
  low: 'muted',
};

export default function BacklogPage() {
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);
  const { data: tickets, isLoading } = useBacklog();

  const ticketList = tickets ?? [];

  return (
    <TuiPanel
      id="backlog"
      title="BACKLOG"
      order={1}
      itemCount={ticketList.length}
      onActivateItem={(idx) => setSelectedTicketId(ticketList[idx]?.id ?? null)}
    >
      <TuiList<BacklogTicket>
        panelId="backlog"
        items={ticketList}
        keyFn={(t) => t.id}
        onActivate={(t) => setSelectedTicketId(t.id)}
        emptyMessage={isLoading ? 'loading...' : 'no backlog items'}
        renderItem={(t, _i, active) => (
          <div className="flex items-center justify-between gap-2">
            <span className="flex items-center gap-2 min-w-0">
              <TuiBadge color={PRIORITY_COLOR[t.priority]}>{t.priority}</TuiBadge>
              <span className={active ? 'text-text-bright truncate' : 'text-text-secondary truncate'}>
                {t.title}
                {t.description && (
                  <span className="text-text-muted ml-1">— {t.description}</span>
                )}
              </span>
            </span>
            <TuiBadge color="muted">{t.category}</TuiBadge>
          </div>
        )}
      />
    </TuiPanel>
  );
}
