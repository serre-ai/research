'use client';

import type { ForumVote } from '@/lib/collective-types';

interface VoteBarProps {
  votes: ForumVote[];
}

export function VoteBar({ votes }: VoteBarProps) {
  const support = votes.filter((v) => v.position === 'support').length;
  const oppose = votes.filter((v) => v.position === 'oppose').length;
  const abstain = votes.filter((v) => v.position === 'abstain').length;
  const total = votes.length || 1;

  return (
    <div className="space-y-1.5">
      <div className="flex h-3 w-full overflow-hidden border border-border">
        {support > 0 && (
          <div
            className="h-full"
            style={{ width: `${(support / total) * 100}%`, backgroundColor: '#10b981' }}
          />
        )}
        {oppose > 0 && (
          <div
            className="h-full"
            style={{ width: `${(oppose / total) * 100}%`, backgroundColor: '#ef4444' }}
          />
        )}
        {abstain > 0 && (
          <div
            className="h-full"
            style={{ width: `${(abstain / total) * 100}%`, backgroundColor: '#737373' }}
          />
        )}
      </div>
      <div className="flex gap-4 font-mono text-[10px] text-text-muted">
        <span style={{ color: '#10b981' }}>{support} support</span>
        <span style={{ color: '#ef4444' }}>{oppose} oppose</span>
        <span>{abstain} abstain</span>
      </div>
    </div>
  );
}
