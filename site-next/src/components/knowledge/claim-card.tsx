'use client';

import { clsx } from 'clsx';
import { Card } from '@/components/ui/card';
import { ProgressBar } from '@/components/ui/progress-bar';
import { ClaimTypeBadge } from './claim-type-badge';
import { relativeTime } from '@/lib/format';
import type { Claim } from '@/lib/knowledge-types';

interface ClaimCardProps {
  claim: Claim;
  isSelected?: boolean;
  onClick?: () => void;
}

export function ClaimCard({ claim, isSelected, onClick }: ClaimCardProps) {
  return (
    <Card
      className={clsx(
        'cursor-pointer transition-colors hover:bg-bg-hover',
        isSelected && 'ring-1 ring-primary border-primary',
      )}
      onClick={onClick}
    >
      <div className="flex items-center gap-2">
        <ClaimTypeBadge type={claim.type} />
        <span className="font-mono text-[10px] text-text-muted">{claim.project}</span>
      </div>
      <p className="mt-2 font-mono text-sm text-text-secondary line-clamp-2">
        {claim.statement}
      </p>
      <div className="mt-3 space-y-1">
        <ProgressBar value={claim.confidence * 100} />
        <div className="flex items-center justify-between">
          <span className="font-mono text-[10px] text-text-muted">{claim.source}</span>
          <span className="font-mono text-[10px] text-text-muted">
            {relativeTime(claim.created_at)}
          </span>
        </div>
      </div>
    </Card>
  );
}
