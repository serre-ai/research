'use client';

import { AgentAvatar } from './agent-avatar';
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
      return event.event_type.replace(/[._]/g, ' ');
  }
}

export function ActivityItem({ event }: ActivityItemProps) {
  const agent = event.agent ?? (event.payload.agent as string) ?? (event.payload.author as string);

  return (
    <div className="flex items-start gap-3 py-2">
      {agent ? (
        <AgentAvatar agentId={agent} size="sm" />
      ) : (
        <div className="h-6 w-6 border border-border bg-bg-elevated" />
      )}
      <div className="min-w-0 flex-1">
        <p className="font-mono text-xs text-text-secondary truncate">
          {agent && <span className="text-text-bright">{agent}</span>}{' '}
          {eventDescription(event)}
        </p>
        <p className="font-mono text-[10px] text-text-muted">{formatTime(event.created_at)}</p>
      </div>
    </div>
  );
}
