'use client';

import { clsx } from 'clsx';
import { Badge } from '@/components/ui/badge';
import { AgentNameBadge } from './agent-name-badge';
import type { Message } from '@/lib/message-types';

interface MessageCardProps {
  message: Message;
  isSelected?: boolean;
  onClick?: () => void;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'now';
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h`;
  return `${Math.floor(hours / 24)}d`;
}

export function MessageCard({ message, isSelected, onClick }: MessageCardProps) {
  const isUnread = message.read_at === null;

  return (
    <button
      onClick={onClick}
      className={clsx(
        'w-full text-left border-b border-border p-4 transition-colors',
        isSelected ? 'bg-bg-elevated' : 'hover:bg-bg-hover',
      )}
      style={{ borderLeft: isUnread ? '3px solid var(--color-primary)' : '3px solid transparent' }}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <AgentNameBadge agentId={message.from_agent} />
        <span className="font-mono text-[10px] text-text-muted">→</span>
        <AgentNameBadge agentId={message.to_agent} />
        {message.priority === 'urgent' && (
          <Badge variant="error">urgent</Badge>
        )}
        <span className="ml-auto font-mono text-[10px] text-text-muted">{timeAgo(message.created_at)}</span>
      </div>
      <p className="font-mono text-sm text-text-bright truncate">{message.subject}</p>
      <p className="font-mono text-xs text-text-muted mt-1 truncate">
        {message.body.slice(0, 80)}{message.body.length > 80 ? '…' : ''}
      </p>
    </button>
  );
}
