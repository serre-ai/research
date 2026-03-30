export const STATUS_COLORS = {
  ok: { base: '#10b981', muted: 'rgba(16, 185, 129, 0.15)', border: 'rgba(16, 185, 129, 0.25)' },
  warn: { base: '#f59e0b', muted: 'rgba(245, 158, 11, 0.15)', border: 'rgba(245, 158, 11, 0.25)' },
  error: { base: '#ef4444', muted: 'rgba(239, 68, 68, 0.15)', border: 'rgba(239, 68, 68, 0.25)' },
  idle: { base: '#737373', muted: 'rgba(115, 115, 115, 0.15)', border: 'rgba(115, 115, 115, 0.25)' },
} as const;

export const DATA_COLORS = ['#60a5fa', '#34d399', '#fbbf24', '#a78bfa', '#f87171', '#22d3ee'] as const;

export type StatusKey = keyof typeof STATUS_COLORS;
