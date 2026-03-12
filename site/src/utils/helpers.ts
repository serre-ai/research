export function timeAgo(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return 'just now';
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function statusColor(status: string): string {
  switch (status) {
    case 'running': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    case 'paused': return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    case 'error': return 'bg-red-500/20 text-red-400 border-red-500/30';
    default: return 'bg-neutral-500/20 text-neutral-400 border-neutral-500/30';
  }
}

export function healthColor(status: string): string {
  switch (status) {
    case 'operational': case 'ok': return 'text-emerald-400';
    case 'degraded': return 'text-amber-400';
    case 'offline': case 'error': return 'text-red-400';
    default: return 'text-neutral-400';
  }
}

export function healthDot(status: string): string {
  switch (status) {
    case 'operational': case 'ok': return 'bg-emerald-400';
    case 'degraded': return 'bg-amber-400';
    case 'offline': case 'error': return 'bg-red-400';
    default: return 'bg-neutral-400';
  }
}

export function cellBg(value: number | null): string {
  if (value === null) return 'bg-[var(--color-bg-surface)]';
  if (value >= 90) return 'bg-emerald-500/25';
  if (value >= 70) return 'bg-emerald-500/15';
  if (value >= 40) return 'bg-amber-500/15';
  return 'bg-red-500/15';
}

export function cellText(value: number | null): string {
  if (value === null) return 'text-[var(--color-text-muted)]';
  if (value >= 90) return 'text-emerald-400';
  if (value >= 70) return 'text-emerald-300';
  if (value >= 40) return 'text-amber-400';
  return 'text-red-400';
}

export function liftColor(lift: number): string {
  if (lift >= 40) return 'text-emerald-400';
  if (lift >= 20) return 'text-emerald-300';
  if (lift >= 5) return 'text-amber-400';
  if (lift >= 0) return 'text-[var(--color-text-muted)]';
  return 'text-red-400';
}

export function liftBg(lift: number): string {
  if (lift >= 40) return 'bg-emerald-500/10';
  if (lift >= 20) return 'bg-emerald-500/5';
  return '';
}

export function barWidth(value: number, max: number): number {
  return Math.min(100, (value / max) * 100);
}

export function spendColor(spent: number, limit: number): string {
  const pct = (spent / limit) * 100;
  if (pct >= 90) return 'bg-red-500/60';
  if (pct >= 70) return 'bg-amber-500/50';
  return 'bg-emerald-500/50';
}

export function spendTextColor(spent: number, limit: number): string {
  const pct = (spent / limit) * 100;
  if (pct >= 90) return 'text-red-400';
  if (pct >= 70) return 'text-amber-400';
  return 'text-emerald-400';
}
