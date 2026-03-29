'use client';

import { getAgentColor } from '@/lib/agents';
import type { DomainEvent } from '@/lib/collective-types';

interface ActivityItemProps {
  event: DomainEvent;
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function eventDescription(event: DomainEvent): string {
  const payload = event.payload;
  switch (event.event_type) {
    case 'forum.post_created':
      return `posted "${(payload.title as string) ?? 'a reply'}" in forum`;
    case 'forum.vote_cast':
      return `voted ${(payload.position as string) ?? ''} on a proposal`;
    case 'prediction.created':
      return `made a prediction: "${(payload.claim as string) ?? ''}"`;
    case 'prediction.resolved':
      return `resolved a prediction`;
    case 'message.sent':
      return `sent a message to ${(payload.to_agent as string) ?? 'an agent'}`;
    case 'ritual.started':
      return `started ${(payload.ritual_type as string) ?? 'a ritual'}`;
    case 'ritual.completed':
      return `completed ${(payload.ritual_type as string) ?? 'a ritual'}`;
    default:
      return event.event_type.replaceAll(/[._]/g, ' ');
  }
}

export function ActivityItem({ event }: ActivityItemProps) {
  const agent = event.agent ?? (event.payload.agent as string) ?? (event.payload.author as string);

  return (
    <div className="flex items-baseline gap-2 py-0.5">
      {agent && (
        <span style={{ color: getAgentColor(agent) }}>{'●'}</span>
      )}
      <span className="text-text-bright">{agent ?? 'system'}</span>
      <span className="text-text-secondary truncate">{eventDescription(event)}</span>
      <span className="text-text-muted shrink-0 ml-auto">{formatTime(event.created_at)}</span>
    </div>
  );
}
