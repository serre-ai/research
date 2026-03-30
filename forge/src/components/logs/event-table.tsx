'use client';

import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { AgentNameBadge } from '@/components/collective/agent-name-badge';
import type { DomainEvent } from '@/lib/collective-types';

function relativeTime(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;

  const minutes = Math.floor(diffMs / 60_000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function truncate(str: string, max: number): string {
  return str.length > max ? str.slice(0, max) + '...' : str;
}

interface EventTableProps {
  events: DomainEvent[];
  isLoading?: boolean;
}

export function EventTable({ events, isLoading }: EventTableProps) {
  return (
    <table className="w-full font-mono text-xs">
      <thead>
        <tr>
          <th className="pb-2 text-left text-[10px] uppercase text-text-muted">Type</th>
          <th className="pb-2 text-left text-[10px] uppercase text-text-muted">Agent</th>
          <th className="pb-2 text-left text-[10px] uppercase text-text-muted">Payload</th>
          <th className="pb-2 text-left text-[10px] uppercase text-text-muted">Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {isLoading
          ? Array.from({ length: 5 }).map((_, i) => (
              <tr key={i} className="border-t border-border">
                <td className="py-2 pr-4"><Skeleton className="h-4 w-24" /></td>
                <td className="py-2 pr-4"><Skeleton className="h-4 w-16" /></td>
                <td className="py-2 pr-4"><Skeleton className="h-4 w-48" /></td>
                <td className="py-2"><Skeleton className="h-4 w-14" /></td>
              </tr>
            ))
          : events.map((event) => (
              <tr key={event.id} className="border-t border-border">
                <td className="py-2 pr-4">
                  <Badge>{event.event_type}</Badge>
                </td>
                <td className="py-2 pr-4">
                  {event.agent ? (
                    <AgentNameBadge agentId={event.agent} />
                  ) : (
                    <span className="text-text-muted">&mdash;</span>
                  )}
                </td>
                <td className="py-2 pr-4 text-text-secondary">
                  {truncate(JSON.stringify(event.payload), 80)}
                </td>
                <td className="py-2 text-text-muted">
                  {relativeTime(event.created_at)}
                </td>
              </tr>
            ))}
      </tbody>
    </table>
  );
}
