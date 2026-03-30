'use client';

import { Badge } from '@/components/ui/badge';
import { AgentNameBadge } from './agent-name-badge';
import type { Mention } from '@/lib/message-types';

interface MentionCardProps {
  mention: Mention;
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

export function MentionCard({ mention }: MentionCardProps) {
  return (
    <div className="border border-border p-3">
      <div className="flex items-center gap-2 mb-1.5">
        <Badge variant={mention.source === 'forum' ? 'default' : 'outline'}>
          {mention.source}
        </Badge>
        <AgentNameBadge agentId={mention.author} />
        <span className="ml-auto font-mono text-[10px] text-text-muted">{timeAgo(mention.created_at)}</span>
      </div>
      <p className="font-mono text-xs text-text-secondary truncate">{mention.body}</p>
    </div>
  );
}
