'use client';

import { clsx } from 'clsx';
import type { PostType } from '@/lib/collective-types';

const typeStyles: Record<PostType, { bg: string; text: string; label: string }> = {
  proposal: { bg: 'rgba(234,179,8,0.15)', text: '#EAB308', label: 'Proposal' },
  debate: { bg: 'rgba(239,68,68,0.15)', text: '#ef4444', label: 'Debate' },
  signal: { bg: 'rgba(59,130,246,0.15)', text: '#3b82f6', label: 'Signal' },
  prediction: { bg: 'rgba(168,85,247,0.15)', text: '#a855f7', label: 'Prediction' },
  reply: { bg: 'rgba(115,115,115,0.15)', text: '#737373', label: 'Reply' },
  synthesis: { bg: 'rgba(20,184,166,0.15)', text: '#14B8A6', label: 'Synthesis' },
};

interface PostTypeBadgeProps {
  type: PostType;
  className?: string;
}

export function PostTypeBadge({ type, className }: PostTypeBadgeProps) {
  const style = typeStyles[type] ?? typeStyles.reply;

  return (
    <span
      className={clsx('inline-flex items-center px-2 py-0.5 font-mono text-[10px] font-medium border', className)}
      style={{ backgroundColor: style.bg, color: style.text, borderColor: style.text }}
    >
      {style.label}
    </span>
  );
}
