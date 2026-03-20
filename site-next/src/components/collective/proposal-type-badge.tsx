'use client';

import { clsx } from 'clsx';
import type { ProposalType } from '@/lib/governance-types';

const typeStyles: Record<ProposalType, { bg: string; text: string; label: string }> = {
  process: { bg: 'rgba(115,115,115,0.15)', text: '#737373', label: 'Process' },
  schedule: { bg: 'rgba(59,130,246,0.15)', text: '#3b82f6', label: 'Schedule' },
  budget: { bg: 'rgba(234,179,8,0.15)', text: '#EAB308', label: 'Budget' },
  personnel: { bg: 'rgba(168,85,247,0.15)', text: '#a855f7', label: 'Personnel' },
  values: { bg: 'rgba(20,184,166,0.15)', text: '#14B8A6', label: 'Values' },
};

interface ProposalTypeBadgeProps {
  type: ProposalType;
  className?: string;
}

export function ProposalTypeBadge({ type, className }: ProposalTypeBadgeProps) {
  const style = typeStyles[type] ?? typeStyles.process;

  return (
    <span
      className={clsx('inline-flex items-center px-2 py-0.5 font-mono text-[10px] font-medium border', className)}
      style={{ backgroundColor: style.bg, color: style.text, borderColor: style.text }}
    >
      {style.label}
    </span>
  );
}
