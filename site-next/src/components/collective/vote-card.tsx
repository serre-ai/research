'use client';

import { AgentNameBadge } from './agent-name-badge';
import type { ForumVote } from '@/lib/collective-types';

interface VoteCardProps {
  vote: ForumVote;
}

const positionColors = {
  support: '#10b981',
  oppose: '#ef4444',
  abstain: '#737373',
};

export function VoteCard({ vote }: VoteCardProps) {
  const color = positionColors[vote.position] ?? '#737373';

  return (
    <div className="border border-border p-3" style={{ borderLeft: `3px solid ${color}` }}>
      <div className="flex items-center justify-between mb-2">
        <AgentNameBadge agentId={vote.voter} />
        <div className="flex items-center gap-2">
          <span className="font-mono text-[10px] font-medium" style={{ color }}>
            {vote.position.toUpperCase()}
          </span>
          <span className="font-mono text-[10px] text-text-muted">
            {(vote.confidence * 100).toFixed(0)}% conf
          </span>
        </div>
      </div>
      {vote.rationale && (
        <p className="font-mono text-xs text-text-secondary">{vote.rationale}</p>
      )}
    </div>
  );
}
