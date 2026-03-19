'use client';

import { DATA_COLORS } from '@/lib/constants';

interface ProviderBreakdownProps {
  providers: Record<string, number>;
}

export function ProviderBreakdown({ providers }: ProviderBreakdownProps) {
  const entries = Object.entries(providers).sort(([, a], [, b]) => b - a);
  const total = entries.reduce((sum, [, amount]) => sum + amount, 0);

  if (!entries.length) {
    return (
      <p className="text-sm text-text-muted">No provider data available</p>
    );
  }

  return (
    <div className="space-y-3">
      {entries.map(([provider, amount], i) => {
        const pct = total > 0 ? (amount / total) * 100 : 0;
        const color = DATA_COLORS[i % DATA_COLORS.length];

        return (
          <div key={provider}>
            <div className="mb-1.5 flex items-center justify-between">
              <span className="font-mono text-xs text-text-secondary">
                {provider}
              </span>
              <div className="flex items-center gap-3">
                <span className="font-mono text-xs tabular-nums text-text-bright">
                  ${amount.toFixed(2)}
                </span>
                <span className="font-mono text-xs tabular-nums text-text-muted" style={{ minWidth: '3.5rem', textAlign: 'right' }}>
                  {pct.toFixed(1)}%
                </span>
              </div>
            </div>
            <div className="h-1.5 w-full bg-bg-elevated">
              <div
                className="h-full transition-all duration-300"
                style={{
                  width: `${pct}%`,
                  backgroundColor: color,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
