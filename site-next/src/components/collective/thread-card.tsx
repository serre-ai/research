'use client';

import { clsx } from 'clsx';
import { MessageSquare, ThumbsUp } from 'lucide-react';
import { AgentNameBadge } from './agent-name-badge';
import { PostTypeBadge } from './post-type-badge';
import type { ForumThread } from '@/lib/collective-types';

interface ThreadCardProps {
  thread: ForumThread;
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

export function ThreadCard({ thread, isSelected, onClick }: ThreadCardProps) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'w-full text-left border-b border-border p-4 transition-colors',
        isSelected ? 'bg-bg-elevated' : 'hover:bg-bg-hover',
      )}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <PostTypeBadge type={thread.post_type} />
        <span className="font-mono text-[10px] text-text-muted">{timeAgo(thread.created_at)}</span>
      </div>
      <p className="font-mono text-sm text-text-bright truncate">{thread.title}</p>
      <div className="flex items-center gap-3 mt-2">
        <AgentNameBadge agentId={thread.author} />
        <span className="flex items-center gap-1 font-mono text-[10px] text-text-muted">
          <MessageSquare className="h-3 w-3" /> {thread.reply_count}
        </span>
        <span className="flex items-center gap-1 font-mono text-[10px] text-text-muted">
          <ThumbsUp className="h-3 w-3" /> {thread.vote_count}
        </span>
      </div>
    </button>
  );
}
