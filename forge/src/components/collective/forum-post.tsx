'use client';

import { AgentAvatar } from './agent-avatar';
import { AgentNameBadge } from './agent-name-badge';
import { PostTypeBadge } from './post-type-badge';
import { getAgentColor } from '@/lib/agents';
import type { ForumPost as ForumPostType } from '@/lib/collective-types';

interface ForumPostProps {
  post: ForumPostType;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function ForumPost({ post }: ForumPostProps) {
  const color = getAgentColor(post.author);

  return (
    <div
      className="border-b border-border p-4"
      style={{ borderLeft: `3px solid ${color}` }}
    >
      <div className="flex items-center gap-3 mb-3">
        <AgentAvatar agentId={post.author} size="sm" />
        <AgentNameBadge agentId={post.author} />
        {post.post_type !== 'reply' && <PostTypeBadge type={post.post_type} />}
        <span className="ml-auto font-mono text-[10px] text-text-muted">
          {formatDate(post.created_at)}
        </span>
      </div>
      <div className="font-mono text-sm text-text-secondary whitespace-pre-wrap leading-relaxed">
        {post.body}
      </div>
    </div>
  );
}
