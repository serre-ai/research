'use client';

import { clsx } from 'clsx';
import type { RitualType } from '@/lib/ritual-types';

const typeStyles: Record<RitualType, { bg: string; text: string; label: string }> = {
  standup: { bg: 'rgba(16,185,129,0.15)', text: '#10b981', label: 'Standup' },
  retrospective: { bg: 'rgba(115,115,115,0.15)', text: '#737373', label: 'Retrospective' },
  pre_mortem: { bg: 'rgba(239,68,68,0.15)', text: '#ef4444', label: 'Pre-mortem' },
  reading_club: { bg: 'rgba(234,179,8,0.15)', text: '#EAB308', label: 'Reading Club' },
  calibration_review: { bg: 'rgba(59,130,246,0.15)', text: '#3b82f6', label: 'Calibration' },
  values_review: { bg: 'rgba(168,85,247,0.15)', text: '#a855f7', label: 'Values Review' },
};

interface RitualTypeBadgeProps {
  type: RitualType;
  className?: string;
}

export function RitualTypeBadge({ type, className }: RitualTypeBadgeProps) {
  const style = typeStyles[type] ?? typeStyles.standup;

  return (
    <span
      className={clsx('inline-flex items-center px-2 py-0.5 font-mono text-[10px] font-medium border', className)}
      style={{ backgroundColor: style.bg, color: style.text, borderColor: style.text }}
    >
      {style.label}
    </span>
  );
}
