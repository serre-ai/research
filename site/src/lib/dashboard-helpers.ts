import type { StatusKey } from '@/lib/constants';

export function mapStatusToKey(status: string): StatusKey {
  switch (status) {
    case 'active':
    case 'running':
    case 'completed':
    case 'success':
      return 'ok';
    case 'paused':
    case 'pending':
    case 'in_progress':
      return 'warn';
    case 'error':
    case 'failed':
      return 'error';
    default:
      return 'idle';
  }
}

export function formatCurrency(value: number): string {
  return `$${value.toFixed(0)}`;
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'today';
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
