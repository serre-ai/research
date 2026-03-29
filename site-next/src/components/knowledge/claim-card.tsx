'use client';

import { clsx } from 'clsx';
import { TuiBadge, TuiProgress } from '@/components/tui';
import { relativeTime } from '@/lib/format';
import type { Claim } from '@/lib/knowledge-types';

interface ClaimCardProps {
  claim: Claim;
  isSelected?: boolean;
  onClick?: () => void;
}

export function ClaimCard({ claim, isSelected, onClick }: ClaimCardProps) {
  return (
    <div
      onClick={onClick}
      className={clsx(
        'cursor-pointer border-b border-border py-1.5 last:border-0 hover:bg-bg-hover',
        isSelected && 'bg-bg-hover',
      )}
    >
      <div className="flex items-center gap-2">
        <TuiBadge color="accent">{claim.type}</TuiBadge>
        <span className="text-text-muted">{claim.project}</span>
      </div>
      <span className="text-text-secondary line-clamp-2">{claim.statement}</span>
      <div className="flex items-center gap-2 mt-0.5">
        <TuiProgress value={claim.confidence * 100} width={8} showPercent={false} />
        <span className="text-text-muted">{Math.round(claim.confidence * 100)}%</span>
        <span className="text-text-muted ml-auto">{relativeTime(claim.created_at)}</span>
      </div>
    </div>
  );
}
