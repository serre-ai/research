'use client';

import { Check, X, Clock } from 'lucide-react';

interface OutcomeBadgeProps {
  outcome: boolean | null;
}

export function OutcomeBadge({ outcome }: OutcomeBadgeProps) {
  if (outcome === true) {
    return (
      <span className="inline-flex items-center gap-1 font-mono text-[10px] font-medium" style={{ color: '#10b981' }}>
        <Check className="h-3 w-3" /> TRUE
      </span>
    );
  }
  if (outcome === false) {
    return (
      <span className="inline-flex items-center gap-1 font-mono text-[10px] font-medium" style={{ color: '#ef4444' }}>
        <X className="h-3 w-3" /> FALSE
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 font-mono text-[10px] font-medium text-text-muted">
      <Clock className="h-3 w-3" /> PENDING
    </span>
  );
}
