'use client';

import { TuiProgress } from '@/components/tui';

interface ProviderBreakdownProps {
  providers: Record<string, number>;
}

export function ProviderBreakdown({ providers }: ProviderBreakdownProps) {
  const entries = Object.entries(providers).sort(([, a], [, b]) => b - a);
  const total = entries.reduce((sum, [, amount]) => sum + amount, 0);

  if (!entries.length) {
    return <span className="text-text-muted">no provider data</span>;
  }

  return (
    <div className="space-y-1">
      {entries.map(([provider, amount]) => {
        const pct = total > 0 ? Math.round((amount / total) * 100) : 0;
        return (
          <div key={provider} className="flex items-center gap-2">
            <span className="w-20 shrink-0 text-text-secondary">{provider}</span>
            <TuiProgress value={pct} width={12} showPercent={false} color="accent" />
            <span className="tabular-nums text-text-bright">${amount.toFixed(2)}</span>
            <span className="tabular-nums text-text-muted">{pct}%</span>
          </div>
        );
      })}
    </div>
  );
}
